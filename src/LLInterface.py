
class LLInterface(object):
    static_MAC = 1

    def __init__(self):
        self.MAC_address = LLInterface.static_MAC
        LLInterface.static_MAC += 1
        self.connection = None
        self.frame = None

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

    def transmit(self):
        self.connection.transmit(self, self.frame)

    def transmit(self, frame):
        self.frame = frame
        self.transmit()
