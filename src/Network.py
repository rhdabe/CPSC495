
from Packet import Packet
from Connection import Connection
from Interfaces import *
import Node
import simpy
import os
import SimPyStuff

class Network:
    def __init__(self):
        # indexed by node_id
        self.nodes = {}

        # indexed by host IP address
        self.hosts = {}

        # indexed by a unique tuple of node_ids.  See get_node_pair_id
        self.connections = {}

        # indexed by a Connection instance.  Values are simpy Events which return the connection state when triggered.
        self.connectionStates = {}

        # indexed by packet_id
        self.packets = {}

        # for use in MacroGUI
        self.traced = False



    def add_node(self, node):
        """
        add a node to the network
        """
        self.nodes[node.node_id] = node

        if isinstance(node, Node.Host):
            self.hosts[node.get_IP_address()] = node

    def get_node_pair_id(self, n1_id, n2_id):
        return (n1_id, n2_id) if n1_id <= n2_id else (n2_id, n1_id)

    # def create_messageUDP(self, startIP, endIP, messageString):
    #     startID = self.hosts[startIP].node_id
    #     endID = self.hosts[startIP].node_id
    #     # TODO The IDS are not important for message creation.  Should use port numbers.  Fix this.
    #     segment = UDPSegment(UDPHeader(startID, endID, 0), messageString)
    #     self.create_message(startID, endID, segment)
    #
    # def create_messageTCP(self, startIP, endIP, messageString):
    #     startID = self.hosts[startIP].node_id
    #     endID = self.hosts[startIP].node_id
    #     # TODO The IDS are not important for message creation.  Should use port numbers.  Fix this.
    #     segment = TCPSegment(TCPHeader(startID, endID), messageString)
    #     self.create_message(startID, endID, segment)
    #
    # def create_message(self, startIP, endIP, UDP_TCP_segment):
    #     startID = self.hosts[startIP].node_id
    #     # TODO The IDS are not important for message creation.  Should use port numbers.  Fix this.
    #     ip_datagram = IPDatagram(IPHeader(startIP,endIP), UDP_TCP_segment)
    #     eth_frame = EthernetFrame(EthernetHeader(startIP, endIP), ip_datagram)
    #     self.add_packet(Packet(self.nodes[startID], eth_frame))


    def add_connection(self, n1_id, n2_id, connection):
        """
        add a connection between two nodes (by id)
        """
        pair_id = self.get_node_pair_id(n1_id, n2_id)
        self.connections[pair_id] = connection
        self.connectionStates[connection] = SimPyStuff.ConnectionSet(env)

    def get_connection(self, n1_id, n2_id):
        return self.connections[self.get_node_pair_id(n1_id,n2_id)]

    def add_packet(self, packet):
        self.packets[packet.packet_id] = packet

    def remove_node(self, node_id):
        """
        remove a node by id
        """

        try:
            node = self.nodes[node_id]
            del self.nodes[node_id]
            for c_id in self.connections.keys():
                if node_id in c_id:
                    self.remove_connection(c_id[0], c_id[1])
            for p_id, packet in self.packets.iteritems():
                if node_id == packet.current_node.node_id:
                    del self.packets[p_id]

            if isinstance(node, Node.Host):
                del self.hosts[node.interfaces[0].IP_address]

            return True
        except:
            return False

    def remove_connection(self, n1_id, n2_id):
        """
        remove a connection by ids of nodes
        """
        try:
            del self.connectionStates[self.connections[self.get_node_pair_id(n1_id, n2_id)]]
            del self.connections[self.get_node_pair_id(n1_id, n2_id)]
            return True
        except:
            return False

    def get_connected_nodes(self, node_id):
        """
        returns a list of nodes connected to the given node in the form
        [{"node": the node at the other end, "connection": the connection object}]
        """
        connected = []
        for c_id, connection in self.connections.iteritems():
            if node_id in c_id:
                other_node = c_id[0] if c_id[1] == node_id else c_id[1]
                connected.append({"node":other_node, "connection":connection})
        return connected

    def get_as_graph(self):
        graph = {}
        for node in self.nodes:
            graph_node = {}
            for connection in self.get_connected_nodes(node):
                graph_node[connection["node"]] = connection["connection"].get_latency()
            graph[node] = graph_node
        return graph

    def get_better_graph(self):
        # Need to include the actual node and connection objects.
        # This will allow me to replace node_id's by interface IP addresses in the table
        #quite easily.

        graph = {}
        for node in self.nodes.values():
            graph_node = {}
            for connected in self.get_connected_nodes(node.node_id):
                graph_node[self.nodes[connected["node"]]] = connected["connection"]
            graph[node] = graph_node

        # Also, Switches need to be removed for this to work properly.

        done_list = []
        graph_copy = graph.copy()
        for node in graph_copy:
            done_list = []
            if not isinstance(node, Node.Router):
                for adj_node_1, adj_conn_1 in graph_copy[node].iteritems():
                    adj_ints = adj_conn_1.interfaces
                    far_int_1 = adj_ints[0] if adj_ints[1] in node.interfaces.values() else adj_ints[1]
                    for adj_node_2, adj_conn_2 in graph_copy[node].iteritems():
                        if adj_node_2 != adj_node_1 and adj_node_2 not in done_list:
                            oth_adj_ints = adj_conn_2.interfaces
                            far_int_2 = oth_adj_ints[0] if oth_adj_ints[1] in node.interfaces.values() else oth_adj_ints[1]

                            new_conn = Connection(None, adj_conn_1.get_latency() + adj_conn_2.get_latency())
                            new_conn.fake_connect_interfaces(far_int_1, far_int_2)

                            graph[adj_node_1][adj_node_2] = new_conn
                            graph[adj_node_2][adj_node_1] = new_conn

                    dict = graph[adj_node_1]
                    del dict[node]
                    done_list.append(adj_node_1)
                del graph[node]
        return graph

trace = None
env = None
network = None

def trace_init():
    global trace
    if trace is not None:
        trace.close()
        os.remove('trace')

    trace = open('trace', mode='w', buffering=0)

def network_init():

    global network
    network = Network()
    global env
    env = simpy.Environment(trace_cb=SimPyStuff.trace_cb)
    trace_init()

    Node.Node.static_id = 0

    Connection.static_id = 0
    Packet.static_packet_id = 0
    LLInterface.static_MAC = 1
    LLInterface.static_ID = 0
    NLInterface.static_IP = 1
