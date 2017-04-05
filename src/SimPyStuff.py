import simpy
from simpy.core import BoundClass
from Interfaces import *
import src.Network
from Protocols import *
from RSegments.Message import Message
from RSegments.IP import IPHeader, IPDatagram
from RSegments.Ethernet import *
import Node

class DropStoreGet(simpy.resources.store.StoreGet):
    pass

class DropStorePut(simpy.resources.store.StorePut):
    pass

class TraceEvent(simpy.Event):
    def __str__(self):
        return str(type(self).__name__)

class PacketSent(TraceEvent):
    pass

class PacketArrived(TraceEvent):
    pass

class PacketDropped(TraceEvent):
    pass

class MessageReceived(TraceEvent):
    pass

class MessageEncapsulated(TraceEvent):
    pass

class SegmentEncapsulated(TraceEvent):
    pass

class SegmentDecapsulated(TraceEvent):
    pass

class DatagramEncapsulated(TraceEvent):
    pass

class DatagramDecapsulated(TraceEvent):
    pass

class FrameDecapsulated(TraceEvent):
    pass

class ConnectionSet(TraceEvent):
    pass

class PacketCreated(TraceEvent):
    pass

class DropStore(simpy.Store):
    def dropPut(self, item):
        if len(self.items) < self.capacity:
            self.put(item)
        else:
           PacketDropped(src.Network.env).succeed(value = str(item))
        # Otherwise, ignore the item.

    put = BoundClass(DropStorePut)

    get = BoundClass(DropStoreGet)

def AppInputProcess(env, app_input_store):
    while True:
        message = yield app_input_store.get()
        MessageReceived(env).succeed(value=str(message))
        yield env.timeout(1)


def AppOutputProcess(env, app_output_store, tran_output_store):
    while True:
        message = yield app_output_store.get()
        segment = protocols["Trans"][message.transport_protocol].getSegment(message)
        yield env.timeout(1)
        yield tran_output_store.put(segment)
        MessageEncapsulated(env).succeed(value=str(message))


def TranInputProcess(env, tran_input_store, app_input_store):
    while True:
        segment = yield tran_input_store.get()
        yield env.timeout(1)
        yield app_input_store.put(segment.message)
        SegmentDecapsulated(env).succeed(value=str(segment))



def TranOutputProcess(env, tran_output_store, net_output_store):
    while True:
        segment = yield tran_output_store.get()
        src_IP = segment.message.src_IP
        dest_IP = segment.message.dest_IP
        datagram = IPDatagram(IPHeader(src_IP,dest_IP), segment)
        yield env.timeout(1)
        SegmentEncapsulated(env).succeed(value=str(datagram))
        yield net_output_store.put(datagram)



def HostNetOutputProcess(net_output_store, host):
    # This process handles moving packets from a communal network layer output_store into the output store of the
    # specific network layer interface that will handle the transmission.  It only exists within a Host.
    # Note that encapsulation does not occur here, because a datagram is moving from one network level entity
    # to another.  Since this processing doesn't occur, I treat this step as instantaneous, and so there is no
    # timeout here.
    while True:
        datagram = yield net_output_store.get()
        dest_IP = datagram.get_dest_IP()
        next_interface = host.next_hop(dest_IP)["Interface"]
        yield next_interface.output_NL_queue.put(datagram)

