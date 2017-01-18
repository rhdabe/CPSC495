# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\QTFiles\MacroView.ui'
#
# Created by: PyQt4 UI code generator 4.11.4
#
# WARNING! All changes made in this file will be lost!

__version__ = "1.0.1"

from PyQt4 import QtCore, QtGui

import src.Network
import src.Node as SimulationNode
import src.Connection as SimulationConnection
from Node import *
import src.SimulationLoop as SimulationLoop
from SendMessageWindow import SendMessage_Window
# import sip
import time

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


class Ui_MainWindow(object):


    def setupUi(self, MainWindow):

        self.simulation_thread = None
        self.simulation_started = False
        self.simulation_paused = False

        self.nodes = {}
        self.selectedNodes = {}
        self.connections = []
        self.selectedConnections = []

        MainWindow.setObjectName(_fromUtf8("MainWindow"))
        MainWindow.resize(805, 585)

        self.MsgWindow = QtGui.QMainWindow(MainWindow)
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.thisMainWindow = MainWindow

        self.frameMain = NetworkFrame(self.centralwidget)

        palette = QtGui.QPalette()
        palette.setColor(QtGui.QPalette.Background, QtCore.Qt.darkGray)

        self.frameMain.setPalette(palette)
        self.frameMain.setAutoFillBackground(False)
        self.frameMain.setGeometry(QtCore.QRect(0, 0, 631, 521))
        self.frameMain.setAcceptDrops(True)
        self.frameMain.setFrameShape(QtGui.QFrame.StyledPanel)
        self.frameMain.setFrameShadow(QtGui.QFrame.Raised)
        self.frameMain.setLineWidth(1)
        self.frameMain.setObjectName(_fromUtf8("frameMain"))

        #Node Properties QDockWidget
        self.dockNodeProperties = QtGui.QDockWidget(self.centralwidget)
        self.dockNodeProperties.setGeometry(QtCore.QRect(580, 10, 211, 251))
        self.dockNodeProperties.setObjectName(_fromUtf8("dockNodeProperties"))
        self.dockNPContents = QtGui.QWidget()
        self.dockNPContents.setObjectName(_fromUtf8("dockNCContents"))
        self.lblLocation = QtGui.QLabel(self.dockNPContents)
        self.lblLocation.setGeometry(QtCore.QRect(30, 50, 46, 13))
        self.lblLocation.setObjectName(_fromUtf8("lblLocation"))
        self.lblType = QtGui.QLabel(self.dockNPContents)
        self.lblType.setGeometry(QtCore.QRect(20, 10, 71, 16))
        self.lblType.setObjectName(_fromUtf8("lblType"))
        self.lblNetworkInfo = QtGui.QLabel(self.dockNPContents)
        self.lblNetworkInfo.setGeometry(QtCore.QRect(20, 90, 91, 16))
        self.lblNetworkInfo.setObjectName(_fromUtf8("lblNetworkInfo"))
        self.lblNetworkInfo.hide()
        self.lblIP = QtGui.QLabel(self.dockNPContents)
        self.lblIP.setGeometry(QtCore.QRect(50, 110, 46, 13))
        self.lblIP.setObjectName(_fromUtf8("lblIP"))
        self.lblIP.hide()
        self.cboNodeType = QtGui.QComboBox(self.dockNPContents)
        self.cboNodeType.setGeometry(QtCore.QRect(108, 10, 81, 22))
        self.cboNodeType.setMaxVisibleItems(3)
        self.cboNodeType.setMaxCount(3)
        self.cboNodeType.setObjectName(_fromUtf8("cboNodeType"))
        self.lblMAC = QtGui.QLabel(self.dockNPContents)
        self.lblMAC.setGeometry(QtCore.QRect(50, 140, 46, 13))
        self.lblMAC.setObjectName(_fromUtf8("lblMAC"))
        self.lblMAC.hide()
        self.txtXPos = QtGui.QPlainTextEdit(self.dockNPContents)
        self.txtXPos.setGeometry(QtCore.QRect(90, 50, 51, 21))
        self.txtXPos.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.txtXPos.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.txtXPos.setObjectName(_fromUtf8("txtXPos"))
        self.txtYPos = QtGui.QPlainTextEdit(self.dockNPContents)
        self.txtYPos.setGeometry(QtCore.QRect(160, 50, 51, 21))
        self.txtYPos.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.txtYPos.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.txtYPos.setObjectName(_fromUtf8("txtYPos"))
        self.frameMain.addPosition(self.txtXPos, self.txtYPos)
        self.txtIP = QtGui.QPlainTextEdit(self.dockNPContents)
        self.txtIP.setGeometry(QtCore.QRect(80, 110, 121, 21))
        self.txtIP.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.txtIP.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.txtIP.setObjectName(_fromUtf8("txtIP"))
        self.txtIP.hide()
        self.txtMAC = QtGui.QPlainTextEdit(self.dockNPContents)
        self.txtMAC.setGeometry(QtCore.QRect(80, 140, 121, 21))
        self.txtMAC.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.txtMAC.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.txtMAC.setObjectName(_fromUtf8("txtMAC"))
        self.txtMAC.hide()
        self.btnModifyNode = QtGui.QPushButton(self.dockNPContents)
        self.btnModifyNode.setGeometry(QtCore.QRect(80, 200, 75, 23))
        self.btnModifyNode.setObjectName(_fromUtf8("btnModifyNode"))
        self.btnModifyNode.setEnabled(False)
        self.btnDeleteNode = QtGui.QPushButton(self.dockNPContents)
        self.btnDeleteNode.setGeometry(QtCore.QRect(120, 170, 75, 23))
        self.btnDeleteNode.setObjectName(_fromUtf8("btnDeleteNode"))
        self.btnDeleteNode.setEnabled(False)
        self.btnAddNode = QtGui.QPushButton(self.dockNPContents)
        self.btnAddNode.setGeometry(QtCore.QRect(30, 170, 75, 23))
        self.btnAddNode.setObjectName(_fromUtf8("btnAddNode"))
        self.dockNodeProperties.setWidget(self.dockNPContents)

        #Connection Properties QDockWidget
        self.dockConnectionProperties = QtGui.QDockWidget(self.centralwidget)
        self.dockConnectionProperties.setGeometry(QtCore.QRect(560, 270, 211, 231))
        self.dockConnectionProperties.setObjectName(_fromUtf8("dockConnectionProperties"))
        self.dockCPContents = QtGui.QWidget()
        self.dockCPContents.setObjectName(_fromUtf8("dockCPContents"))
        self.lblConnectionLength = QtGui.QLabel(self.dockCPContents)
        self.lblConnectionLength.setGeometry(QtCore.QRect(30, 50, 41, 16))
        self.lblConnectionLength.setObjectName(_fromUtf8("lblConnectionLength"))
        self.lblConnectionType = QtGui.QLabel(self.dockCPContents)
        self.lblConnectionType.setGeometry(QtCore.QRect(10, 10, 81, 20))
        self.lblConnectionType.setObjectName(_fromUtf8("lblConnectionType"))
        self.lblConnectionBandwidth = QtGui.QLabel(self.dockCPContents)
        self.lblConnectionBandwidth.setGeometry(QtCore.QRect(20, 80, 61, 16))
        self.lblConnectionBandwidth.setObjectName(_fromUtf8("lblConnectionBandwidth"))
        self.cboConnectionType = QtGui.QComboBox(self.dockCPContents)
        self.cboConnectionType.setGeometry(QtCore.QRect(108, 10, 81, 22))
        self.cboConnectionType.setMaxVisibleItems(3)
        self.cboConnectionType.setMaxCount(3)
        self.cboConnectionType.setObjectName(_fromUtf8("cboConnectionType"))
        self.txtConnectionLength = QtGui.QPlainTextEdit(self.dockCPContents)
        self.txtConnectionLength.setGeometry(QtCore.QRect(90, 50, 61, 21))
        self.txtConnectionLength.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.txtConnectionLength.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.txtConnectionLength.setObjectName(_fromUtf8("txtConnectionLength"))
        self.txtConnectionBandwidth = QtGui.QPlainTextEdit(self.dockCPContents)
        self.txtConnectionBandwidth.setGeometry(QtCore.QRect(90, 80, 61, 21))
        self.txtConnectionBandwidth.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.txtConnectionBandwidth.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.txtConnectionBandwidth.setObjectName(_fromUtf8("txtConnectionBandwidth"))
        self.btnModifyConnection = QtGui.QPushButton(self.dockCPContents)
        self.btnModifyConnection.setGeometry(QtCore.QRect(60, 170, 75, 23))
        self.btnModifyConnection.setObjectName(_fromUtf8("btnModifyConnection"))
        self.btnAddConnection = QtGui.QPushButton(self.dockCPContents)
        self.btnAddConnection.setGeometry(QtCore.QRect(40, 140, 75, 23))
        self.btnAddConnection.setObjectName(_fromUtf8("btnAddConnection"))
        self.btnDeleteConnection = QtGui.QPushButton(self.dockCPContents)
        self.btnDeleteConnection.setGeometry(QtCore.QRect(120, 140, 75, 23))
        self.btnDeleteConnection.setObjectName(_fromUtf8("btnDeleteConnection"))
        self.dockConnectionProperties.setWidget(self.dockCPContents)

        # Simulation Controls QDockWidget
        self.dockSimulationControls = QtGui.QDockWidget(self.centralwidget)
        self.dockSimulationControls.setGeometry(QtCore.QRect(550, 500, 225, 96))
        self.dockSimulationControls.setObjectName(_fromUtf8("dockSimulationControls"))
        self.dockSCContents = QtGui.QWidget()
        self.dockSCContents.setObjectName(_fromUtf8("dockSCContents"))
        self.btnStart = QtGui.QPushButton(self.dockSCContents)
        self.btnStart.setGeometry(QtCore.QRect(0, 0, 50, 23))
        self.btnStart.setObjectName(_fromUtf8("btnStartButton"))
        self.btnNext = QtGui.QPushButton(self.dockSCContents)
        self.btnNext.setGeometry(QtCore.QRect(55, 0, 50, 23))
        self.btnNext.setObjectName(_fromUtf8("btnNextButton"))
        self.btnPlay = QtGui.QPushButton(self.dockSCContents)
        self.btnPlay.setGeometry(QtCore.QRect(110, 0, 50, 23))
        self.btnPlay.setObjectName(_fromUtf8("btnPlayButton"))
        self.btnPause = QtGui.QPushButton(self.dockSCContents)
        self.btnPause.setGeometry(QtCore.QRect(165, 0, 50, 23))
        self.btnPause.setObjectName(_fromUtf8("btnPauseButton"))
        self.btnMsg = QtGui.QPushButton(self.dockSCContents)
        self.btnMsg.setGeometry(QtCore.QRect(0, 30, 60, 23))
        self.btnMsg.setObjectName(_fromUtf8("btnMsgButton"))
        self.updateIntervalSpinner = QtGui.QSpinBox(self.dockSCContents)
        self.lblUpdateInterval = QtGui.QLabel(self.dockSCContents)
        self.lblUpdateInterval.setGeometry(QtCore.QRect(65, 30, 100, 20))
        self.lblUpdateInterval.setObjectName(_fromUtf8("lblUpdateInterval"))
        self.updateIntervalSpinner.setGeometry(QtCore.QRect(170, 30, 50, 20))
        self.updateIntervalSpinner.setObjectName(_fromUtf8("spinnerUpdateInterval"))
        self.updateIntervalSpinner.setRange(0, 1000)
        self.updateIntervalSpinner.setSingleStep(100)
        self.dockSimulationControls.setWidget(self.dockSCContents)


        # some temp stuff
        MainWindow.setCentralWidget(self.centralwidget)
        self.actionNew = QtGui.QAction(MainWindow)
        self.actionNew.setObjectName(_fromUtf8("actionNew"))
        # self.actionOpen = QtGui.QAction(MainWindow)
        # self.actionOpen.setObjectName(_fromUtf8("actionOpen"))
        # self.actionRecent = QtGui.QAction(MainWindow)
        # self.actionRecent.setObjectName(_fromUtf8("actionRecent"))
        # self.actionSave = QtGui.QAction(MainWindow)
        # self.actionSave.setObjectName(_fromUtf8("actionSave"))
        # self.actionSave_As = QtGui.QAction(MainWindow)
        # self.actionSave_As.setObjectName(_fromUtf8("actionSave_As"))
        self.actionExit = QtGui.QAction(MainWindow)
        self.actionExit.setObjectName(_fromUtf8("actionExit"))

        # I cannot figure out how create generic calls here yet so will need to redo each time .ui file is recreated
        self.initializeWidgets();

        self.retranslateUi(MainWindow)
        self.cboNodeType.setCurrentIndex(0)
        self.cboConnectionType.setCurrentIndex(0)

        # calling functions from buttons here
        QtCore.QObject.connect(self.cboConnectionType, QtCore.SIGNAL(_fromUtf8("activated(int)")), self.decideBandwidth)
        QtCore.QObject.connect(self.btnAddConnection, QtCore.SIGNAL(_fromUtf8("clicked()")), self.addConnection)
        QtCore.QObject.connect(self.btnDeleteConnection, QtCore.SIGNAL(_fromUtf8("clicked()")), self.deleteSelectedConnections)
        QtCore.QObject.connect(self.btnModifyConnection, QtCore.SIGNAL(_fromUtf8("clicked()")), self.modifyConnection)
        QtCore.QObject.connect(self.btnAddNode, QtCore.SIGNAL(_fromUtf8("clicked()")), self.addNode)
        QtCore.QObject.connect(self.btnDeleteNode, QtCore.SIGNAL(_fromUtf8("clicked()")), self.deleteSelectedNodes)
        QtCore.QObject.connect(self.btnModifyNode, QtCore.SIGNAL(_fromUtf8("clicked()")), self.modifyNode)
        QtCore.QObject.connect(self.btnStart, QtCore.SIGNAL(_fromUtf8("clicked()")), self.startSimulation)
        QtCore.QObject.connect(self.btnNext, QtCore.SIGNAL(_fromUtf8("clicked()")), self.stepSimulation)
        QtCore.QObject.connect(self.btnPause, QtCore.SIGNAL(_fromUtf8("clicked()")), self.pauseSimulation)
        QtCore.QObject.connect(self.btnPlay, QtCore.SIGNAL(_fromUtf8("clicked()")), self.playSimulation)
        QtCore.QObject.connect(self.btnMsg, QtCore.SIGNAL(_fromUtf8("clicked()")),
                               self.openMsgWindow)  # Button to Open MSG window
        # copy to here




        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow", None))
        self.dockNodeProperties.setWindowTitle(_translate("MainWindow", "Node Properties", None))
        self.lblLocation.setText(_translate("MainWindow", "Location", None))
        self.lblType.setText(_translate("MainWindow", "Node Type", None))
        self.lblNetworkInfo.setText(_translate("MainWindow", "Network Info", None))
        self.lblIP.setText(_translate("MainWindow", "IP", None))
        self.lblMAC.setText(_translate("MainWindow", "MAC", None))
        self.btnModifyNode.setText(_translate("MainWindow", "Modify", None))
        self.btnDeleteNode.setText(_translate("MainWindow", "Delete", None))
        self.btnAddNode.setText(_translate("MainWindow", "Add", None))
        self.dockConnectionProperties.setWindowTitle(_translate("MainWindow", "Connection Properties", None))
        self.lblConnectionLength.setText(_translate("MainWindow", "Length", None))
        self.lblConnectionType.setText(_translate("MainWindow", "Connection Type", None))
        self.lblConnectionBandwidth.setText(_translate("MainWindow", "Bandwidth", None))
        self.btnModifyConnection.setText(_translate("MainWindow", "Modify", None))
        self.btnModifyConnection.setEnabled(False)
        self.btnAddConnection.setText(_translate("MainWindow", "Add", None))
        self.btnAddConnection.setEnabled(False)
        self.btnDeleteConnection.setText(_translate("MainWindow", "Delete", None))
        self.btnDeleteConnection.setEnabled(False)
        self.actionNew.setText(_translate("MainWindow", "New", None))
        # self.actionOpen.setText(_translate("MainWindow", "Open", None))
        # self.actionRecent.setText(_translate("MainWindow", "Recent", None))
        # self.actionSave.setText(_translate("MainWindow", "Save", None))
        # self.actionSave_As.setText(_translate("MainWindow", "Save As...", None))
        self.actionExit.setText(_translate("MainWindow", "Exit", None))
        self.btnStart.setText(_translate("MainWindow", "Start", None))
        self.btnNext.setText(_translate("MainWindow", "Next", None))
        self.btnPlay.setText(_translate("MainWindow", "Play", None))
        self.btnPause.setText(_translate("MainWindow", "Pause", None))
        self.lblUpdateInterval.setText(_translate("MainWindow", "Update Interval (ms)", None))
        self.dockSimulationControls.setWindowTitle(_translate("MainWindow", "Simulation Controls", None))
        self.btnMsg.setText(_translate("MainWindow", "Messages", None))

    # I cannot figure out how to put these calls elsewhere yet so will need to copy each time .ui file is recreated

    def initializeWidgets(self):
        self.decideBandwidth()
        self.cboConnectionType.addItems(['Coax', 'Fibre', 'Custom'])
        self.cboNodeType.addItems(['Host', 'Router', 'Switch'])

        self.txtConnectionBandwidth.setPlainText(`200`)
        self.txtConnectionLength.setPlainText(`200`)

    def decideBandwidth(self):
        if self.cboConnectionType.currentText() == "Custom":
            self.lblConnectionBandwidth.show()
            self.txtConnectionBandwidth.show()
        else:
            self.lblConnectionBandwidth.hide()
            self.txtConnectionBandwidth.hide()

    def addNode(self):
       #Create the GUI node
        thisNode = Node(self.cboNodeType.currentText(), self.txtXPos.toPlainText(), self.txtYPos.toPlainText())
        self.nodes[int(thisNode.getUniqueID())] = thisNode
        self.placeNodeGraphic(thisNode)

        #Create the simulation node
        self.addSimulationNode()


    def addSimulationNode(self):
        nodeType = self.cboNodeType.currentText()
        if nodeType == "Host":
            src.Network.network.add_node(SimulationNode.Host())
        elif nodeType == "Router":
            src.Network.network.add_node(SimulationNode.Router())
        elif nodeType == "Switch":
            src.Network.network.add_node(SimulationNode.Switch())

    # deletes node, close on repaint
    def deleteSelectedNodes(self):

        for node_id in self.selectedNodes.keys():
            #remove node from nodes dictionary
            self.nodes.pop(node_id)
            #remove node from selectedNodes dictionary
            self.selectedNodes.pop(node_id)
            #remove the corresponding network node
            src.Network.network.remove_node(node_id)

        #TODO recompute routing tables

        self.clearAndRepaint()

    def isNodeSelected(self, node):
        if self.selectedNodes.get(node.getIDInt(), False): return True
        else: return False

    def checkModifyNode(self):
        if len(self.selectedNodes) == 1: self.btnModifyNode.setEnabled(True)
        else: self.btnModifyNode.setEnabled(False)

    def checkAddNode(self):
        #TODO finish this
        pass
    def checkDeleteNodes(self):
        if len(self.selectedNodes) > 0: self.btnDeleteNode.setEnabled(True)
        else: self.btnDeleteNode.setEnabled(False)

    def modifyNode(self):
        #Checking of whether node modification is allowed is handled by enabling/disabling btnModifyNode.
        #(called from NodeLabel.mousePressedEvent())
        #This method should not be called other than by the pressing of said button.
        #TODO consider adding an exception in the case not exactly one node is selected when we get to here

        # TODO Modify multiple selection process as follows:
        # 3:
        #   require use of Shift+Click to select more than one label.

        selectedNode = self.selectedNodes.values()[0]

        #"Modify" GUI node (Remove old node and create new one with the new characteristics.  Necessary because
        #                 simulation nodes must be handled this way, and therefore so too must GUI nodes
        #                 otherwise their id's will no longer match.)
        #TODO This sort of nonsense is a good case for consolidating the two nodes into a single class. Consider it.
        self.deleteSelectedNodes()
        self.addNode()

        self.clearAndRepaint()

    def addConnection(self):

        #TODO consider adding an exception in the case not exactly two nodes are selected when we get here
        #TODO consider adding multiple connections when multiple nodes are selected
        #Easiest would be to make a complete graph out of the selected nodes.

        selectedNodes = self.selectedNodes.values()

        node1 = selectedNodes[0]
        node2 = selectedNodes[1]

        #Add simulation connection
        simNodes = src.Network.network.nodes
        simConnection = SimulationConnection.Connection(simNodes[node1.getIDInt()], simNodes[node2.getIDInt()],
                                       self.cboConnectionType.currentText(),
                                       self.txtConnectionLength.toPlainText())

        src.Network.network.add_connection(node1.getIDInt(), node2.getIDInt(), simConnection)

        #Add GUI connection
        nodeTuple = src.Network.network.get_node_pair_id(node1.getIDInt(), node2.getIDInt())
        self.connections.append(nodeTuple)
        self.placeConnectionGraphic(simConnection.connection_id, simConnection.connectionType, node1, node2)



        #Darren's code
        #TODO remove this
        # tooMany = False
        # numNodes = 0
        #
        # for x in range(len(self.nodes)):
        #     if self.nodes[x].isSelected and numNodes == 0:
        #         node1 = self.nodes[x]
        #         numNodes = numNodes + 1
        #     elif self.nodes[x].isSelected and numNodes == 1:
        #         node2 = self.nodes[x]
        #         numNodes = numNodes + 1
        #     elif self.nodes[x].isSelected and numNodes == 2:
        #         tooMany = True
        #     x = x + 1
        #
        # if not tooMany and numNodes == 2:
        #     connection = Connection(node1, node2, self.txtConnectionBandwidth.toPlainText())
        #     connection.connectionType = self.cboConnectionType.currentText()
        #     connection.connectionLength = self.txtConnectionLength.toPlainText()
        #     connection.connectionBandWidth = self.txtConnectionBandwidth.toPlainText()
        #     self.connections.append(connection)
        #
        #     self.placeConnectionGraphic(connection.connection_id, connection.connectionType, node1, node2)
        # elif tooMany:
        #     print "Cant select more than 2 nodes before attempting to create a connection"
        # else:
        #     print "Must select 2 nodes before attempting to create a connection"

    def deleteSelectedConnections(self):
        #This gets called by the button press.
        print "deleteSelectedConnections()"
        print "connections:"
        print self.connections
        print "selectedConnections:"
        print self.selectedConnections

        for connection in self.selectedConnections:
            #remove GUI connection
            self.connections.remove(connection)
            #remove simulation connection
            del(src.Network.network.connections[connection])
            #remove record of having this connection selected.
            print "connections:"
            print self.connections
            print "selectedConnections:"
            print self.selectedConnections

        self.selectedConnections = []

        print"done deleting now"
        print "connections:"
        print self.connections
        print "selectedConnections:"
        print self.selectedConnections

        self.clearAndRepaint()

    def isConnectionSelected(self, endNodesTuple):
        if self.selectedConnections.__contains__(endNodesTuple): return True
        else: return False

    def checkModifyConnection(self):
        if len(self.selectedConnections) == 1: self.btnModifyConnection.setEnabled(True)
        else: self.btnModifyConnection.setEnabled(False)
    def checkAddConnection(self):
        if len(self.selectedNodes) == 2: self.btnAddConnection.setEnabled(True)
        else: self.btnAddConnection.setEnabled(False)
    def checkDeleteConnections(self):
        if len(self.selectedConnections) > 0: self.btnDeleteConnection.setEnabled(True)
        else: self.btnDeleteConnection.setEnabled(False)

    def modifyConnection(self):
        #Checking of whether connection modification is allowed is handled by enabling/disabling btnModifyConnection.
        #(called from NodeLabel.mousePressedEvent())
        #This method should not be called other than by the pressing of said button.

        # TODO Modify multiple selection process as follows:
        # 3:
        #   require use of Shift+Click to select more than one connection.

        selectedNode = self.selectedNodes.values()[0]

        #"Modify" GUI node (Remove old node and create new one with the new characteristics.  Necessary because
        #                 simulation nodes must be handled this way, and therefore so too must GUI nodes
        #                 otherwise their id's will no longer match.)
        #TODO This sort of nonsense is a good case for consolidating the two nodes into a single class. Consider it.
        self.deleteSelectedNodes()
        self.addNode()

        self.clearAndRepaint()

    def clearAndRepaint(self):
        while self.frameMain.children():
            child = self.frameMain.children()[0]
            child.setParent(None) #Immediately removes child from children list of parent
            child.deleteLater() #Don't care when this happens.  Want to avoid sip.delete() hangups.
           # sip.delete(self.frameMain.children()[0])
                #sip.delete() hangs up sometimes for unknown reason.
                # Node number and deletion order dependent.  Highly reproducible.
        self.rebuildFrameMainGraphics()

    def rebuildFrameMainGraphics(self):
        for x in self.nodes.keys():
            self.placeNodeGraphic(self.nodes[x])

        for node1ID,node2ID in self.connections:
            connection = src.Network.network.get_connection(node1ID, node2ID)
            self.placeConnectionGraphic(connection.connection_id, connection.connectionType,
                                        self.nodes[node1ID], self.nodes[node2ID])

         #TODO this may need to change later too (if it needs to be a dictionary instead)

        #TODO fix and test this.
        #This code is to delete connections if one of their nodes is deleted.
        # for x in range(len(self.connections)):
        #     connectionNodes = self.connections[x].getConnectionNodes()
        #     source = connectionNodes[0]
        #     dest = connectionNodes[1]
        #     if source == None or dest == None:
        #         self.deleteConnection(self.connections[x])
        #     else:
        #         self.placeConnectionGraphic(self.connections[x].getUniqueID(), self.connections[x].getConnectionType(), source, dest)

        self.frameMain.repaint()


    # difficult to implement. Worry about add/delete working properly
    def modifyConnection(self):
        print "modify connection"
        # call repaint

    def placeNodeGraphic(self, aNode):

        nodePosition = aNode.getLocation()
        x1 = int(nodePosition[0])
        y1 = int(nodePosition[1])

        self.lblNode = NodeLabel(self.frameMain)
        self.lblNode.setMainWindow(self)
        self.lblNode.setGeometry(x1, y1, 41, 31)
        self.lblNode.setText(_fromUtf8(""))
        self.lblNode.nodeObject = aNode
        if aNode.getType() == "Host":
            self.lblNode.setPixmap(QtGui.QPixmap(_fromUtf8("../Resources/pc.png")))
        elif aNode.getType() == "Router":
            self.lblNode.setPixmap(QtGui.QPixmap(_fromUtf8("../Resources/router.png")))
        else:
            self.lblNode.setPixmap(QtGui.QPixmap(_fromUtf8("../Resources/switch.png")))

        self.lblNode.setObjectName(_fromUtf8(aNode.getUniqueID()))
        self.lblNode.show()

    def placeConnectionGraphic(self, connectionID, connectionType, firstNode, secondNode):

        firstNodeID = firstNode.getIDInt();
        secondNodeID = secondNode.getIDInt();

        # connection will always be a pair of lines 1 horizontal and 1 vertical

        # find center of firstNode image as start x, y
        start = firstNode.getLocation()
        end = secondNode.getLocation()
        x1 = int(start[0]) + 20
        y1 = int(start[1]) + 15

        x2 = int(end[0]) + 20
        y2 = int(end[1]) + 15

        if connectionType == "Coax":
            connectionColor = "blue"
        elif connectionType == "Fibre":
            connectionColor = "red"
        else:
            connectionColor = "green"

        #TODO Remove
        #connectionID = str(connectionID)

        if (x2 - x1) > 0:  # x direction from node 1 to node 2 is positive
            if (y2 - y1) > 0:  # y direction from node 1 to node 2 is positive
                if (x2 - x1) > (y2 - y1):  # line in x direction is longer than y
                    self.drawHorizontalLine(x1, y1, (x2 - x1), connectionColor, connectionID, firstNodeID, secondNodeID)
                    self.drawVerticalLine(x2, y1, (y2 - y1), connectionColor, connectionID, firstNodeID, secondNodeID)
                else:  # line in y is longer than x
                    self.drawVerticalLine(x1, y1, (y2 - y1), connectionColor, connectionID, firstNodeID, secondNodeID)
                    self.drawHorizontalLine(x1, y2, (x2 - x1), connectionColor, connectionID, firstNodeID, secondNodeID)
            else:  # y direction from node 1 to node 2 is negative
                if (x2 - x1) > (y1 - y2):  # line in x direction is longer than y
                    self.drawHorizontalLine(x1, y1, (x2 - x1 + 6), connectionColor, connectionID, firstNodeID, secondNodeID)
                    self.drawVerticalLine(x2, y2, (y1 - y2), connectionColor, connectionID, firstNodeID, secondNodeID)
                else:  # line in y is longer than x
                    self.drawVerticalLine(x1, y2, (y1 - y2), connectionColor, connectionID, firstNodeID, secondNodeID)
                    self.drawHorizontalLine(x1, y2, (x2 - x1), connectionColor, connectionID, firstNodeID, secondNodeID)
        else:  # x direction from node 1 to node 2 is negative
            if (y2 - y1) > 0:  # y direction from node 1 to node 2 is positive
                if (x1 - x2) > (y2 - y1):  # line in x is longer than y
                    self.drawHorizontalLine(x2, y1, (x1 - x2 + 6), connectionColor, connectionID, firstNodeID, secondNodeID)
                    self.drawVerticalLine(x2, y1, (y2 - y1), connectionColor, connectionID, firstNodeID, secondNodeID)
                else:  # line in y is longer than x
                    self.drawVerticalLine(x1, y1, (y2 - y1), connectionColor, connectionID, firstNodeID, secondNodeID)
                    self.drawHorizontalLine(x2, y2, (x1 - x2), connectionColor, connectionID, firstNodeID, secondNodeID)
            else:  # y direction from node 1 to node 2 is negative
                if (x1 - x2) > (y1 - y2):  # line in x is longer than y
                    self.drawHorizontalLine(x2, y1, (x1 - x2), connectionColor, connectionID, firstNodeID, secondNodeID)
                    self.drawVerticalLine(x2, y2, (y1 - y2), connectionColor, connectionID, firstNodeID, secondNodeID)
                else:  # line in y is longer than x
                    self.drawVerticalLine(x1, y2, (y1 - y2), connectionColor, connectionID, firstNodeID, secondNodeID)
                    self.drawHorizontalLine(x2, y2, (x1 - x2), connectionColor, connectionID, firstNodeID, secondNodeID)

    def drawHorizontalLine(self, xPos, yPos, lineLength, lineColor, connectionID, firstNodeID, secondNodeID):

        self.linConnection = NetworkConnection(self.frameMain)
        self.linConnection.connectionID = connectionID
        self.linConnection.nodeTuple = src.Network.network.get_node_pair_id(firstNodeID,secondNodeID)
        self.linConnection.setMainWindow(self)
        self.linConnection.setGeometry(QtCore.QRect(xPos, yPos, lineLength, 6))
        self.linConnection.setStyleSheet(_fromUtf8("color:" + lineColor))
        self.linConnection.setFrameShadow(QtGui.QFrame.Plain)
        self.linConnection.setLineWidth(6)
        self.linConnection.setFrameShape(QtGui.QFrame.HLine)
        self.linConnection.setObjectName(_fromUtf8(str(connectionID) + "H"))
        self.linConnection.lower()
        self.linConnection.show()

    def drawVerticalLine(self, xPos, yPos, lineLength, lineColor, connectionID, firstNodeID, secondNodeID):

        self.linConnection = NetworkConnection(self.frameMain)
        self.linConnection.connectionID = connectionID
        self.linConnection.nodeTuple = src.Network.network.get_node_pair_id(firstNodeID,secondNodeID)
        self.linConnection.setMainWindow(self)
        self.linConnection.setGeometry(QtCore.QRect(xPos, yPos, 6, lineLength))
        self.linConnection.setStyleSheet(_fromUtf8("color:" + lineColor))
        self.linConnection.setFrameShadow(QtGui.QFrame.Plain)
        self.linConnection.setLineWidth(6)
        self.linConnection.setFrameShape(QtGui.QFrame.VLine)
        self.linConnection.setObjectName(_fromUtf8(str(connectionID) + "V"))
        self.linConnection.lower()
        self.linConnection.show()


    def startSimulation(self):
        print "startSimulation"
        if not self.simulation_started:
            self.simulation_started = True

        src.Network.network_init()

    def stepSimulation(self):
        print "stepSimulation"
        if self.simulation_started and self.simulation_paused: src.SimulationLoop.tick()

    def playSimulation(self):
        print "playSimulation"
        self.simulation_paused = False
        #time.sleep() accepts time in seconds.  Spinner displays in ms.
        interval = float(self.updateIntervalSpinner.value() / 1000)
        self.simulation_thread = SimulationLoop.start_simulation(src.Network.network, updateInterval=interval)

    def pauseSimulation(self):
        print"pauseSimulation"
        self.simulation_paused = True
        self.simulation_thread.end()

    def openMsgWindow(self):  # Method to open button window
        SendMessage_Window(self.MsgWindow)


