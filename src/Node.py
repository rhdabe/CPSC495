from RSegments.EthernetFrame import *
from RSegments.IPDatagram import *
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
    #ID's will be used as addresses of one type or another
    static_id = 1

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

        # TODO This will not work.  Must transmit from all switches first, and then read from all switches.  Two passes.
        '''
             Switch processing should occur in this order:

             This Switch processes all frames on interfaces with a set received flag.
                 Filter frames, or forward them on to their next interface.
             This Switch transmits on all interfaces with outgoing packets.
                 (In LLInterface: If a transmission is completed, free up this interface.)
             This Switch reads on all interfaces with incoming packets.
                 (In LLInterface: One more bit is read on each interface from their connection
                 If a packet read is completed, set self.frame = the complete frame, and set received flag)

        '''

    def get_pretty_switch_table(self):

        string = "{Desination MAC : Outgoing Interface ID [Interface MAC address]}\n"

        for MAC, int_id in self.interfaces.iteritems():
            string += str(MAC) + ":" + str(int_id) +  "[" + str(self.interfaces[int_id].MAC_address) + "]\n"

        return string

    def new_interface(self):
        newInterface = LLInterface(self)
        self.interfaces[self.local_interface_id] = newInterface
        self.local_interface_id += 1
        return newInterface

    def send(self):
        self.transmit_LL_interfaces()

    def receive(self):
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
        print "processing frame from", frame.get_src_MAC(), "to", frame.get_dest_MAC(), "inbound on interface", incoming_interface_id,\
            "with MAC", self.interfaces[incoming_interface_id].MAC_address

        # Add/refresh entry in switch table for src_MAC
        self.switch_table[frame.get_src_MAC()] = {'Interface' : incoming_interface_id, 'TTL' : Switch.DEFAULT_TTL}

        # Determine the next interface this frame would go on.
        next_interface = self.next_interface(frame.get_dest_MAC())

        # If I know where this frame should go next:
        if isinstance(next_interface, (int, long)):
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
        self.interfaces[next_interface_id].send_frame(frame)

    def broadcast(self, frame, incoming_id):
        print "broadcasting frame from", frame.get_src_MAC(), "to", frame.get_dest_MAC()
        # TODO Don't know if this is good enough...
        for id,interface in self.interfaces.iteritems():
            if not id == incoming_id:
                interface.send_frame(frame)

    def next_interface(self, dest_MAC):
        # If the switch table contains the next interface for dest_MAC, return its id, else return False.
        next_id = self.switch_table.get(dest_MAC, False)
        print "next_interface for", dest_MAC, "is", next_id

        if next_id:
            return next_id["Interface"]
        else:
            return False

    def get_ethernet_header(self, message):
        return message.frame_header

    def get_ethernet_datagram(self, message):
        return message.ip_datagram

    def wrap_new_ethernet_frame(self, message, destination_id):
        #TODO the length of the header shouldn't be zero?
        return EthernetFrame(EthernetHeader(self.static_id, destination_id, 0), message)

