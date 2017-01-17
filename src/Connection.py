class Connection:
    static_id = 0;
    def __init__(self, node1, node2, type, length):
        #Note that node1 and node2 are Node descendent instances, not node ids.
        self.connection_id = Connection.static_id
        Connection.static_id += 1
        self.nodes = [node1, node2]
        self.connectionType = type
        self.connectionLength = length
        self.trafficCount = 0

    def other_node(self, node):
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