def NetOutputProcess(env, NL_int):
    #assert isinstance(NL_int, NLInterface), "ERROR: NL_Process's NL_int argument is not an NLInterface instance"
    while True:
        datagram = yield NL_int.output_NL_queue.get()

        dest_IP = datagram.get_dest_IP()
        # Passing through a router means moving to a new subnet.
        # Thus, a new dest_MAC address is needed which is either in the ARP table, or else needs to be queried via
        #  ARP.  The src_MAC also must be updated to the MAC address of this interface.

        # The destination MAC address of the frame is that of the next hop router: may not be the final destination.
        # This is because IP addresses can only be resolved to MAC addresses on the same subnet (at or before the
        # next hop router).
        next_IP = NL_int.node.next_hop(dest_IP)["IP"]
        dest_dict = NL_int.ARP_table.get(next_IP, {})
        next_MAC = dest_dict.get("MAC", -1) if dest_dict != {} else -1

        if next_MAC != -1: # If ARP table has an entry for this dest_IP
            # remove this frame from the ARP list if it is there.
            try:
                NL_int.ARP_list.remove(datagram)
            except ValueError:
                # I don't care if it's not there.  Don't do anything.
                pass
            frame = EthernetFrame(EthernetHeader(NL_int.MAC_address, next_MAC), datagram)
            yield env.timeout(1)
            DatagramEncapsulated(env).succeed(value = str(frame))
            # If we know the MAC address associated with the destination IP, then put the frame in the LL output store
            print "NL_int IP", NL_int.IP_address, 'sending packet', str(frame)
            yield NL_int.output_LL_queue.put(frame)

        else: # if ARP table does not have an entry for this dest_IP
            if not (datagram in NL_int.ARP_list):
                # If we do not know where to send it, and aren't already waiting for an ARP reply, we must leave the
                # packet in the queue, and enact ARP.
                arp_frame = NL_int.make_ARP_frame(NL_int.IP_address, next_IP, NL_int.MAC_address)
                PacketCreated(env).succeed(value=str(arp_frame))
                print 'NL_int IP', str(NL_int.IP_address), 'sending ARP query'

                # queue an ARP frame to be sent by the link layer.
                yield env.timeout(1)
                yield NL_int.output_LL_queue.put(arp_frame)
                print 'NL_int IP', NL_int.IP_address, 'pushed ARP query to LL', arp_frame

                NL_int.ARP_list.append(datagram)
            else:
                #If this packet is already waiting on an ARP reply, don't send another one.
                print 'NL_int IP', NL_int.IP_address, 'waiting for ARP...'
            # TODO don't like this. Would maybe be better if I could avoid removing it from the store at all.
            # TODO That said, this is somewhat more efficient, as one packet waiting on ARP won't plug up the system.
            # Whether it's in the ARP list or not, the datagram is waiting on ARP, now, so it needs to go back in
            # the output queue.
            NL_int.output_NL_queue.put(datagram)
            # Have to wait at bit here, otherwise the get at the top succeeds immediately and nothing ever happens.
            yield src.Network.env.timeout(1)

def NetInputProcess(env, NL_int):
    in_store = NL_int.input_NL_queue
    router = NL_int.node

    while True:
        datagram = yield in_store.get()

        other_node = NL_int.connection.other_interface(NL_int).node.node_id
        this_node = NL_int.node.node_id
        info = "from node:%d to node:%d frame:%s" % (this_node, other_node, str(datagram))

        dest_IP = datagram.get_dest_IP()

        # If the datagram is destined for some other IP (for now, nothing talks directly to Routers, so delete if it
        # is for this Router.)
        if dest_IP != NL_int.IP_address:
            # forward the frame
            next_interface = router.next_hop(dest_IP)["Interface"]
            # If the other interface's output queue is full, wait until it isn't.
            print "NL_int IP", NL_int.IP_address, 'forwarding packet', datagram
            yield env.timeout(1)
            yield next_interface.output_NL_queue.put(datagram)
        else:
            if isinstance(NL_int.node, Node.Host):
                yield env.timeout(1)
                DatagramDecapsulated(env).succeed(value=str(datagram))
                yield NL_int.node.input_TL_queue.put(datagram.segment)

        # else: ignore the frame