class NodeLabel(QtGui.QLabel):

    def setMainWindow(self, mw):
        self.mainWindow = mw

    def mouseDoubleClickEvent(self, ev):
        print "double click event"

    def mousePressEvent(self, ev):
        # TODO disable add/remove connection buttons at appropriate times.
        # TODO add Shift + Click for multiple selection

        if self.mainWindow.isNodeSelected(self.nodeObject):
            self.mainWindow.selectedNodes.pop(self.nodeObject.getIDInt())
        else:
            self.mainWindow.selectedNodes[self.nodeObject.getIDInt()] = self.nodeObject

        self.highlightSelected()

        self.mainWindow.checkModifyNode()
        self.mainWindow.checkDeleteNodes()
        self.mainWindow.checkModifyConnection()
        self.mainWindow.checkAddConnection()


    def highlightSelected(self):
        if self.mainWindow.isNodeSelected(self.nodeObject):
            if self.nodeObject.getType() == "Host":
                self.setPixmap(QtGui.QPixmap(_fromUtf8("../Resources/pc_hl.png")))
            elif self.nodeObject.getType() == "Router":
                self.setPixmap(QtGui.QPixmap(_fromUtf8("../Resources/router_hl.png")))
            else:
                self.setPixmap(QtGui.QPixmap(_fromUtf8("../Resources/switch_hl.png")))
        else:
            if self.nodeObject.getType() == "Host":
                self.setPixmap(QtGui.QPixmap(_fromUtf8("../Resources/pc.png")))
            elif self.nodeObject.getType() == "Router":
                self.setPixmap(QtGui.QPixmap(_fromUtf8("../Resources/router.png")))
            else:
                self.setPixmap(QtGui.QPixmap(_fromUtf8("../Resources/switch.png")))


