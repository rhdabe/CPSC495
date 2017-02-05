
class LLInterface(object):
    # TODO apparently switch interfaces can send and receive at the same time... maybe figure that out later.

    #MAC addresses start from 1.  0 is the broadcast address.
    static_MAC = 1

    def __init__(self):
        self.MAC_address = LLInterface.static_MAC
        LLInterface.static_MAC += 1
        self.connection = None  # points to current connection object
        self.frame = None  # points to current frame to be transmitted or that has been received.
        self.active = False  # this interface has some business that needs attending to.
        self.receiving = False  # currently receiving bit string to be parsed into self.frame
        self.received = False  # a frame has been received.
        self.transmitting = False  # currently transmitting self.frame
        self.bit_string = ''  # will hold bit string to be parsed if receiving, or to be transmitted if transmitting
        self.next_bit = 0  # index of next bit to be transmitted from self.bit_string

    def connect(self, connection):
        self.connection = connection
        connection.connect1(self)

    def disconnect(self, connection):
        self.connection.disconnect(self)
        self.connection = None

    def set_frame(self, frame):
        self.frame = frame

    def send(self, frame):
        print "starting frame transmission"
        self.transmitting = True
        self.active = True
        self.frame = frame
        # TODO This will be fixed eventually (below)
        self.bit_string = frame.bit_string
        self.connection.wake_up(self)

    def send_bit(self):

        if len(self.bit_string) > self.next_bit:
            print "sending bit", self.bit_string[self.next_bit]
            self.connection.transmit(self.bit_string[self.next_bit])
            self.next_bit += 1
        else:
            print "no more bits to send"
            #we're done transmitting
            self.transmitting = False
            self.active = False
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
        pass

    def is_transmitting(self):
        pass

    def received(self):
        pass

    def get_frame(self):
        self.active = False
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
