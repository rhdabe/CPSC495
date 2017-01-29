
class LLInterface(object):
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

    def setFrame(self, frame):
        self.frame = frame

    def send(self, frame):
        self.transmitting  = True
        self.transmit(frame)

    def transmit(self):
        self.active = True
        self.connection.transmit(self, self.frame)

    def transmit(self, frame):
        self.frame = frame
        self.transmit()

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