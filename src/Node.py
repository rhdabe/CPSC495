from RSegments.Ethernet import *
from RSegments.IP import *
import Network
from Interfaces import LLInterface, NLInterface
import random
from RSegments.Segment import *
from RSegments.Header import *


'''
It is not Switches that have link-layer addresses, but their interfaces.  Thus, a single switch would properly
have a different address for each interface, and so a switch should have a dictionary of interfaces, indexed by address
(just an integer, an interface id, for example).  The link layer interface could be its own object, and could do the
translation from link layer frames to physical bits and send them out on the connection.

Routers have an ARP module, which holds an ARP table for translation between link layer (MAC) and network layer (IP)
addresses within a given subnet. IP Address    MAC Address   TTL (when entry will be deleted, typically 20min)

However, this table is initially empty.  It is populated via the exchange of ARP packets containing (at least):
(Example query packet)
Src IP  Src MAC  Dst IP  Dst MAC
1       1        2       0 (Broadcast)

Routers use these to ask all link layer interfaces in the subnet for a MAC address not known in the router's ARP table.
Obviously, the only valid choice of MAC address to send the ARP packets to is the broadcast address (i.e. address to
everyone).  Interfaces recieving these broadcasted ARP packets pass them up to their ARP modules.  If their IP is the
Dst IP, they reply by filling the Dst MAC field, and returning the ARP packet to sender.

Sending an ARP packet is the first step in sending a network datagram to an IP address whose MAC address is not known.

General notes:

I'm going to change what happens during a simulation step as follows.

Connections will each have a variable which represents the binary state of the connection (on/off, 1/0).
In a step, the sending interface will set the shared bit, and the recieving interface(s?) will read it.

Most steps will involve this sort of work.  Occaisionally, a router or switch will have some higher level things to do.
I will take raising or lowering a packet one level on the protocol stack to take one step, as well... maybe

In routers, packets elevated to the network layer by this Switch (inheritance) to this Router (elevate method?) will
be added to the router's packet queue.  This could be done by having an elevate flag in the Switch for each of its
interfaces.  If the flag is set, then the packet goes up to the network layer in this Router.  The Router step will
check for elevate flags and if found move the associated packets to the queue all at once.

Forwarding will also take place.  To preserve sanity, forwarder will occur BEFORE elevation within Router.step().
Otherwise, a packet could be elevated and forwarded in a single step.




'''

class Node(object):
    static_id = 0

    def __init__(self):

        self.node_id = Node.static_id
        Node.static_id += 1

    '''returns the packets whose current location is this node'''
    def get_packets(self):
        network = Network.network

        my_packets = []
        for packet in network.packets:
            if packet.current_node == self.node_id:
                my_packets.append(packet)
        return my_packets

class Switch(Node):
    DEFAULT_TTL = 100

    def __init__(self):
        Node.__init__(self)

        # Switch table format: [dest_MAC : {"Interface" : id#, "TTL" : #} }
        self.switch_table = {}

        # Interfaces format: {interface_id: LLInterface instance}
        self.interfaces = {}

        # Used to uniquely index the interfaces in the interfaces table.
        self.local_interface_id = 0

    def new_interface(self):
        newInterface = LLInterface(self)
        self.interfaces[self.local_interface_id] = newInterface
        self.local_interface_id += 1
        return newInterface

    def send(self):
        self.switch_send()

    def receive(self):
        self.switch_receive()

    def switch_send(self):
        self.transmit_LL_interfaces()

    def switch_receive(self):
        self.read_LL_interfaces()

    def transmit_LL_interfaces(self):
        for id, interface in self.interfaces.items():
            if interface.is_transmitting():
                print "sending on interface", id, "with MAC", self.interfaces[id].MAC_address
                interface.transmit()

    def read_LL_interfaces(self):
        for id, interface in self.interfaces.items():
                if interface.has_received():
                    frame = interface.get_frame()
                    self.process_frame(frame, id)
                if interface.is_receiving():
                    print "reading on interface", id, "with MAC", interface.MAC_address
                    interface.read()
                # else the interface is inactive. Do nothing.

    def process_frame(self, frame, incoming_interface_id):
        print "Switch processing frame from", frame.get_src_MAC(), "to", frame.get_dest_MAC(), "inbound on interface", incoming_interface_id,\
            "with MAC", self.interfaces[incoming_interface_id].MAC_address

        # Add/refresh entry in switch table for src_MAC
        self.switch_table[frame.get_src_MAC()] = {'Interface' : incoming_interface_id, 'TTL' : Switch.DEFAULT_TTL}
        print "Added/Refreshed switch table entry:"
        print "MAC", frame.get_src_MAC(), ":", self.switch_table[frame.get_src_MAC()]
        # Determine the next interface this frame would go on.
        next_interface = self.next_interface(frame.get_dest_MAC())

        # If I know where this frame should go next:
        if next_interface != -1:
            print"next_interface", next_interface, "incoming_interface", incoming_interface_id
            if next_interface != incoming_interface_id:
                self.forward_LL_frame(frame, next_interface)
            # else: ignore the frame.
        else:
            # If I don't know where to send it, send it to everyone.
            self.broadcast(frame, incoming_interface_id)

    def forward_LL_frame(self, frame, next_interface_id):
        print "forwarding frame from", frame.get_src_MAC(), "to", frame.get_dest_MAC(), "on interface", next_interface_id,\
            "with MAC", self.interfaces[next_interface_id].MAC_address
        self.interfaces[next_interface_id].output_LL_queue.enqueue(frame)

    def broadcast(self, frame, incoming_id):
        print "broadcasting frame from", frame.get_src_MAC(), "to", frame.get_dest_MAC()
        for id,interface in self.interfaces.iteritems():
            if not id == incoming_id:
                interface.output_LL_queue.enqueue(frame)

    def next_interface(self, dest_MAC):
        # If the switch table contains the next interface for dest_MAC, return its id, else return 0,
        # in which case the frame will then be broadcast on all interfaces.
        next_id = self.switch_table.get(dest_MAC, -1)
        print "next_interface for dest_MAC ", dest_MAC, "is", next_id

        next_id = next_id["Interface"] if next_id != -1 else -1

        return next_id

    def get_pretty_switch_table(self):

        string = "{Destination MAC : Outgoing Interface ID [Interface MAC address] : TTL}\n"
        table = self.switch_table
        for MAC in self.switch_table:
            int_id = table[MAC]["Interface"]

            string += str(MAC) + ":" + str(int_id) + "[" + str(self.interfaces[int_id].MAC_address) + \
                      "] :" + str(table[MAC]["TTL"]) + "\n"
        return string

