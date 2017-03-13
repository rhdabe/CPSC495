
from Packet import Packet
from Connection import Connection
from Node import Node, Host
from Interfaces import *

class Network:
    def __init__(self):
        # indexed by node_id
        self.nodes = {}

        #indexed by host IP address
        self.hosts = {}

        #indexed by a unique tuple of node_ids.  See get_node_pair_id
        self.connections = {}

        #indexed by packet_id
        self.packets = {}

    def add_node(self, node):
        """
        add a node to the network
        """
        self.nodes[node.node_id] = node

        print "Network add_node:  nodes:"
        print self.nodes

        if isinstance(node, Host):
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

    def get_connection(self, n1_id, n2_id):
        return self.connections[self.get_node_pair_id(n1_id,n2_id)]

    def add_packet(self, packet):
        self.packets[packet.packet_id] = packet

    def remove_node(self, node_id):
        """
        remove a node by id
        """
        try:
            del self.nodes[node_id]
            for c_id in self.connections.keys():
                if node_id in c_id:
                    del self.connections[c_id]
            for p_id, packet in self.packets.iteritems():
                if node_id == packet.current_node.node_id:
                    del self.packets[p_id]
            # for node in self.nodes.values():
            #     if not self.get_connected_nodes(node): self.remove_node(node.node_id)
            return True
        except:
            return False



    def remove_connection(self, n1_id, n2_id):
        """
        remove a connection by ids of nodes
        """
        try:
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
        #Need to include the actual node and connection objects.
        #This will allow me to replace node_id's by interface IP addresses in the table
        #quite easily.
        graph = {}
        for node in self.nodes.values():
            graph_node = {}
            for connection in self.get_connected_nodes(node.node_id):
                graph_node[self.nodes[connection["node"]]] = connection["connection"]
            graph[node] = graph_node
        return graph

def network_init():
    global network
    network = Network()
    Node.static_id=0
    Connection.static_id=0
    Packet.static_packet_id = 0
    LLInterface.static_MAC = 1
    NLInterface.static_IP = 1
