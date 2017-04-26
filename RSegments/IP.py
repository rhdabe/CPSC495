
class IPHeader:
    length = 16 # bits

    def __init__(self, src, dst):
        self.src_IP = src
        self.dest_IP = dst

    def __str__(self):
        return "src_IP: " + str(self.src_IP) + " dest_IP: " + str(self.dest_IP)
        # return '{0:b}{1:b}'.format(self.src_IP[0], self.src_IP[1], self.dest_IP[0], self.dest_IP[1])


class IPDatagram:
    def __init__(self, header, payload):
        self.header = header
        self.segment = payload

    # default print notation when printing an IPDatagram
    def __str__(self):
        return "ip_header: %s segment: %s" % (self.header, self.segment)

    def get_src_IP(self):
        return self.header.src_IP

    def set_src_IP(self, s):
        self.header.src_IP = s

    def get_dest_IP(self):
        return self.header.dest_IP

    def set_dest_IP(self, d):
        self.header.dest_IP = d



