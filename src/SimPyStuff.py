import simpy
from Interfaces import *
import src.Network


class DropStore(simpy.Store):

    def dropPut(self, item):
        if len(self.items) < self.capacity:
            self.put(item)
        # Otherwise, ignore the item.

def LL_Input_Port(env, LL_int):
   # assert isinstance(LL_int, LLInterface()) and not isinstance(LL_int, NLInterface),\
    #    "ERROR: LL_Process's LL_int argument is not an LLInterface instance"

    in_store = LL_int.input_LL_queue
    switch = LL_int.node

    while True:
        frame = yield in_store.get()

        # Forward the frame, if I know where to send it

        # Add/refresh entry in switch table for src_MAC
        switch.switch_table[frame.get_src_MAC()] = {'Interface': LL_int.id, 'TTL': switch.DEFAULT_TTL}

        # Determine the next interface this frame would go on.
        next_interface = switch.next_interface(frame.get_dest_MAC())

        # If I know where this frame should go next:
        if next_interface != -1:
            if next_interface != LL_int.id:
                print LL_int, 'forwarding frame', frame
                yield switch.interfaces[next_interface].output_LL_queue.put(frame)
                # Will wait until it is possible to put the frame in the relevant output queue.
            # else: ignore the frame. They shouldn't be addressed to switches.
        else:
            # If I don't know where to send it, send it to everyone.
            for id, interface in switch.interfaces.iteritems():
                if not id == LL_int.id:
                    # TODO where do switches drop packets during congestion?
                    print "LL_int MAC", LL_int.MAC_address, 'broadcasting frame', frame
                    yield interface.output_LL_queue.put(frame)
                    # Assume switches buffer output frames, but not input frames, because
                    # they can only receive one at a time.

def LL_Output_Port(env, LL_int):
    # assert isinstance(LL_int, LLInterface()) and not isinstance(LL_int, NLInterface),\
    #    "ERROR: LL_Process's LL_int argument is not an LLInterface instance"

    out_store = LL_int.output_LL_queue

    while True:
        frame = yield out_store.get()
        print "LL_int MAC", LL_int.MAC_address, 'sending frame', frame
        yield env.timeout(LL_int.connection.get_latency())
        send_frame(frame, LL_int)
        print 'LL_int MAC', LL_int.MAC_address, 'finished sending', frame


def NL_Input_Port(env, NL_int):
   # assert isinstance(NL_int, NLInterface), "ERROR: NL_Process's NL_int argument is not an NLInterface instance"
    in_store = NL_int.input_NL_queue
    router = NL_int.node

    while True:
        frame = yield in_store.get()

        need_to_process = False

        # If it has my MAC, might need to process.
        if frame.get_dest_MAC() == NL_int.MAC_address or frame.get_dest_MAC() == 0:
            need_to_process = True;
            if NL_int.is_ARP_packet(frame):
                # If it is ARP, then I can deal with it now.  No need to process.
                need_to_process = False;

                frame = NL_int.process_ARP_packet(NL_int, frame)

                if(frame != None): yield NL_int.output_NL_queue.put(frame)
        # else: ignore the frame.

        if(need_to_process):
            dest_IP = frame.ip_datagram.get_dest_IP()

            # If the datagram is destined for some other IP (for now, nothing talks directly to Routers, so delete if it
            # is for this Router.)
            if dest_IP != NL_int.IP_address:
                # forward the frame
                next_interface = router.next_hop(dest_IP)["Interface"]
                # If the other interface's output queue is full, wait until it isn't.
                print "NL_int IP", NL_int.IP_address, 'forwarding packet', frame
                yield next_interface.output_NL_queue.put(frame)
            else:
                if isinstance(NL_int.node, src.Node.Host):
                    print "message received at", NL_int.IP_address, frame.ip_datagram.segment
            # else: ignore the frame

def NL_Output_Port(env, NL_int):
    #assert isinstance(NL_int, NLInterface), "ERROR: NL_Process's NL_int argument is not an NLInterface instance"

    out_store = NL_int.output_NL_queue

    while True:
        frame = yield out_store.get()

        dest_IP = frame.ip_datagram.get_dest_IP()
        # Passing through a router means moving to a new subnet.
        # Thus, a new dest_MAC address is needed which is either in the ARP table, or else needs to be queried via
        #  ARP.  The src_MAC also must be updated to the MAC address of this interface.

        # The destination MAC address of the frame is that of the next hop router: may not be the final destination.
        # This is because IP addresses can only be resolved to MAC addresses on the same subnet (at or before the
        # next hop router).
        next_IP = NL_int.node.next_hop(dest_IP)["IP"]
        dest_dict = NL_int.ARP_table.get(next_IP, {})
        next_MAC = dest_dict.get("MAC", -1) if dest_dict != {} else -1

        if next_MAC != -1:
            # remove this frame from the ARP list if it is there.
            try:
                NL_int.ARP_list.remove(frame)
            except ValueError:
                # I don't care if it's not there.  Don't do anything.
                pass

            # If we know the MAC address associated with the destination IP, then send,
            # updating both the dest_MAC and src_MAC fields of the EthernetFrame
            frame.set_src_MAC(NL_int.MAC_address)
            frame.set_dest_MAC(next_MAC)

            print "NL_int IP", NL_int.IP_address, 'sending packet', frame
            yield env.timeout(NL_int.connection.get_latency())
            send_frame(frame, NL_int)
            print 'NL_int IP', NL_int.IP_address, 'finished sending', frame

        else:
            if not (frame in NL_int.ARP_list):
                # If we do not know where to send it, and aren't already waiting for an ARP reply, we must leave the
                # packet in the queue, and enact ARP.
                print "IP", NL_int.IP_address, "sending ARP query"
                arp_frame = NL_int.make_ARP_frame(NL_int.IP_address, dest_IP, NL_int.MAC_address)

                #TODO this may no longer be necessary
                NL_int.node.add_packet(NL_int, arp_frame)

                print 'NL_int IP', NL_int.IP_address, 'sending ARP query', arp_frame

                yield env.timeout(NL_int.connection.get_latency())
                send_frame(arp_frame, NL_int)
                print 'NL_int IP', NL_int.IP_address, 'finisehd sending ARP query', arp_frame

                NL_int.ARP_list.append(frame)

            else:
                #If this packet is already waiting on an ARP reply, don't send another one.
                print 'NL_int IP', NL_int.IP_address, 'waiting for ARP...'
            #TODO don't like this.
            out_store.put(frame)
            yield src.Network.env.timeout(1)

def send_frame(frame, interface):
    # It is possible that the connection has been deleted mid transmission,
    # In which case, the connection and connectionStates event no longer exist.
    # If this happens, then just move on.

    #TODO nothing happens if this is uncommented.  Literally nothing.  Debugger won't touch it. I don't get it.
    # try:
    #     for bit in frame.get_bit_string():
    #         print "setting connection state to", bit
    #         # Trigger event to change connection state so it shows up in trace and GUI.
    #         src.Network.network.connectionStates[interface.connection].succeed(bit)
    #         # Reset the connection state event
    #         src.Network.network.connectionStates[interface.connection] = simpy.events.Event()
    #         yield simpy.Timeout(1)
    # except KeyError:
    #     pass
   # Move the frame into the other interface's input queue.  If the queue is full, the frame will be dropped.

    other_interface = interface.connection.other_interface(interface)

    if isinstance(other_interface, src.Interfaces.NLInterface):
        interface.connection.other_interface(interface).input_NL_queue.dropPut(frame)
    else: interface.connection.other_interface(interface).input_LL_queue.dropPut(frame)

