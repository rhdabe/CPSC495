"""Defines the Packet class"""
__author__ = "Rhys Beck"
__version__ = "2.0.0"
import PyQt4.QtCore as QtCore
from PyQt4.QtCore import *

try:
    _fromUtf8 = QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

class Packet (QObject):

    static_packet_id = 0

    def __init__(self, interface, frame):

        self.connection = None
        self.transmitting = False
        self.frame = frame
        self.current_interface = interface
        self.packet_id = Packet.static_packet_id
        Packet.static_packet_id += 1
        self.moved = pyqtSignal()
        self.microWindow = None

    def connect_to_micro(self, microGUIWindow):
        self.microWindow = microGUIWindow
        self.connect(self, QtCore.SIGNAL(_fromUtf8("valueChanged()")), self.microWindow.updateState())

    def disconnect_from_micro(self):
        self.disconnect(self, QtCore.SIGNAL(_fromUtf8("valueChanged()")), self.microWindow.updateState())
        self.microWindow = None

    def set_current_interface(self, new_interface):
        self.current_interface = new_interface
        self.emit(QtCore.SIGNAL('valueChanged'))

