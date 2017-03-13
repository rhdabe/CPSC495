from RSegments.Ethernet import *
from RSegments.IP import *
from Interfaces import *



def init():
    global globvar
    globvar = 17

def is_ARP_query(frame):
    datagram = frame.IP_datagram
    return isinstance(frame, EthernetFrame) and frame.header.dest_MAC == NLInterface.ARP_MAC \
           and datagram.payload == NLInterface.ARP_payload

def is_ARP_reply(frame):
    datagram = frame.IP_datagram
    return isinstance(frame, EthernetFrame) and frame.header.dest_MAC != NLInterface.ARP_MAC \
           and datagram.payload == NLInterface.ARP_payload

'''constructs an ARP ethernet frame to be sent out over the network'''
def make_ARP_frame(src_IP, dest_IP, src_MAC):
    ARP_datagram = IPDatagram(IPHeader(src_IP, dest_IP), NLInterface.ARP_payload)
    ARP_frame = EthernetFrame(EthernetHeader(src_MAC, NLInterface.ARP_MAC), ARP_datagram)
    return ARP_frame

def is_ARP_packet(frame):
    return frame.IP_datagram.payload == NLInterface.ARP_payload

p = make_ARP_frame(1, 2, 3)

print "is ARP?", is_ARP_packet(p)

print "is query?", is_ARP_query(p)

print "is reply?", is_ARP_reply(p)

p.set_src_MAC(4)

print "now is reply?", is_ARP_reply(p)

print "is query?", is_ARP_query(p)

print "still ARP?", is_ARP_packet(p)