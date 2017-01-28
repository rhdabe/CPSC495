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

    def __init__(self, interface1, interface2, type = "Coax", length= 100):
        #Note that node1 and node2 are Node descendent instances, not node ids.
        self.connection_id = Connection.static_id
        Connection.static_id += 1
        self.interfaces = [interface1, interface2]
        self.connectionType = type
        self.connectionLength = length
        self.trafficCount = 0


    def get_latency(self):
        #TODO some sort of calc based on type and length
        return self.connectionLength

    #TODO : remove this
    # def other_node(self, node):
    #     if node == self.nodes[0]:
    #         return self.nodes[1]
    #     else:
    #         return self.nodes[0]


    def other_interface(self, node):
        if node == self.nodes[0]:
            return self.nodes[1]
        else:
            return self.nodes[0]

    def addTraffic(self):
        self.trafficCount += 1

    def removeTraffic(self):
        self.trafficCount -= 1

    def inUse(self):
        if self.trafficCount > 0:
            return True
        return False

    def connect(self, interface):
        # TODO: for now, assume all connections are one to one, but may add broadcasting later (so no exceptions yet)
        if len(self.interfaces) < 2:
            self.interfaces.append(interface)

    def disconnect(self, interface):
        self.interfaces.remove(interface)

    def transmit(self, interface, frame):
        self.other_interface(interface).setFrame(frame)
