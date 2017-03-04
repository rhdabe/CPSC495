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

from src.Node import Host, Switch, Router

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
        self.setupUi()
        self.node = node

    def setupUi(self):
        self.MainWindow.setObjectName(_fromUtf8("RouterWindow"))
        self.MainWindow.resize(200, 200)
        self.centralwidget = QtGui.QWidget(self.MainWindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.gridLayout = QtGui.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.tableLabel = QtGui.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(16)
        self.tableLabel.setFont(font)
        self.tableLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.tableLabel.setObjectName(_fromUtf8("tableLabel"))
        self.gridLayout.addWidget(self.tableLabel, 0, 2, 1, 1)

        self.MainWindow.show()

    def retranslateUi(self, MainWindow):

        if isinstance(self.node, Host):
            MainWindow.setWindowTitle(_translate("MainWindow", "Host Routing Table", None))
            self.tableLabel.setText(str(self.node.routing_table))
        elif isinstance(self.node, Router):
            MainWindow.setWindowTitle(_translate("MainWindow", "Router Routing Table", None))
            self.tableLabel.setText(str(self.node.routing_table))
        elif isinstance(self.node, Switch):
            MainWindow.setWindowTitle(_translate("MainWindow", "Switch Table", None))
            self.tableLabel.setText(str(self.node.switch_table))

