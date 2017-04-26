class Connection:
    static_id = 0;
    COAX_LATENCY = 2
    FIBRE_LATENCY = 1

    def __init__(self, type="Coax", length=2):
        # Note that node1 and node2 are Node descendant instances, not node ids.
        self.connection_id = Connection.static_id
        Connection.static_id += 1
        self.interfaces = []
        self.connectionType = type
        self.connectionLength = length
        self.trafficCount = 0
        self.state = 0
        self.customLatency = 2

        #hokey integration list for micro
        self.nodes = []

    def get_latency(self):

        if self.connectionType == "Coax":
            return Connection.COAX_LATENCY * self.connectionLength
        elif self.connectionType == "Fibre":
            return Connection.FIBRE_LATENCY * self.connectionLength
        elif self.connectionType == "Custom":
            return self.customLatency * self.connectionLength
        elif self.connectionType == None:
            return self.connectionLength

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

    def connect_interface(self, interface):
        if len(self.interfaces) < 2:
            self.interfaces.append(interface)

    def connect_nodes(self, node1, node2):
        interface1 = node1.new_interface()
        interface2 = node2.new_interface()
        self.interfaces = [interface1, interface2]
        interface1.connect(self)
        interface2.connect(self)
        self.nodes = [node1, node2]

    '''This method is used to create pseudo connections for reducing the network graph prior to routing table
        calculation'''
    def fake_connect_interfaces(self, interface1, interface2):
        self.interfaces = [interface1, interface2]

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
        other = self.other_interface(sending_interface)
        print "shutting down interface with MAC", other.MAC_address

        other.shut_down(sending_interface.frame)