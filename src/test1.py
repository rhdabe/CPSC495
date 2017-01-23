import test2
import src.Network
import sys
from PyQt4.Qt import *

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



class MyPopup(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        self.btn1 = QPushButton("Click me", self)
        self.btn1.setGeometry(QRect(0, 0, 100, 30))
        self.connect(self.btn1, SIGNAL("clicked()"), self.doit)
        self.w = None

    def doit(self):
        print "Opening a new popup window..."
        self.w = MyPopup()
        self.w.setGeometry(QRect(100, 100, 400, 200))
        self.w.show()

    def paintEvent(self, e):
        dc = QPainter(self)
        dc.drawLine(0, 0, 100, 100)
        dc.drawLine(100, 0, 0, 100)

class MainWindow(QMainWindow):
    def __init__(self, *args):
        QMainWindow.__init__(self, *args)
        self.cw = QWidget(self)
        self.setCentralWidget(self.cw)
        self.btn1 = QPushButton("Click me", self.cw)
        self.btn1.setGeometry(QRect(0, 0, 100, 30))
        self.connect(self.btn1, SIGNAL("clicked()"), self.doit)
        self.w = None

    def doit(self):
        print "Opening a new popup window..."
        self.w = MyPopup()
        self.w.setGeometry(QRect(100, 100, 400, 200))
        self.w.show()

class App(QApplication):
    def __init__(self, *args):
        QApplication.__init__(self, *args)
        self.main = MainWindow()
        self.connect(self, SIGNAL("lastWindowClosed()"), self.byebye )
        self.main.show()

    def byebye(self):
        print"bye bye"

app = App(sys.argv)
MainWindow = MainWindow()
sys.exit(app.exec_())