class Router(Switch):
    # TODO: all network entities should include a step() function which performs the necessary operations to move them
    # TODO: ahead one step in time.  Ex. Router needs to have the TTL fields in its ARP table decremented every step.

    def __init__(self):
        Switch.__init__(self)

        # Routing table format: {final_dest_IP : {"Interface" : outgoing NLInterface, "IP" : int(receiving IP address)}
        self.routing_table = {}

        # ARP table format: {int(dest_IP) : {"MAC" : #, "TTL" : #} }
        self.ARP_table = {}

    def new_interface(self):
        newInterface = NLInterface(self)
        self.interfaces[self.local_interface_id] = newInterface
        self.local_interface_id += 1
        return newInterface

    '''This is overridden to remove MAC_based packet switching (self.process_frame() bit is commented out)
        and switch table stuff.'''
    def read_LL_interfaces(self):
        for id, interface in self.interfaces.items():
                # if interface.has_received():
                #    frame = interface.get_frame()
                #    self.process_frame(frame, id)
                if interface.is_receiving():
                    print "reading on interface", id, "with MAC", interface.MAC_address
                    interface.read()

    def send(self):
        self.router_send()

    def receive(self):
        self.router_receive()

    def router_send(self):
        self.switch_send()
        self.process_output_queues()

    def router_receive(self):
        self.switch_receive()
        self.process_input_queues()

    def process_output_queues(self):
        # Check all output queues for pending IPDatagram transmissions
        for interface in self.interfaces.values():
            interface.process_output_queue()

    def process_input_queues(self):
        # Check all input queues for delivered datagrams.
        for interface_id, interface in self.interfaces.iteritems():
            if interface.process_input_queue():
                self.process_datagram(interface_id)

    def process_datagram(self, incoming_interface_id):
        print "Router processing datagram on interface " + str(incoming_interface_id)


        interface = self.interfaces[incoming_interface_id]
        queue = interface.input_NL_queue
        frame = queue.peek_head()
        dest_IP = queue.peek_head().IP_datagram.get_dest_IP()

        # If the datagram is destined for some other IP (for now, nothing talks directly to Routers, so delete if it
        # is for this Router.)
        if dest_IP != interface.IP_address:
            self.forward_IP_datagram(incoming_interface_id)
        else:
            queue.dequeue

    def forward_IP_datagram(self, incoming_interface_id):

        queue = self.interface[incoming_interface_id].output_NL_queue
        dest_IP = queue.peek_head().IP_datagram.get_dest_IP()

        next_interface = self.next_hop(dest_IP)
        next_interface.output_NL_queue.enqueue(queue.dequeue())

    def next_hop(self, dest_IP):
        # Returns routing table entry for dest_IP.  Format {"Interface": outgoing NLInterface, "IP": receiving IP}
        return self.routing_table[dest_IP]

    def get_pretty_routing_table(self):

        string = "Routing Table\n{Destination IP Address : Next IP Address}\n"
        for dest_IP, next_interface in self.routing_table.iteritems():
            string += str(dest_IP) + " : " + str(next_interface.IP_address) + "\n"

        return string

    def get_pretty_arp_table(self):
        string = "ARP Table:\n{Dest. IP Address : {Dest. MAC Address : TTL} }\n"
        for dest_IP, dest_MAC in self.ARP_table.iteritems():
            string += str(dest_IP) + " : " + str(dest_MAC) + "\n"

        return string

