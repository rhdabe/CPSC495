from NQueue import NQueue
from RSegments.IP import *
from RSegments.Ethernet import *
class LLInterface(object):
    # TODO for now use infinite queues.  Later will set queue size.
    # TODO apparently switch interfaces can send and receive at the same time... maybe figure that out later.
    # TODO apparently switches do not have MAC addresses for interfaces that connect to Hosts or Routers.


    #MAC addresses start from 1.  0 is the broadcast address.
    static_MAC = 1

    def __init__(self, node):
        self.node = node
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
        print "interface connected to", connection
        self.connection = connection

    def disconnect(self, connection):
        self.connection = None

    def send_frame(self, frame):
        # command from switch to send a frame
        assert isinstance(frame, EthernetFrame), "ERROR: %s is not an EthernetFrame" % frame
        if self.transmitting:
            print "switch adding frame to output queue"
            self.output_LL_queue.enqueue(frame)
        else:
            print "starting frame transmission"
            self.transmitting = True
            self.frame = frame
            # TODO This will be fixed eventually (below)
            self.bit_string = frame.get_bit_string()
            self.connection.wake_up(self)
            self.send_bit()

    def transmit(self):
        if self.transmitting:
            self.send_bit()
        elif not self.output_LL_queue.isEmpty():
            self.send_frame(self.output_LL_queue.dequeue())

    def send_bit(self):
        if len(self.bit_string) > self.next_bit:
            print "sending bit", self.bit_string[self.next_bit]
            self.connection.transmit(self.bit_string[self.next_bit])
            self.next_bit += 1
        else:
            print "no more bits to send"
            #we're done transmitting
            self.transmitting = False
            self.connection.shut_down(self)

    def parse_bit_string(self):
        #TODO: This doesn't really parse anything right now.  Maybe do later.
        self.connection.finish_transmission(self)

    def read(self):
        print "reading bit", self.connection.state
        self.bit_string += str(self.connection.state)

    def parse_bit_string(self):
        #TODO Maybe later I can make this actually legit.
        self.frame = self.connection.other_interface(self).frame

    def is_transmitting(self):
        return self.transmitting or not self.output_LL_queue.isEmpty()

    def is_receiving(self):
        return self.receiving

    def is_transmitting(self):
        return self.transmitting or not self.output_LL_queue.isEmpty()

    def has_received(self):
        return self.received

    def is_active(self):
        return self.transmitting or self.receiving or self.received or not self.output_LL_queue.isEmpty()

    def get_frame(self):
        self.received = False
        frame = self.frame
        self.frame = None
        return frame

    def wake_up(self):
        # Signals the beginning of an incoming frame.
        print"I'm LLInterface with MAC", self.MAC_address, "and I'm awake!"
        self.active = True
        self.receiving = True

    def shut_down(self, f):
        # Signals the end of an incoming frame.
        print"I'm LLInterface with MAC", self.MAC_address, "and I'm asleep!"
        self.active = False
        self.receiving = False
        self.received = True
        self.frame = f

class NLInterface (LLInterface):
    # TODO this is flat IP.  Consider making it hierarchical.
    # TODO could implement using bitwise operators and keep IP addresses as integer values.
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
        self.ARP_table = node.ARP_table

        # List of packets waiting on ARP replies.  Used to prevent this router from ARP spamming.
        self.ARP_list = []

    def shut_down(self, frame):
        # Signals the end of an incoming frame.
        print "I'm NLInterface MAC", self.MAC_address, "and I'm asleep!"
        self.receiving = False
        self.received = True
        self.input_NL_queue.enqueue(frame)

    def send_datagram(self, datagram):
        assert isinstance(datagram, IPDatagram), "ERROR: %s is not an IPDatagram" % datagram
        # command from switch to send a frame
        self.output_NL_queue.add(datagram)

    def process_output_queue(self):

        if not self.output_NL_queue.isEmpty():
            frame = self.output_NL_queue.peek_head()
            datagram = frame.IP_datagram
            dest_IP = datagram.get_dest_IP()
            # Passing through a router means moving to a new subnet.
            # Thus, a new dest_MAC address is needed which is either in the ARP table, or else needs to be queried via
            #  ARP.  The src_MAC also must be updated to the MAC address of this interface.

            dest_dict = self.ARP_table.get(dest_IP, {})

            dest_MAC = dest_dict.get("MAC", -1) if dest_dict != {} else -1

            if dest_MAC != -1:
                # If we know the MAC address associated with the destination IP, then send,
                # updating both the dest_MAC and src_MAC fields of the EthernetFrame
                frame.src_MAC = self.MAC_address
                frame.dest_MAC = dest_MAC
                self.send_frame(self.output_NL_queue.dequeue())
            else:
                if not self.ARP_list.__contains__(frame):
                    # If we do not know, and aren't already waiting for an ARP reply, we must leave the IPDatagram
                    # in the queue, and enact ARP.
                    print "Sending ARP query"
                    arp_frame = self.make_ARP_frame(self.IP_address, dest_IP, self.MAC_address)
                    self.send_frame(arp_frame)
                    self.ARP_list.append(frame)

            #   else: If this packet is already waiting on an ARP reply, don't send another one.

    def is_ARP_packet(self, frame):
        return frame.IP_datagram.payload == NLInterface.ARP_payload

    '''either returns the ARP packet to sender with this interface's MAC address as the src_MAC
        or else updates the ARP table stored in the Router to which this interface belongs.'''
    def process_ARP_packet(self):
        print "Processing ARP packet"
        # This method assumes that the ARP packet is at the head of this interface's input queue.
        frame = self.input_NL_queue.dequeue()
        src_IP = frame.IP_datagram.get_src_IP()

        if self.is_ARP_reply(frame):
            print "updating ARP table"
            self.ARP_table[src_IP] = {}
            self.ARP_table[src_IP]["MAC"] = frame.src_MAC
            self.ARP_table[src_IP]["TTL"] = NLInterface.DEFAULT_ARP_TTL

        elif self.is_ARP_query(frame):
            print "replying to ARP query"
            sender_MAC = frame.get_src_MAC()

            frame.set_dest_MAC(frame.get_src_MAC())
            frame.set_src_MAC(self.MAC_address)
            datagram = frame.IP_datagram

            sender_IP = datagram.get_src_IP()

            self.ARP_table[sender_IP] = {}
            self.ARP_table[sender_IP]["MAC"] = sender_MAC
            self.ARP_table[sender_IP]["TTL"] = NLInterface.DEFAULT_ARP_TTL

            datagram.set_dest_IP(datagram.get_src_IP())
            datagram.set_src_IP(self.IP_address)
            self.output_NL_queue.enqueue(frame)

            # update this node's ARP table

    def is_ARP_query(self, frame):
        datagram = frame.IP_datagram
        return isinstance(frame, EthernetFrame) and frame.header.dest_MAC == NLInterface.ARP_MAC \
               and datagram.payload == NLInterface.ARP_payload

    def is_ARP_reply(self, frame):
        datagram = frame.IP_datagram
        return isinstance(frame, EthernetFrame) and frame.header.dest_MAC != NLInterface.ARP_MAC \
               and datagram.payload == NLInterface.ARP_payload

    '''constructs an ARP ethernet frame to be sent out over the network'''
    def make_ARP_frame(self, src_IP, dest_IP, src_MAC):
        ARP_datagram = IPDatagram(IPHeader(src_IP, dest_IP), NLInterface.ARP_payload)
        ARP_frame = EthernetFrame(EthernetHeader(src_MAC, NLInterface.ARP_MAC), ARP_datagram)
        return ARP_frame
