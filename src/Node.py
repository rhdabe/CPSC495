from Segments.EthernetFrame import EthernetFrame
from Segments.IPDatagram import IPDatagram
from Segments.Segment import *
import Network


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
I will take raising or lowering a packet one level on the protocol stack to take one step, as well.


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

    def __init__(self):
        Node.__init__(self)

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

        #Routing table format: {final destination, next hop}
        self.routing_table = {}


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

        pass

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
        # TODO implement this.  ARP table TTL's must be decremented.
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


