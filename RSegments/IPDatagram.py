
import EthernetFrame

class IPHeader:
    length = 16 # bits
    def __init__(self, src, dst):
        #src and dst addresses are two-integer tuples satisfying the following constraints:
        # assert 1 < src[0] < 16, "ERROR: source IP is two 4 bit numbers excluding 0"
        # assert 1 < src[1] < 16, "ERROR: source IP is two 4 bit numbers excluding 0"
        # assert 0 < dst[0] < 16, "ERROR: destination IP is two 4 bit numbers including 0 (broadcast)"
        # assert 0 < dst[1] < 16, "ERROR: destination IP is two 4 bit numbers including 0 (broadcast)"
        self.src_IP = src
        self.dest_IP = dst

    def __str__(self):
        return '{0:b}{1:b}'.format(self.src_IP[0], self.src_IP[1], self.dest_IP[0], self.dest_IP[1])


class IPDatagram:
    def __init__(self, header, payload):
        assert isinstance(payload, EthernetFrame), "ERROR: %s is not an EthernetFrame " % (payload)
        self.header = header
        self.frame = payload

    # default print notation when printing an IPDatagram
    def __str__(self):
        return "[IP HEADER: %s , %s]" % (self.ip_header, self.frame)

    def get_src_IP(self):
        return self.header.src_IP

    def get_dest_IP(self):
        return self.header.dest_IP



