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

    static_MAC = 1

    def __init__(self):
        Node.__init__(self)
        self.MAC_address = Switch.static_MAC
        Switch.static_MAC += 1

    def get_ethernet_header(self, message):
        return message.frame_header

    def get_ethernet_datagram(self, message):
        return message.ip_datagram

    def wrap_new_ethernet_frame(self, message, destination_id):
        #TODO the length of the header shouldn't be zero?
        return EthernetFrame(Header(self.static_id, destination_id, 0), message)

    def next_hop(self, dest_id):
        return Network.network.nodes[self.routing_table[dest_id]]

class Router(Switch):

    static_IP = 1

    def __init__(self):
        Switch.__init__(self)
        self.IP_address = Router.static_IP
        Router.static_IP += 1

    def get_ip_header(self, message):
        return message.ip_header

    def get_ip_segment(self, message):
        return message.segment


    def wrap_new_ip_frame(self, message, source_id, destination_id):
        #TODO the length of the header shouldn't be zero?
        return IPDatagram(Header(source_id, destination_id, 0),message)

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