class Router(Switch):
    # TODO: all network entities should include a step() function which performs the necessary operations to move them
    # TODO: ahead one step in time.  Ex. Router needs to have the TTL fields in its ARP table decremented every step.

    ARP_MAC = 0
    ARP_payload = 'ARP'

    def __init__(self):
        Switch.__init__(self)

        # Routing table format: {final_dest_IP : next IP}
        self.routing_table = {}

        # ARP table format: ["IP" : {"MAC" : #, "TTL" : #} }
        self.ARP_table = {}

        # List of packets waiting on ARP replies.  Used to prevent this router from ARP spamming.
        self.ARP_list = []


    def new_interface(self):

        # Each link layer interface in this Router has an associated input queue, and output queue.
        newInterface = NLInterface(self)
        self.interfaces[self.local_interface_id] = newInterface
        self.local_interface_id += 1
        return newInterface

    def send(self):
        self.process_output_queues()

    def receive(self):
        self.process_input_queues()

    def process_output_queues(self):
        # Check all output queues for pending IPDatagram transmissions
        for interface in self.interfaces:
            if not interface.output_NL_queue.isEmpty():
                datagram = interface.output_NL_queue.peek_last()
                dest_IP = datagram.get_dest_IP()
                dest_MAC = self.ARP_table.get(dest_IP, False)
                if isinstance(dest_MAC, (int,long)):
                    # If we know the MAC address associated with the destination IP, then encapsulate and send.
                    interface.output_LL_queue.enqueue(EthernetFrame(EthernetHeader(), interface.output_NL_queue.dequeue()))
                else:
                    # If we do not know, we must leave the IPDatagarm in the queue, and enact ARP.
                    arp_frame = self.make_ARP_frame(interface.IP_address, dest_IP, interface.MAC_address)
                    interface.send_frame(arp_frame)
                    self.ARP_list.append(datagram)

    def process_input_queues(self):
        # Check all input queues for delivered datagrams.
        for interface_id, interface in self.interfaces.iteritems():
            if not interface.input_NL_queue.isEmpty():
                self.process_datagram(interface.input_NL_queue, interface_id)

    def process_datagram(self, queue, incoming_interface_id):
        # I'm working with an interface queue here because later I may change to finite queues, in which case, the
        # output queue might be full and so dequeuing the packet way back at the begining of processing would be
        # the wrong thing to do.  That decision should be made in the forward_IP_datagram method.

        datagram = queue.peek_last()
        # Packets could be intended for this router, and not a host, in a real network (control stuff)
        # If the datagram is destined for some other IP
        if not datagram.get_dest_IP() == self.IP_address:
            self.forward_IP_datagram(queue)
        else:
            if self.is_ARP_packet(datagram):
                self.process_ARP_packet(queue)

    def forward_IP_datagram(self, queue):
        # I'm working with an interface queue here because later I may change to finite queues, in which case, the
        # output queue might be full and so dequeuing the packet way back at the begining of processing would be
        # the wrong thing to do.  The decision should be made here as to whether forwarding actually happens.

        dest_IP = datagram.get_dest_IP()

        next_interface = self.next_hop(dest_IP)
        next_interface.output_NL_queue.enqueue(queue.dequeue())

    def make_ARP_frame(self, src_IP, dest_IP, src_MAC):
        ARP_datagram = IPDatagram(IPHeader(src_IP, self.dest_IP))
        ARP_frame = EthernetFrame(EthernetHeader(src_MAC, Router.ARP_MAC), Router.ARP_payload)
        return ARP_frame

    def is_ARP_packet(self, frame):
        datagram = frame.IP_datagram
        return isinstance(frame, EthernetFrame) and datagram.header.dest_IP == Router.ARP_IP \
            and datagram.payload == Router.ARP_payload

    def process_ARP_packet(self, datagram):
        datagram.dest_IP = datagram.get_src_IP()
        datagram.src_IP = self.IP_address

    def next_hop(self, dest_IP):
        # Returns next IP address according to this router's routing table.
        return self.routing_table[dest_IP]

    def get_pretty_routing_table(self):
        print "get pretty routing table", self.routing_table

        string = "{Destination IP Address : Next IP Address}"
        for dest_IP, next_interface in self.routing_table.iteritems():
            string += str(dest_IP) + " : " + str(next_interface.IP_address) + "\n"

        return string


#TODO decide whether to keep these or nuke them.
    # def get_ip_header(self, message):
    #     return message.ip_header
    #
    # def get_ip_segment(self, message):
    #     return message.segment
    #
    # def wrap_new_IP_datagram(self, message, source_id, destination_id):
    #     #TODO the length of the header shouldn't be zero?
    #     return IPDatagram(Header(source_id, destination_id, 0),message)

    def step(self):
        # TODO implement this.
        '''
        ARP table TTL's must be decremented, and expired entries removed.

        Packet processing must be advanced. (In this order!)

            This Switch processes all frames on interfaces with a set received flag.
                If the dest_IP is not self.IP_address,
            This Switch transmits on all interfaces with outgoing packets.
                (In LLInterface: If a transmission is completed, free up this interface.)
            This Switch reads on all interfaces with incoming packets.
                (In LLInterface: One more bit is read on each interface from their connection
                If a packet read is completed, set self.frame = the complete frame, and set received flag)

            Forward a packet in the queue.
                wrap it in a link layer frame and give it to this Switch.
            Elevate packets from this Switch (elevate())


        '''
        pass

class Host(Router):

    #TODO Randomly generate a port number.
    DEFAULT_PORT_NUMBER = 1

    def __init__(self):
        Router.__init__(self)
        self.new_interface()

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
        startID = self.hosts[startIP].node_id
        endID = self.hosts[startIP].node_id
        segment = TCPSegment(TCPHeader(port, port), messageString)
        self.create_message(startID, endID, segment)

    '''encapsulate message in IP datagram and place in NL_Interface input queue to be routed'''
    def create_message(self, startIP, endIP, UDP_TCP_segment):
        startID = self.hosts[startIP].node_id
        ip_datagram = IPDatagram(IPHeader(startIP, endIP), UDP_TCP_segment)
        self.interfaces[0].input_NL_queue.enqueue(ip_datagram);

        # TODO it would be useful to keep the list of packets for tracking purposes, but it doesn't work this way.
        #self.add_packet(Packet(self.nodes[startID], eth_frame))
