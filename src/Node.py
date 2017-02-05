from Segments.EthernetFrame import EthernetFrame
from Segments.IPDatagram import IPDatagram
from Segments.Segment import *
import Network
from LLInterface import LLInterface


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
        self.num_interfaces = 0

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



    def transmit_all_interfaces(self):
        for id, interface in self.interfaces.items():
            if interface.active and interface.transmitting:
                print "sending on interface", id, "with MAC", self.interfaces[id].MAC_address
                interface.send_bit()
                # else the interface is inactive. Do nothing.

    def read_all_interfaces(self):
        for id, interface in self.interfaces.items():
            if interface.active:
                if interface.received:
                    frame = interface.get_frame()
                    self.process_frame(frame, id)
                #TODO I don't think I need to do anything if an interface has finished transmitting. It should just clear its frame and set itself as free/inactive.
                if interface.receiving:
                    print "reading on interface", id, "with MAC", interface.MAC_address
                    interface.read()
                # else the interface is inactive. Do nothing.


    def new_interface(self):
        self.interfaces[self.num_interfaces] = LLInterface()
        self.num_interfaces += 1

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
                self.forward(frame, next_interface)
            # else: ignore the frame.
        else:
            # If I don't know where to send it, send it to everyone.
            self.broadcast(frame)

    def forward(self, frame, next_interface_id):
        print "forwarding frame from", frame.get_src_MAC(), "to", frame.get_dest_MAC(), "on interface", next_interface_id,\
            "with MAC", self.interfaces[next_interface_id].MAC_address
        if not self.interfaces[next_interface_id].active:
            #TODO not sure this is good enough.
            self.interfaces[next_interface_id].send(frame)

    def broadcast(self, frame):
        print "broadcasting frame from", frame.get_src_MAC(), "to", frame.get_dest_MAC()
        # TODO Don't know if this is good enough...
        for interface in self.interfaces.values():
            if not interface.active:
                interface.send(frame)


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
        return EthernetFrame(Header(self.static_id, destination_id, 0), message)

class Router(Switch):
    # TODO: all network entities should include a step() function which performs the necessary operations to move them
    # ahead one step in time.  Ex. Router needs to have the TTL fields in its ARP table decremented every step.
    # TODO this is flat IP.  Consider making it hierarchical.
    static_IP = 1


    def __init__(self):
        Switch.__init__(self)
        self.IP_address = Router.static_IP
        Router.static_IP += 1
        self.packet_queue = []

        #Routing table format: {final_dest_IP : next IP}
        self.routing_table = {}

        #ARP table format: ["IP" : {"MAC" : #, "TTL" : #} }
        self.ARP_table = {}



    def forward(self, packet):
        '''
        Look in routing table for which IP I should send this packet to next.
        If I know the MAC address for that IP, just DOOIT!
        If I do not, then broadcast ARP packet to get that MAC and add it to ARP table.
        '''

        dest_IP = packet.getDestIP()

        if self.routing_table.get(dest_IP, False):
            if self.IP_address != dest_IP:
                next_IP = self.next_hop(dest_IP)
                packet.set_connection(
                    Network.network.connections[Network.network.get_node_pair_id(
                        self.current_node.node_id, next_IP)])
            else:
                pass
                # TODO What do I do if this packet is for me?
                # TODO self.received(packet)
        else:
            pass
            #TODO do the ARP thing!

    def next_hop(self, dest_IP):
        #Returns IP next IP address according to this router's routing table.
        return self.routing_table[dest_IP]

    def ARP(self, IP_address):
        '''
        Broadcast ARP packet to get MAC address for the given IP address and add it to ARP table.
        '''
        pass

    def get_ip_header(self, message):
        return message.ip_header

    def get_ip_segment(self, message):
        return message.segment

    def wrap_new_IP_datagram(self, message, source_id, destination_id):
        #TODO the length of the header shouldn't be zero?
        return IPDatagram(Header(source_id, destination_id, 0),message)

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

    def __init__(self):
        Router.__init__(self)

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

    def send_message(self, dest_id, message_string):
        Network.network.create_messageTCP(self.static_id, dest_id, message_string)


