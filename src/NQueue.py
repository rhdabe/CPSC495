from SimPyStuff import *


class NQueue(object):

    packet_capacity = 10

    def __init__(self, capacity = packet_capacity):
        self.store = DropStore(src.Network.env, capacity)

    def isEmpty(self):
        return len(self.items) == 0

    def put(self, item):
        return self.store.put(item)

    def dropPut(self, item):
        self.store.dropPut(item)

    def get(self):
        return self.store.get()

    def size(self):
        return len(self.store.items)