def LinkInputProcess(env, interface):

    in_store = interface.input_LL_queue
    node = interface.node

    while True:
        frame = yield in_store.get()

        other_node = interface.connection.other_interface(interface).node.node_id
        this_node = interface.node.node_id
        info = "from node:%d to node:%d frame:%s" % (other_node, this_node, str(frame))

        PacketArrived(src.Network.env).succeed(value=info)

        # Behaviour of this process depends on if the node is a Switch or a Router

        if isinstance(node, Node.Router):
            # If the node is a Router, then the link layer has only to move the recieved frame up to the Network layer
            # and decapsulate it.
            # If it has my MAC, might need to process.
            if frame.get_dest_MAC() == interface.MAC_address or frame.get_dest_MAC() == 0:
                if interface.is_ARP_packet(frame):
                    # If it is ARP, then I can deal with it now.  No need to process.

                    # Construct an ARP reply
                    result = interface.process_ARP_packet(interface, frame)

                    # If we need to reply, put the reply frame directly into the interface's link layer output queue
                    if result is not None:
                        yield env.timeout(1)
                        PacketCreated(env).succeed(value=str(result))
                        yield interface.output_LL_queue.put(result)
                    # else: update ARP table (done in process_ARP_packet(...))
                else:  # If the packet is for me and not an ARP packet, I need to raise it to network level.
                    yield env.timeout(1)
                    FrameDecapsulated(env).succeed(value=str(frame))
                    yield interface.input_NL_queue.put(frame.ip_datagram)
        elif isinstance(node, Node.Switch):
            # If the node is a Switch, then the link layer must perform forwarding or broadcasting as appropriate.
            switch = node
            # Forward the frame, if I know where to send it

            # Add/refresh entry in switch table for src_MAC
            switch.switch_table[frame.get_src_MAC()] = {'Interface': interface.id, 'TTL': switch.DEFAULT_TTL}

            # Determine the next interface this frame would go on.
            next_interface = switch.next_interface(frame.get_dest_MAC())

            # If I know where this frame should go next:
            if next_interface != -1:
                if next_interface != interface.id:
                    print interface, 'forwarding frame', frame
                    yield env.timeout(1)
                    yield switch.interfaces[next_interface].output_LL_queue.put(frame)
                    # Will wait until it is possible to put the frame in the relevant output queue.
                # else: ignore the frame. They shouldn't be addressed to switches.
            else:
                # If I don't know where to send it, send it to everyone.
                yield env.timeout(1)
                for id, other_int in switch.interfaces.iteritems():
                    if id != interface.id:
                        # TODO where do switches drop packets during congestion?
                        print "LL_int MAC", interface.MAC_address, 'broadcasting frame', frame
                        yield other_int.output_LL_queue.put(copy.deepcopy(frame))
                        # Assume switches buffer output frames, but not input frames, because
                        # they can only receive one at a time.

def LinkOutputProcess(env, LL_int):
    out_store = LL_int.output_LL_queue

    while True:
        frame = yield out_store.get()
        print "LL_int MAC", LL_int.MAC_address, 'sending frame', frame
        # send the frame out onto the connection
        yield src.Network.env.process(PhysOutputProcess(env, frame, LL_int))

def PhysOutputProcess(env, frame, interface):
    # Write the frame bit string onto the connection

    # write to connection once per time step by setting the connection state
    for bit in frame.get_bit_string():
        # Trigger event to change connection state so it shows up in trace and GUI.
        connection = interface.connection
        connection.state = bit
        string = 'Conn:id:%s state:%s' % (connection.connection_id, connection.state)
        src.Network.network.connectionStates[interface.connection].succeed(string)
        # Reset the connection state event
        src.Network.network.connectionStates[interface.connection] = ConnectionSet(src.Network.env)
        yield src.Network.env.timeout(1)

    # trigger PacketSent event for trace
    other_interface = interface.connection.other_interface(interface)
    other_node = other_interface.node.node_id
    this_node = interface.node.node_id
    info = "from node:%d to node:%d frame:%s" % (this_node, other_node, str(frame))

    PacketSent(src.Network.env).succeed(value=info)

    # Let it carry on down the line.  I don't need to wait for it (spawn a new process to model propagation)
    env.process(PhysInputProcess(env, frame, interface))

def PhysInputProcess(env, frame, interface):
    # propagate frame across the connection to the other interface
    yield src.Network.env.timeout(interface.connection.get_latency())

    # Move the frame into the other interface's link layer input queue.
    # If the queue is full, the frame will be dropped.
    interface.connection.other_interface(interface).input_LL_queue.dropPut(frame)


def trace_cb(event):
    if not isinstance(event, (DropStoreGet, DropStorePut, simpy.Timeout, simpy.events.Initialize, simpy.Process)):
        env = event.env
        value = event.value
        string = '%d event: %s value: %s' % (env.now, event, value)

        # TODO remove this line
        print string + '\n'

        trace = src.Network.trace
        trace.write(string)
        trace.write('\n')