import test2
import src.Network
import sys
from PyQt4.Qt import *
from Node import *
from Connection import *
from RSegments.EthernetFrame import *


class Frame:

    def __init__(self, srcMAC, destMAC, payload):
        self.dest_MAC = destMAC
        self.src_MAC = srcMAC
        self.payload = payload
        self.bit_string = None

connection = Connection("Coax", 100)

s1 = Switch()
s1.new_interface()  # Will have MAC address 1
s1.switch_table[2] = {"Interface":0, "TTL": 100}

s2 = Switch()
s2.new_interface()  # Will have MAC address 2

s1.new_interface() # interface frame will come in on

int1 = s1.interfaces[0]
int1.connect(connection)
int2 = s2.interfaces[0]
int2.connect(connection)
int3 = s1.interfaces[1]

connection.connect2(int1, int2)

frame = EthernetFrame(EthernetHeader(3,2), "01010100011010000110100101110011001000000110100101110011001000000110000100100000011001100111001001100001011011010110010100111111")
#ascii for This is a frame?


#  Now we're gonna pretend int 1 just received the frame to see if s1 will broadcast it correctly.
int3.active = True
int3.received = True
int3.frame = frame

while int1.is_active() or int3.is_active():
    s1.transmit_all_interfaces()
    s2.transmit_all_interfaces()
    s1.read_all_interfaces()
    s2.read_all_interfaces()

print "sent", int1.bit_string
print "got ", int2.bit_string



# test2.init()
# print test2.globvar
# src.Network.network_init()
# network = src.Network.network
# if network != None: print "it worked"
#
# list = [(0,1),(0,2)]
# list2 = [(0,1),(0,2)]
# print list2
# for connection in list:
#     list2.remove(connection)
#     print list2



# class MyPopup(QWidget):
#     def __init__(self):
#         QWidget.__init__(self)
#         self.btn1 = QPushButton("Click me", self)
#         self.btn1.setGeometry(QRect(0, 0, 100, 30))
#         self.connect(self.btn1, SIGNAL("clicked()"), self.doit)
#         self.w = None
#
#     def doit(self):
#         print "Opening a new popup window..."
#         self.w = MyPopup()
#         self.w.setGeometry(QRect(100, 100, 400, 200))
#         self.w.show()
#
#     def paintEvent(self, e):
#         dc = QPainter(self)
#         dc.drawLine(0, 0, 100, 100)
#         dc.drawLine(100, 0, 0, 100)
#
# class MainWindow(QMainWindow):
#     def __init__(self, *args):
#         QMainWindow.__init__(self, *args)
#         self.cw = QWidget(self)
#         self.setCentralWidget(self.cw)
#         self.btn1 = QPushButton("Click me", self.cw)
#         self.btn1.setGeometry(QRect(0, 0, 100, 30))
#         self.connect(self.btn1, SIGNAL("clicked()"), self.doit)
#         self.w = None
#
#     def doit(self):
#         print "Opening a new popup window..."
#         self.w = MyPopup()
#         self.w.setGeometry(QRect(100, 100, 400, 200))
#         self.w.show()
#
# class App(QApplication):
#     def __init__(self, *args):
#         QApplication.__init__(self, *args)
#         self.main = MainWindow()
#         self.connect(self, SIGNAL("lastWindowClosed()"), self.byebye )
#         self.main.show()
#
#     def byebye(self):
#         print"bye bye"
#
# app = App(sys.argv)
# MainWindow = MainWindow()
# sys.exit(app.exec_())