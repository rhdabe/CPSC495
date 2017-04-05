from IP import *
class EthernetHeader:
    length = 8 # bits
    def __init__(self, src, dst):
        assert 1 <= src < 16, "ERROR: source MAC is a 4 bit number excluding 0"
        assert 0 <= dst < 16, "ERROR: destination MAC is a 4 bit number including 0 (broadcast)"
        self.src_MAC = src
        self.dest_MAC = dst

    def __str__(self):
        return "src_MAC:" + str(self.src_MAC) + " dest_MAC:" + str(self.dest_MAC)
        # return '{0:b}{1:b}'.format(self.src_MAC,self.dest_MAC)


class EthernetFrame:
    def __init__(self, header, datagram):
        # assert isinstance(datagram, IPDatagram), "ERROR: %s is not an IPDatagram " % datagram
        # assert isinstance(header, EthernetHeader), "ERROR: %s is not an EthernetHeader" % header
        self.header = header
        self.ip_datagram = datagram

    def set_src_MAC(self, sm):
        self.header.src_MAC = sm

    def get_src_MAC(self):
        return self.header.src_MAC

    def set_dest_MAC(self, dm):
        self.header.dest_MAC = dm

    def get_dest_MAC(self):
        return self.header.dest_MAC

    def get_bit_string(self):
        # TODO make this really work!!!
        return "101"

    def __str__(self):
        return 'ethernet_header:%s ip_datagram:%s' % (self.header, self.ip_datagram)
