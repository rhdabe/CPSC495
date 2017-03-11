# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'SendMessageWindow.ui'
#
# Created by: PyQt4 UI code generator 4.11.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui
from PyQt4.QtGui import *
from PyQt4.QtCore import *
import src
from src.Node import Host

from src.Node import Host, Router, Switch

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8


    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)


class TableWindow(object):
    def __init__(self, MainWindow, node):
        self.MainWindow = MainWindow
        self.node = node
        self.setupUi()

    def setupUi(self):
        self.MainWindow.setObjectName(_fromUtf8("TableWindow"))
        self.MainWindow.resize(200, 200)
        self.centralwidget = QtGui.QWidget(self.MainWindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.gridLayout = QtGui.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 1, 3, 1, 1)

        self.toLabel = QtGui.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(16)
        self.toLabel.setFont(font)
        self.toLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.toLabel.setObjectName(_fromUtf8("fromLabel"))
        self.gridLayout.addWidget(self.toLabel, 0, 2, 1, 1)

        spacerItem2 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem2, 4, 2, 1, 1)
        self.MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(self.MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 200, 21))
        self.menubar.setObjectName(_fromUtf8("menubar"))
        self.MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(self.MainWindow)
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
        self.MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(self.MainWindow)

        self.MainWindow.show()

    def retranslateUi(self, MainWindow):

        simNode = src.Network.network.nodes[self.node.getIDInt()]

        text = "Node number: " + str(simNode.node_id) + "\n"


        if self.node.getType() == "Host":
            MainWindow.setWindowTitle(_translate("MainWindow", "Host Routing Table", None))
            text += "Host IP address: " + str(simNode.interfaces[0].IP_address) + "\n"
            self.toLabel.setText(_translate("MainWindow", text + simNode.get_pretty_routing_table(), None))
        elif self.node.getType() == "Router":
            MainWindow.setWindowTitle(_translate("MainWindow", "Router Routing Table", None))
            self.toLabel.setText(_translate("MainWindow", text + simNode.get_pretty_routing_table(), None))
        elif self.node.getType() == "Switch":
            MainWindow.setWindowTitle(_translate("MainWindow", "Switch Table", None))
            self.toLabel.setText(_translate("MainWindow", text + simNode.get_pretty_switch_table(), None))

