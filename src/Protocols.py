from RSegments.Segment import *
from Exceptions import *
class ApplicationProtocol:
    src_port = 0
    dest_port = 0

class DefaultProtocol(ApplicationProtocol):
    # 456 for 'def' in default.
    src_port = 456
    dest_port = 456

class ReplyProtocol(ApplicationProtocol):
    # TODO do this
    pass

class TransportProtocol:
    def getSegment(self, message):
        pass

class UDP(TransportProtocol):

    @staticmethod
    def getSegment(message):
        protocol = protocols["App"][message.application_protocol]
        src_port = protocol.src_port
        dest_port = protocol.dest_port
        segment = UDPSegment(UDPHeader(src_port, dest_port), message)
        return segment



protocols = {
    "App":
        {"Default": DefaultProtocol},
    "Trans":
        {"UDP": UDP}, #TODO implement TCP
    "Net":
        {},
    "Link":
        {}
}