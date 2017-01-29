
class LLInterface(object):
    # TODO apparently switch interfaces can send and receive at the same time... maybe figure that out later.

    #MAC addresses start from 1.  0 is the broadcast address.
    static_MAC = 1

    def __init__(self):
        self.MAC_address = LLInterface.static_MAC
        LLInterface.static_MAC += 1
        self.connection = None
        self.frame = None
        self.active = False
        self.recieving = False
        self.transmitting = False
        self.bit_string = ''
        self.next_bit = 0

    def __init__(self, connection):
        self.MAC_address = LLInterface.static_MAC
        LLInterface.static_MAC += 1
        self.connect(connection)

    def connect(self, connection):
        self.connection = connection
        connection.connect(self)

    def disconnect(self, connection):
        self.connection.disconnect(self)
        self.connection = None

    def set_frame(self, frame):
        self.frame = frame

    def send(self, frame):

        self.transmitting  = True
        self.transmit(frame)

    def parse_bit_string(self):
        #TODO: This doesn't really parse anything right now.  Maybe do later.
        self.connection.finish_transmission(self)

    def transmit(self):
        self.active = True
        if len(self.bit_string) > self.next_bit:
            self.connection.transmit(self, self.bit_string[self.next_bit])
            self.next_bit += 1
        else:
            #we're done transmitting
            self.parse_bit_string()

    def transmit(self, frame):
        self.frame = frame
        self.transmit()

    def read(self):
        self.bit_string += self.connection.state

    def is_receiving(self):
        pass

    def is_transmitting(self):
        pass

    def received(self):
        pass

    def get_frame(self):
        frame = self.frame
        self.frame = None
        return frame