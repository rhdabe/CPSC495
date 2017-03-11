from IP import *
class EthernetHeader:
    length = 8 # bits
    def __init__(self, src, dst):
        assert 1 <= src < 16, "ERROR: source MAC is a 4 bit number excluding 0"
        assert 0 <= dst < 16, "ERROR: destination MAC is a 4 bit number including 0 (broadcast)"
        self.src_MAC = src
        self.dest_MAC = dst

    def __str__(self):
        return '{0:b}{1:b}'.format(self.src_MAC,self.dest_MAC)


class EthernetFrame:
    def __init__(self, header, datagram):
        #TODO put this back sometime maybe.
        assert isinstance(datagram, IPDatagram), "ERROR: %s is not an IPDatagram " % datagram
        assert isinstance(header, EthernetHeader), "ERROR: %s is not an EthernetHeader" % header
        self.header = header
        self.IP_datagram = datagram

    def get_src_MAC(self):
        return self.header.src_MAC

    def get_dest_MAC(self):
        return self.header.dest_MAC

