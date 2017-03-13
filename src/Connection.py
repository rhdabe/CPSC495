class Connection:
    static_id = 0;

    #TODO remove this.
    # def __init__(self, node1, node2, type = "Coax", length= 100):
    #     #Note that node1 and node2 are Node descendent instances, not node ids.
    #     self.connection_id = Connection.static_id
    #     Connection.static_id += 1
    #     self.nodes = [node1, node2]
    #     self.connectionType = type
    #     self.connectionLength = length
    #     self.trafficCount = 0

    def __init__(self, type="Coax", length=100):
        # Note that node1 and node2 are Node descendant instances, not node ids.
        self.connection_id = Connection.static_id
        Connection.static_id += 1
        self.interfaces = []
        self.connectionType = type
        self.connectionLength = length
        self.trafficCount = 0
        self.state = 0

    def get_latency(self):
        #TODO some sort of calc based on type and length
        return self.connectionLength


    def other_interface(self, interface):
        if interface == self.interfaces[0]:
            return self.interfaces[1]
        else:
            return self.interfaces[0]

    def addTraffic(self):
        self.trafficCount += 1

    def removeTraffic(self):
        self.trafficCount -= 1

    def inUse(self):
        if self.trafficCount > 0:
            return True
        return False

    def connect1(self, interface):
        # TODO: for now, assume all connections are one to one, but may add broadcasting later (so no exceptions yet)
        if len(self.interfaces) < 2:
            self.interfaces.append(interface)

    def connect2(self, interface1, interface2):
        # TODO: for now, assume all connections are one to one, but may add broadcasting later (so no exceptions yet)
        self.interfaces = [interface1, interface2]
        interface1.connect(self)
        interface2.connect(self)

    def disconnect(self, interface):
        self.interfaces.remove(interface)

    def disconnect(self):
        self.interfaces = []

    def reconnect(self, disconnect_int, connect_int):
        self.disconnect(disconnect_int)
        self.connect(connect_int)

    def transmit(self, bit):
        self.state = bit

    def wake_up(self, sending_interface):
        other = self.other_interface(sending_interface)
        print "waking up interface with MAC", other.MAC_address
        other.wake_up()

    def shut_down(self, sending_interface):
        # TODO this cheats by sending the frame over in the shut_down method because bit parsing isn't implemented
        other = self.other_interface(sending_interface)
        print "shutting down interface with MAC", other.MAC_address

        other.shut_down(sending_interface.frame)