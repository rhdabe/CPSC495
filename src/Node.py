from RSegments.Ethernet import *
from RSegments.IP import *
import Network
import Interfaces
import random
from RSegments.Segment import *
from RSegments.Header import *
from Packet import Packet
from NQueue import NQueue
from SimPyStuff import *


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
        self.packets = {}
        self.node_id = Node.static_id
        Node.static_id += 1
    #
    # '''returns the packets whose current location is this node'''
    # def get_packets(self):
    #     network = Network.network
    #
    #     my_packets = []
    #     for packet in network.packets:
    #         if packet.current_node == self.node_id:
    #             my_packets.append(packet)
    #     return my_packets


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
        newInterface = Interfaces.LLInterface(self)
        self.interfaces[newInterface.id] = newInterface
        self.local_interface_id += 1
        return newInterface

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
        newInterface = Interfaces.NLInterface(self)
        self.interfaces[newInterface.id] = newInterface
        self.local_interface_id += 1
        return newInterface

    def next_hop(self, dest_IP):
        # Returns routing table entry for dest_IP.  Format {"Interface": outgoing NLInterface, "IP": receiving IP}
        return self.routing_table[dest_IP]

    def get_pretty_routing_table(self):
        string = "Routing Table\n{Destination IP Address : Next IP Address}\n"
        for dest_IP, next_dict in self.routing_table.iteritems():
            string += str(dest_IP) + " : " + str(next_dict["IP"]) + "\n"
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

        # Define queues for modeling interaction between protocol stack layers
        self.input_AL_queue = NQueue(1)
        self.output_AL_queue = NQueue(1)
        self.input_TL_queue = NQueue(1)
        self.output_TL_queue = NQueue(1)
        self.net_output_queue = NQueue(1)

        # Define SimPy processes to manage the queues
        self.input_AL_process = Network.env.process(AppInputProcess(Network.env, self.input_AL_queue))
        self.output_AL_process = Network.env.process(AppOutputProcess(Network.env,
                                                                     self.output_AL_queue, self.output_TL_queue))
        self.input_TL_process = Network.env.process(TranInputProcess(Network.env,
                                                                     self.input_TL_queue, self.input_AL_queue))
        self.output_TL_process = Network.env.process(TranOutputProcess(Network.env,
                                                                       self.output_TL_queue, self.net_output_queue))
        self.host_output_process = Network.env.process(HostNetOutputProcess(self.net_output_queue, self))

    def new_interface(self):
        # Restrict Hosts to have a single IP address for simplicity of message sending.
        if len(self.interfaces) == 0:
            newInterface = Interfaces.NLInterface(self)
            self.interfaces[newInterface.id] = newInterface
        return self.interfaces.values()[0]

    # TODO assumes only one interface.  This may change.
    def get_IP_address(self):
        return self.interfaces.values()[0].IP_address

    def send_message(self, msg, startIP, endIP, app_protocol = "Default", trans_protocol = "UDP"):

         message = Message(msg, startIP, endIP,app_protocol, trans_protocol)

         self.output_AL_queue.put(message)

