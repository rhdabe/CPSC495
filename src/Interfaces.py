from NQueue import NQueue
class LLInterface(object):
    # TODO apparently switch interfaces can send and receive at the same time... maybe figure that out later.

    #MAC addresses start from 1.  0 is the broadcast address.
    static_MAC = 1

    def __init__(self):
        self.output_queue = NQueue()
        self.MAC_address = LLInterface.static_MAC
        LLInterface.static_MAC += 1
        self.connection = None  # points to current connection object
        self.frame = None  # points to current frame to be transmitted or that has been received.
        self.receiving = False  # currently receiving bit string to be parsed into self.frame
        self.received = False  # a frame has been received.
        self.transmitting = False  # currently transmitting self.frame
        self.bit_string = ''  # will hold bit string to be parsed if receiving, or to be transmitted if transmitting
        self.next_bit = 0  # index of next bit to be transmitted from self.bit_string

    def is_transmitting(self):
        return self.transmitting or not self.output_queue.isEmpty()

    def connect(self, connection):
        self.connection = connection
        connection.connect1(self)

    def disconnect(self, connection):
        self.connection.disconnect(self)
        self.connection = None

    def set_frame(self, frame):
        self.frame = frame

    def transmit(self):
        if self.transmitting:
            self.send_bit()
        elif not self.output_queue.isEmpty():
            self.send(self.output_queue.deque())

    def send(self, frame):
        if self.transmitting:
            print "switch adding frame to output queue"
            self.output_queue.enqueue(frame)
        else:
            print "starting frame transmission"
            self.transmitting = True
            self.active = True
            self.frame = frame
            # TODO This will be fixed eventually (below)
            self.bit_string = frame.get_bit_string()
            self.connection.wake_up(self)
            self.send_bit()

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

    def is_receiving(self):
        return self.receiving

    def is_transmitting(self):
        return self.transmitting or not self.output_queue.isEmpty()

    def has_received(self):
        return self.received

    def is_active(self):
        return self.transmitting or self.receiving or self.received or not self.output_queue.isEmpty()

    def get_frame(self):
        self.received = False
        frame = self.frame
        self.frame = None
        return frame

    def wake_up(self):
        print"I'm MAC", self.MAC_address, "and I'm awake!"
        self.active = True
        self.receiving = True

    def shut_down(self):
        print"I'm MAC", self.MAC_address, "and I'm asleep!"
        self.active = False
        self.receiving = False

class NLInterface (LLInterface):
    # TODO this is flat IP.  Consider making it hierarchical.
    # TODO could implement using bitwise operators and keep IP addresses as integer values.
    static_IP = 1

    def __init__(self):
        LLInterface.__init__()
        self.IP_address = NLInterface.static_IP
        NLInterface.static_IP += 1
        self.input_queue = NQueue()