class NetworkFrame(QtGui.QFrame):
    myX = 0
    myY = 0
    myW = 0
    myH = 0
    txtXPosBox = None
    txtYPosBox = None

    def addPosition(self, tbXpos, tbYpos):
        self.txtXPosBox = tbXpos
        self.txtYPosBox = tbYpos

    def mousePressEvent(self, ev):

        point = ev.pos()
        posX = self.round10((point.x() + self.myX), 10)
        posY = self.round10((point.y() + self.myY), 10)

        self.txtXPosBox.setPlainText(`posX`)
        self.txtYPosBox.setPlainText(`posY`)

    def round10(self, x, base=10):
        return int(base * round(float(x) / base))


class NetworkConnection(QtGui.QFrame):

    def setMainWindow(self, mw):
        self.mainWindow = mw

    def getLatency(self):
        #TODO make this actually correct
        #Probably calculate from length and type
        return 100

    def getBandwidth(self):
        #TODO make this actually correct
        #Max bandwidth probably determined by type.
        return 200

    def mousePressEvent(self, ev):
        # TODO add Shift + Click for multiple selection
        # TODO disable add/remove connection buttons at appropriate times.

        if self.mainWindow.isConnectionSelected(self.nodeTuple):
            self.mainWindow.selectedConnections.remove(self.nodeTuple)
        else:
            self.mainWindow.selectedConnections.append(self.nodeTuple)

        print self.mainWindow.selectedConnections

        self.highlightSelected()
        self.mainWindow.checkModifyConnection()
        self.mainWindow.checkDeleteConnections()

    def highlightSelected(self):

        vertical = self.parent().findChild(NetworkConnection, (_fromUtf8(str(self.connectionID) + "V")));
        horizontal = self.parent().findChild(NetworkConnection, (_fromUtf8(str(self.connectionID) + "H")));

        if self.mainWindow.isConnectionSelected(self.nodeTuple):
            vertical.setStyleSheet(_fromUtf8("color:" + "yellow"))
            horizontal.setStyleSheet(_fromUtf8("color:" + "yellow"))
        else:
            connection = src.Network.network.get_connection(self.nodeTuple[0], self.nodeTuple[1])
            if connection.connectionType == "Coax":
                vertical.setStyleSheet(_fromUtf8("color:" + "blue"))
                horizontal.setStyleSheet(_fromUtf8("color:" + "blue"))
            elif connection.connectionType == "Fiber":
                vertical.setStyleSheet(_fromUtf8("color:" + "red"))
                horizontal.setStyleSheet(_fromUtf8("color:" + "red"))
            else:
                vertical.setStyleSheet(_fromUtf8("color:" + "green"))
                horizontal.setStyleSheet(_fromUtf8("color:" + "green"))