class Host(Router):

    def __init__(self):
        Router.__init__(self)
        self.new_interface()
        self.messages = []

    def read_LL_interfaces(self):
        for id, interface in self.interfaces.items():
                # if interface.has_received():
                #     frame = interface.get_frame()
                #     self.process_frame(frame, id)
                if interface.is_receiving():
                    print "reading on interface", id, "with MAC", interface.MAC_address
                    interface.read()

    def process_datagram(self, incoming_interface_id):
        print "Host with IP", self.interfaces[0].IP_address, "processing datagram on interface " + str(incoming_interface_id)
        # I'm working with an interface queue here because later I may change to finite queues, in which case, the
        # output queue might be full and so dequeuing the packet way back at the begining of processing would be
        # the wrong thing to do.  That decision should be made in the forward_IP_datagram method.

        interface = self.interfaces[incoming_interface_id]
        queue = interface.input_NL_queue
        frame = queue.peek_head()
        datagram = frame.IP_datagram
        dest_IP = frame.IP_datagram.get_dest_IP()

        # If the datagram is destined for some other IP
        if dest_IP != interface.IP_address:
            if not (interface.is_ARP_packet(frame)):
                self.forward_IP_datagram(queue)
            else:
                queue.dequeue()
        else:
            if interface.is_ARP_packet(frame):
                interface.process_ARP_packet()
            else:
                payload = frame.IP_datagram.payload
                assert isinstance(payload,UDPSegment) or isinstance(payload, TCPSegment), \
                    "ERROR: datagram payload %s is not UDP or TCP instance" % str(payload)
                # Needed to add this to datagram processing in a Host node.
                self.messages.append(payload)
                queue.dequeue()

    def receive(self):
        self.router_receive()
        for message in self.messages:
            print "Message received:"
            print "\"" + str(message.header) + "\""
            print "\"" + message.message + "\""
        self.messages = []

    def get_protocol_header(self, message):
        return message.header

    def get_protocol_message(self, message):
        return message.message

    def wrap_new_protocol_header(self, header, message):
        if isinstance(header, TCPHeader):
            return TCPSegment(header, message)
        elif isinstance(header, UDPHeader):
            return UDPSegment(header, message)
        else:
            return Segment(header, message)

    def new_interface(self):
        # Restrict Hosts to have a single IP address for simplicity of message sending.
        if len(self.interfaces) == 0:
            self.interfaces[0] = NLInterface(self)

        return self.interfaces[0]

    def get_IP_address(self):
        return self.interfaces[0].IP_address

    '''
    Create a UDP/TCP segment, then encapsulate it in an IPDatagram and let the Router code process it.
    '''
    def send_message(self, dest_IP, message_string, UDP):
        # Randomly select a port number just to show that replies come back to the same port.
        port = random.randrange(0, 10000)

        # Select transport protocol based on use input in SendMessageWindow
        if(UDP):
            self.create_messageUDP(self.get_IP_address, dest_IP, port, message_string)
        else:
            self.create_messageTCP(self.get_IP_address, dest_IP, port, message_string)

    '''
    Create a new UDP message
    '''
    def create_messageUDP(self, startIP, endIP, port, messageString):

        segment = UDPSegment(UDPHeader(port, port, 0), messageString)
        self.create_message(startIP, endIP, segment)

    '''
    create a new TCP message
    '''
    def create_messageTCP(self, startIP, endIP, port, messageString):
        segment = TCPSegment(TCPHeader(port, port, 0), messageString)
        self.create_message(startIP, endIP, segment)

    '''encapsulate message in IP datagram and EthernetFrame then place in NL_Interface input queue to be routed'''
    def create_message(self, startIP, endIP, UDP_TCP_segment):
        interface = self.interfaces[0]
        ip_datagram = IPDatagram(IPHeader(startIP, endIP), UDP_TCP_segment)
        # The 0 destination MAC address doesn't matter.  The correct MAC will be determined in the NL_Interface.
        frame = EthernetFrame(EthernetHeader(interface.MAC_address, 0), ip_datagram)

        self.interfaces[0].output_NL_queue.enqueue(frame);

        # TODO it would be useful to keep the list of packets for tracking purposes, but it doesn't work this way.
        #self.add_packet(Packet(self.nodes[startID], eth_frame))
