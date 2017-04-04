from NQueue import NQueue
from RSegments.IP import *
from RSegments.Ethernet import *
from Packet import Packet
import Network
import SimPyStuff

class LLInterface(object):
    # Note: apparently switches do not have MAC addresses for interfaces that connect to Hosts or Routers. Zero import.

    # MAC addresses start from 1.  0 is the broadcast address.
    static_MAC = 1
    static_ID = 0
    def __init__(self, node):
        self.id = LLInterface.static_ID
        LLInterface.static_ID += 1
        self.node = node
        self.input_LL_process = Network.env.process(SimPyStuff.LinkInputProcess(Network.env, self))
        self.input_LL_queue = NQueue()
        self.output_LL_process = Network.env.process(SimPyStuff.LinkOutputProcess(Network.env, self))
        self.output_LL_queue = NQueue()
        self.MAC_address = LLInterface.static_MAC
        LLInterface.static_MAC += 1
        self.connection = None  # points to current connection object
        self.frame = None  # points to current frame to be transmitted or that has been received.
        self.receiving = False  # currently receiving bit string to be parsed into self.frame
        self.received = False  # a frame has been received.
        self.transmitting = False  # currently transmitting self.frame
        self.bit_string = ''  # will hold bit string to be parsed if receiving, or to be transmitted if transmitting
        self.next_bit = 0  # index of next bit to be transmitted from self.bit_string

    def connect(self, connection):
        self.connection = connection

    def disconnect(self, connection):
        self.connection = None


class NLInterface (LLInterface):
    static_IP = 1

    ARP_MAC = 0
    ARP_payload = 'ARP'
    DEFAULT_ARP_TTL = 20

    def __init__(self, node):
        LLInterface.__init__(self, node)
        self.IP_address = NLInterface.static_IP
        NLInterface.static_IP += 1
        self.input_NL_queue = NQueue()
        self.output_NL_queue = NQueue()
        self.input_NL_process = Network.env.process(SimPyStuff.NetInputProcess(Network.env, self))
        self.output_NL_process = Network.env.process(SimPyStuff.NetOutputProcess(Network.env, self))
        self.ARP_table = node.ARP_table
        self.routing_table = node.routing_table

        # List of datagrams waiting on ARP replies.  Used to prevent this router from ARP spamming.
        self.ARP_list = []

    def is_ARP_packet(self, frame):
        return frame.ip_datagram.segment == NLInterface.ARP_payload


    def process_ARP_packet(self, NL_int, frame):
        '''This method is intended to be called by a SimPy Process.  It either returns the ARP packet to sender with this
        interface's MAC address as the src_MAC or else updates the ARP table stored in the Router to which this interface
        belongs.  Will yield if this NLInterface's output queue is full.

        :arg NL_int an NLInterface instance which has just recieved an ARP frame
        :arg frame an ARP frame to be processed
        '''

        print "IP", NL_int.IP_address, "processing ARP packet"
        # This method assumes that the ARP packet is at the head of this interface's input queue.
        src_IP = frame.ip_datagram.get_src_IP()

        if NL_int.is_ARP_reply(frame):
            # Update the ARP table
            print "IP", NL_int.IP_address, "updating ARP table"
            NL_int.ARP_table[src_IP] = {}
            NL_int.ARP_table[src_IP]["MAC"] = frame.get_src_MAC()
            NL_int.ARP_table[src_IP]["TTL"] = NLInterface.DEFAULT_ARP_TTL

            return None

        elif NL_int.is_ARP_query(frame):
            # Reply to ARP query
            print "IP", NL_int.IP_address, "replying to ARP query"
            sender_MAC = frame.get_src_MAC()

            frame.set_dest_MAC(frame.get_src_MAC())
            frame.set_src_MAC(NL_int.MAC_address)
            datagram = frame.ip_datagram

            sender_IP = datagram.get_src_IP()

            datagram.set_dest_IP(sender_IP)
            datagram.set_src_IP(NL_int.IP_address)
            # update this node's ARP table
            NL_int.ARP_table[sender_IP] = {"MAC": sender_MAC, "TTL": NLInterface.DEFAULT_ARP_TTL}

            return frame

    def is_ARP_query(self, frame):
        datagram = frame.ip_datagram
        return isinstance(frame, EthernetFrame) and frame.header.dest_MAC == NLInterface.ARP_MAC \
               and datagram.segment == NLInterface.ARP_payload

    def is_ARP_reply(self, frame):
        datagram = frame.ip_datagram
        return isinstance(frame, EthernetFrame) and frame.header.dest_MAC != NLInterface.ARP_MAC \
               and datagram.segment == NLInterface.ARP_payload

    '''constructs an ARP ethernet frame to be sent out over the network'''
    def make_ARP_frame(self, src_IP, dest_IP, src_MAC):
        ARP_datagram = IPDatagram(IPHeader(src_IP, dest_IP), NLInterface.ARP_payload)
        ARP_frame = EthernetFrame(EthernetHeader(src_MAC, NLInterface.ARP_MAC), ARP_datagram)
        return ARP_frame
