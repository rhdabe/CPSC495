from PyQt4 import QtCore, QtGui
from GUI.MicroGUI.MicroWindow import MicroMainWindow
import src.Network
import src.Node as SimulationNode
import src.Connection as SimulationConnection
from Node import *
import src.SimulationLoop as SimulationLoop
from SendMessageWindow import SendMessage_Window
from RoutingOrSwitchTableWindow import TableWindow
import routingTableAlgorithm


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
        self.network_traced = False

        self.nodes = {}
        self.selectedNodes = {}
        self.connections = []
        self.selectedConnections = []

        MainWindow.setObjectName(_fromUtf8("MainWindow"))
        MainWindow.resize(805, 585)

        self.NetworkModifyButtonCallbacks = {}
        self.MsgWindow = None
        self.MicroWindow = None
        self.MsgTemplate = QtGui.QMainWindow(MainWindow)
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
        self.dockNodeProperties.setGeometry(QtCore.QRect(580, 10, 211, 155))
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
        self.txtXPos.setPlainText(_fromUtf8('100'))
        self.txtYPos = QtGui.QPlainTextEdit(self.dockNPContents)
        self.txtYPos.setGeometry(QtCore.QRect(160, 50, 51, 21))
        self.txtYPos.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.txtYPos.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.txtYPos.setObjectName(_fromUtf8("txtYPos"))
        self.txtYPos.setPlainText(_fromUtf8('100'))
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
        self.btnModifyNode.setGeometry(QtCore.QRect(80, 110, 75, 23))
        self.btnModifyNode.setObjectName(_fromUtf8("btnModifyNode"))
        self.btnModifyNode.setEnabled(False)
        self.NetworkModifyButtonCallbacks[self.btnModifyNode] = self.checkModifyNode
        self.btnDeleteNode = QtGui.QPushButton(self.dockNPContents)
        self.btnDeleteNode.setGeometry(QtCore.QRect(120, 80, 75, 23))
        self.btnDeleteNode.setObjectName(_fromUtf8("btnDeleteNode"))
        self.btnDeleteNode.setEnabled(False)
        self.NetworkModifyButtonCallbacks[self.btnDeleteNode] = self.checkDeleteNodes
        self.btnAddNode = QtGui.QPushButton(self.dockNPContents)
        self.btnAddNode.setGeometry(QtCore.QRect(30, 80, 75, 23))
        self.btnAddNode.setObjectName(_fromUtf8("btnAddNode"))
        self.NetworkModifyButtonCallbacks[self.btnAddNode] = None

        self.dockNodeProperties.setWidget(self.dockNPContents)

        #Connection Properties QDockWidget
        self.dockConnectionProperties = QtGui.QDockWidget(self.centralwidget)
        self.dockConnectionProperties.setGeometry(QtCore.QRect(580, 175, 211, 231))
        self.dockConnectionProperties.setObjectName(_fromUtf8("dockConnectionProperties"))
        self.dockCPContents = QtGui.QWidget()
        self.dockCPContents.setObjectName(_fromUtf8("dockCPContents"))
        self.lblConnectionLength = QtGui.QLabel(self.dockCPContents)
        self.lblConnectionLength.setGeometry(QtCore.QRect(30, 40, 41, 16))
        self.lblConnectionLength.setObjectName(_fromUtf8("lblConnectionLength"))
        self.lblConnectionType = QtGui.QLabel(self.dockCPContents)
        self.lblConnectionType.setGeometry(QtCore.QRect(10, 10, 81, 20))
        self.lblConnectionType.setObjectName(_fromUtf8("lblConnectionType"))
        self.lblConnectionBandwidth = QtGui.QLabel(self.dockCPContents)
        self.lblConnectionBandwidth.setGeometry(QtCore.QRect(20, 65, 61, 16))
        self.lblConnectionBandwidth.setObjectName(_fromUtf8("lblConnectionBandwidth"))
        self.cboConnectionType = QtGui.QComboBox(self.dockCPContents)
        self.cboConnectionType.setGeometry(QtCore.QRect(108, 10, 81, 22))
        self.cboConnectionType.setMaxVisibleItems(3)
        self.cboConnectionType.setMaxCount(3)
        self.cboConnectionType.setObjectName(_fromUtf8("cboConnectionType"))
        self.txtConnectionLength = QtGui.QPlainTextEdit(self.dockCPContents)
        self.txtConnectionLength.setGeometry(QtCore.QRect(90, 40, 61, 21))
        self.txtConnectionLength.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.txtConnectionLength.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.txtConnectionLength.setObjectName(_fromUtf8("txtConnectionLength"))
        self.txtConnectionBandwidth = QtGui.QPlainTextEdit(self.dockCPContents)
        self.txtConnectionBandwidth.setGeometry(QtCore.QRect(90, 65, 61, 21))
        self.txtConnectionBandwidth.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.txtConnectionBandwidth.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.txtConnectionBandwidth.setObjectName(_fromUtf8("txtConnectionBandwidth"))
        self.btnModifyConnection = QtGui.QPushButton(self.dockCPContents)
        self.btnModifyConnection.setGeometry(QtCore.QRect(80, 120, 80, 25))
        self.btnModifyConnection.setObjectName(_fromUtf8("btnModifyConnection"))
        self.NetworkModifyButtonCallbacks[self.btnModifyConnection] = self.checkDeleteConnections
        self.btnAddConnection = QtGui.QPushButton(self.dockCPContents)
        self.btnAddConnection.setGeometry(QtCore.QRect(40, 90, 80, 25))
        self.btnAddConnection.setObjectName(_fromUtf8("btnAddConnection"))
        self.NetworkModifyButtonCallbacks[self.btnAddConnection] = self.checkAddConnection
        self.btnDeleteConnection = QtGui.QPushButton(self.dockCPContents)
        self.btnDeleteConnection.setGeometry(QtCore.QRect(120, 90, 80, 25))
        self.btnDeleteConnection.setObjectName(_fromUtf8("btnDeleteConnection"))
        self.NetworkModifyButtonCallbacks[self.btnDeleteConnection] = self.checkDeleteConnections
        self.dockConnectionProperties.setWidget(self.dockCPContents)

        # Simulation Controls QDockWidget
        self.dockSimulationControls = QtGui.QDockWidget(self.centralwidget)
        self.dockSimulationControls.setGeometry(QtCore.QRect(580, 355, 225, 150))
        self.dockSimulationControls.setObjectName(_fromUtf8("dockSimulationControls"))
        self.dockSCContents = QtGui.QWidget()
        self.dockSCContents.setObjectName(_fromUtf8("dockSCContents"))
        #TODO this button is not necessary.  start_simulation() should be called immediately on startup.
        self.btnRestart = QtGui.QPushButton(self.dockSCContents)
        self.btnRestart.setGeometry(QtCore.QRect(0, 0, 50, 23))
        self.btnRestart.setObjectName(_fromUtf8("btnRestartButton"))
        self.btnRestart.setDisabled(True)
        self.btnNext = QtGui.QPushButton(self.dockSCContents)
        self.btnNext.setGeometry(QtCore.QRect(55, 0, 50, 23))
        self.btnNext.setObjectName(_fromUtf8("btnNextButton"))
        self.btnPlay = QtGui.QPushButton(self.dockSCContents)
        self.btnPlay.setGeometry(QtCore.QRect(110, 0, 50, 23))
        self.btnPlay.setObjectName(_fromUtf8("btnPlayButton"))
        self.btnPause = QtGui.QPushButton(self.dockSCContents)
        self.btnPause.setGeometry(QtCore.QRect(165, 0, 50, 23))
        self.btnPause.setObjectName(_fromUtf8("btnPauseButton"))
        self.btnClear = QtGui.QPushButton(self.dockSCContents)
        self.btnClear.setGeometry(QtCore.QRect(0, 30, 60, 23))
        self.btnClear.setObjectName(_fromUtf8("btnClearButton"))
        self.btnMsg = QtGui.QPushButton(self.dockSCContents)
        self.btnMsg.setGeometry(QtCore.QRect(0, 60, 60, 23))
        self.btnMsg.setObjectName(_fromUtf8("btnMsgButton"))
        self.btnMicroGUI = QtGui.QPushButton(self.dockSCContents)
        self.btnMicroGUI.setGeometry(QtCore.QRect(0, 90, 60, 23))
        self.btnMsg.setObjectName(_fromUtf8("btnMicroGUIButton"))
        self.updateIntervalSpinner = QtGui.QSpinBox(self.dockSCContents)
        self.lblUpdateInterval = QtGui.QLabel(self.dockSCContents)
        self.lblUpdateInterval.setGeometry(QtCore.QRect(65, 30, 100, 20))
        self.lblUpdateInterval.setObjectName(_fromUtf8("lblUpdateInterval"))
        self.updateIntervalSpinner.setGeometry(QtCore.QRect(170, 30, 50, 20))
        self.updateIntervalSpinner.setObjectName(_fromUtf8("spinnerUpdateInterval"))
        self.updateIntervalSpinner.setRange(0, 1000)
        self.updateIntervalSpinner.setSingleStep(100)
        self.updateIntervalSpinner.setValue(500)
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

        #TODO: Pretty sure this could have been done up top... but whatever.
        # calling functions from buttons here
        QtCore.QObject.connect(self.cboConnectionType, QtCore.SIGNAL(_fromUtf8("activated(int)")), self.decideBandwidth)
        QtCore.QObject.connect(self.btnAddConnection, QtCore.SIGNAL(_fromUtf8("clicked()")), self.addConnection)
        QtCore.QObject.connect(self.btnDeleteConnection, QtCore.SIGNAL(_fromUtf8("clicked()")), self.deleteSelectedConnections)
        QtCore.QObject.connect(self.btnModifyConnection, QtCore.SIGNAL(_fromUtf8("clicked()")), self.modifyConnection)
        QtCore.QObject.connect(self.btnAddNode, QtCore.SIGNAL(_fromUtf8("clicked()")), self.addNode)
        QtCore.QObject.connect(self.btnDeleteNode, QtCore.SIGNAL(_fromUtf8("clicked()")), self.deleteSelectedNodes)
        QtCore.QObject.connect(self.btnModifyNode, QtCore.SIGNAL(_fromUtf8("clicked()")), self.modifyNode)
        QtCore.QObject.connect(self.btnRestart, QtCore.SIGNAL(_fromUtf8("clicked()")), self.restartSimulation)
        QtCore.QObject.connect(self.btnNext, QtCore.SIGNAL(_fromUtf8("clicked()")), self.stepSimulation)
        QtCore.QObject.connect(self.btnPause, QtCore.SIGNAL(_fromUtf8("clicked()")), self.pauseSimulation)
        QtCore.QObject.connect(self.btnPlay, QtCore.SIGNAL(_fromUtf8("clicked()")), self.playSimulation)
        QtCore.QObject.connect(self.btnClear, QtCore.SIGNAL(_fromUtf8("clicked()")), self.clearSimulation)
        QtCore.QObject.connect(self.btnMsg, QtCore.SIGNAL(_fromUtf8("clicked()")),
                               self.openMsgWindow)  # Button to Open MSG window
        QtCore.QObject.connect(self.btnMicroGUI, QtCore.SIGNAL(_fromUtf8("clicked()")),
                               self.openMicroGUI)  # Button to Open MSG window
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
        self.btnRestart.setText(_translate("MainWindow", "Restart", None))
        self.btnNext.setText(_translate("MainWindow", "Next", None))
        self.btnPlay.setText(_translate("MainWindow", "Play", None))
        self.btnPause.setText(_translate("MainWindow", "Pause", None))
        self.btnClear.setText(_translate("MainWindow", "Clear", None))
        self.lblUpdateInterval.setText(_translate("MainWindow", "Update Interval (ms)", None))
        self.dockSimulationControls.setWindowTitle(_translate("MainWindow", "Simulation Controls", None))
        self.btnMsg.setText(_translate("MainWindow", "Messages", None))
        self.btnMicroGUI.setText(_translate("MainWindow", "Micro View", None))
        #Added so I don't have to click the start button EVERY time I want to test something.
        self.clearSimulation()

    # I cannot figure out how to put these calls elsewhere yet so will need to copy each time .ui file is recreated

    def initializeWidgets(self):
        self.decideBandwidth()
        self.cboConnectionType.addItems(['Coax', 'Fibre', 'Custom'])
        self.cboNodeType.addItems(['Host', 'Router', 'Switch'])

        self.txtConnectionBandwidth.setPlainText(`2`)
        self.txtConnectionLength.setPlainText(`2`)

    def decideBandwidth(self):
        if self.cboConnectionType.currentText() == "Custom":
            self.lblConnectionBandwidth.show()
            self.txtConnectionBandwidth.show()
        else:
            self.lblConnectionBandwidth.hide()
            self.txtConnectionBandwidth.hide()

    def addNode(self):
        # Create the GUI node
        thisNode = Node(self.cboNodeType.currentText(), self.txtXPos.toPlainText(), self.txtYPos.toPlainText())
        self.nodes[thisNode.getIDInt()] = thisNode
        self.placeNodeGraphic(thisNode)

        # Create the simulation node
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
            # remove node from nodes dictionary
            self.nodes.pop(node_id)
            # remove node from selectedNodes dictionary
            self.selectedNodes.pop(node_id)
            # remove the corresponding simulation node (incorporates deletion of simulation connection)
            src.Network.network.remove_node(node_id)
            # remove any connections that involved this node.
            for connection in self.connections:
                if connection.__contains__(node_id): self.connections.remove(connection)

        self.clearAndRepaint()

    def isNodeSelected(self, node):
        if self.selectedNodes.get(node.getIDInt(), False): return True
        else: return False

    def checkModifyNode(self):
        if len(self.selectedNodes) == 1: self.btnModifyNode.setEnabled(True)
        else: self.btnModifyNode.setEnabled(False)

    def checkDeleteNodes(self):
        if len(self.selectedNodes) > 0: self.btnDeleteNode.setEnabled(True)
        else: self.btnDeleteNode.setEnabled(False)

    def modifyNode(self):
        #Checking of whether node modification is allowed is handled by enabling/disabling btnModifyNode.
        #(called from NodeLabel.mousePressedEvent())
        #This method should not be called other than by the pressing of said button.

        #"Modify" GUI node (Remove old node and create new one with the new characteristics.  Necessary because
        #                 simulation nodes must be handled this way, and therefore so too must GUI nodes
        #                 otherwise their id's will no longer match.)
        self.deleteSelectedNodes()
        self.addNode()

        self.clearAndRepaint()

    def addConnection(self):
        # This function will only be called if exactly two nodes are selected when the add connection button is pressed.
        selectedNodes = self.selectedNodes.values()

        gnode1 = selectedNodes[0]
        gnode2 = selectedNodes[1]
        simNode1 = src.Network.network.nodes[gnode1.getIDInt()]
        simNode2 = src.Network.network.nodes[gnode2.getIDInt()]

        #Add simulation connection
        simNodes = src.Network.network.nodes

        #create the connection
        simConnection = SimulationConnection.Connection(self.cboConnectionType.currentText(),
                                       int(self.txtConnectionLength.toPlainText()))
        #connect it to interfaces in each node.
        simConnection.connect_nodes(simNode1, simNode2)

        src.Network.network.add_connection(gnode1.getIDInt(), gnode2.getIDInt(), simConnection)

        #Add GUI connection
        nodeTuple = src.Network.network.get_node_pair_id(gnode1.getIDInt(), gnode2.getIDInt())
        self.connections.append(nodeTuple)
        self.placeConnectionGraphic(simConnection.connection_id, simConnection.connectionType, gnode1, gnode2)

        # Recompute routing tables to account for new connection
        try:
            self.recomputeRoutingTables()
        except Exception:
            print "recomputeRoutingTables is whining."

    def deleteSelectedConnections(self):
        for connection in self.selectedConnections:
            # remove GUI connection
            self.connections.remove(connection)
            # remove simulation connection
            src.Network.network.remove_connection(connection[0], connection[1])
        try:
            self.recomputeRoutingTables()
        except Exception:
            print "recomputeRoutingTables() is whining"

        # Remove all selected connection GUI elements.
        self.selectedConnections = []
        self.clearAndRepaint()

    def modifyConnection(self):
        #Checking of whether connection modification is allowed is handled by enabling/disabling btnModifyConnection.
        #(called from NetworkConnection.mousePressedEvent())
        #This method should not be called other than by the pressing of said button.
        #"Modify" Connection (Remove old node and create new one with the new characteristics.  Necessary because
        #                 simulation nodes must be handled this way, and therefore so too must GUI nodes
        #                 otherwise their id's will no longer match.)
        #TODO This sort of nonsense is a good case for consolidating the two nodes into a single class. Consider it.

        print"modifyConnection()"
        node_ids = self.selectedConnections[0]
        # Keep track of whether the end nodes were selected or not so the same nodes are selected before and after.
        selectedFlags = {}

        # get nodes at either end of connection and add to selected nodes so that addConnection will work.

        for node in node_ids:
            if node in self.selectedNodes: selectedFlags[node] = True
            else: selectedFlags[node] = False

            self.selectedNodes[node] = self.nodes[node]

        self.deleteSelectedConnections()
        self.addConnection()

        # remove the nodes from the selected nodes list to regain consistency with GUI.
        for node in node_ids:
            if selectedFlags[node]: self.selectedNodes[node] = self.nodes[node]
            else: del(self.selectedNodes[node])

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

    def clearAndRepaint(self):
        while self.frameMain.children():
            child = self.frameMain.children()[0]
            child.setParent(None)  # Immediately removes child from children list of parent
            child.deleteLater()  # Don't care when this happens.  Want to avoid sip.delete() hangups.
            # sip.delete(self.frameMain.children()[0])
            # sip.delete() hangs up sometimes for unknown reason.
            # Node number and deletion order dependent.  Highly reproducible.
        self.rebuildFrameMainGraphics()

    def rebuildFrameMainGraphics(self):

        for x in self.nodes.keys():
            self.placeNodeGraphic(self.nodes[x])

        for node1ID,node2ID in self.connections:
            connection = src.Network.network.get_connection(node1ID, node2ID)
            self.placeConnectionGraphic(connection.connection_id, connection.connectionType,
                                        self.nodes[node1ID], self.nodes[node2ID])

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

    def placeNodeGraphic(self, aNode):

        nodePosition = aNode.getLocation()
        x1 = int(nodePosition[0])
        y1 = int(nodePosition[1])

        self.lblNode = NodeLabel(self.frameMain)
        self.lblNode.setUIMainWindow(self)
        self.lblNode.setMainWindow(self.thisMainWindow)
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

    def enableNetworkModification(self):
        for button, callback in self.NetworkModifyButtonCallbacks.iteritems():
            if callback is None: button.setEnabled(True)
            else: callback()

    def disableNetworkModification(self):
        for button in self.NetworkModifyButtonCallbacks.keys():
            button.setDisabled(True)

    def traceNetwork(self):
        if(not self.network_traced):
            trace = src.Network.trace

            nodes = self.nodes.values()

            for node in nodes:
                location = node.getLocation()
                trace.write('Node:id:%d type:%s XPos:%s YPos:%s\n'%\
                            (node.getIDInt(), node.getType(), location[0], location[1]))

            for id, conn in src.Network.network.connections.iteritems():
                trace.write('Conn:id:%s type:%s node:%d node:%d\n'%\
                            (conn.connection_id, conn.connectionType, id[0], id[1]))

            self.network_traced = True

    def clearSimulation(self):
        print "clearSimulation"
        self.network_traced = False
        src.Network.trace_init()
        if not self.simulation_started:
            self.simulation_started = True

        src.Network.network_init()
        self.nodes = {}
        self.selectedNodes = {}
        self.connections = []
        self.selectedConnections = []

        # This is for the GUI Node, do not delete it again!
        Node.static_id = 0

        self.pauseSimulation()
        self.clearAndRepaint()

        self.enableNetworkModification()

    def restartSimulation(self):
        print "startSimulation"
        self.network_traced = False
        src.Network.trace_init()
        if not self.simulation_started:
            self.simulation_started = True

        self.selectedNodes = {}
        self.selectedConnections = []
        self.pauseSimulation()
        self.clearAndRepaint()

        self.enableNetworkModification()

    def stepSimulation(self):
        print "stepSimulation"
        self.disableNetworkModification()
        self.traceNetwork()
        if self.simulation_started and self.simulation_paused:
            # time.sleep() accepts time in seconds.  Spinner displays in ms.
            interval = float(self.updateIntervalSpinner.value()) / 1000.0
            self.simulation_thread = SimulationLoop.start_simulation(src.Network.network, src.Network.env.run,
                                                                     updateInterval=interval,
                                                                     numLoops = 1)

    def playSimulation(self):
        print "playSimulation"

        self.disableNetworkModification()
        self.btnClear.setDisabled(True)

        self.traceNetwork()

        self.simulation_paused = False
        #time.sleep() accepts time in seconds.  Spinner displays in ms.
        interval = float(self.updateIntervalSpinner.value()) / 1000.0
        self.simulation_thread = SimulationLoop.start_simulation(src.Network.network, src.Network.env.run,
                                                                 updateInterval = interval)

    def pauseSimulation(self):
        print"pauseSimulation"
        self.simulation_paused = True

        if(self.simulation_thread != None):
            self.simulation_thread.end()

        self.btnClear.setEnabled(True)


    def recomputeRoutingTables(self):
        # compute routing tables for each router and host
        tables = routingTableAlgorithm.routingTables(src.Network.network)

        # insert routing tables into the nodes
        for node in src.Network.network.nodes.values():
            if isinstance(node, src.Node.Router):
                node.routing_table = tables[node]

    def openMsgWindow(self):  # Method to open button window
        self.MsgWindow = SendMessage_Window(self.MsgTemplate)
        QtCore.QObject.connect(self.btnDeleteConnection, QtCore.SIGNAL(_fromUtf8("clicked()")),
                               self.MsgWindow.refreshDropdowns)
        QtCore.QObject.connect(self.btnAddConnection, QtCore.SIGNAL(_fromUtf8("clicked()")),
                               self.MsgWindow.refreshDropdowns)
    def openMicroGUI(self):
        #sn = self.selectedNodes
        sc = self.selectedConnections
        conn = src.Network.network.connections
        # if len(sn) == 2:
        #     self.MicroWindow = MicroMainWindow(self.thisMainWindow, sn[0], sn[1])
        # elif len(sn) == 3:
        #     self.MicroWindow = MicroMainWindow(self.thisMainWindow, sn[0], sn[1], sn[2])
        # elif len(sn) == 4:
        #     self.MicroWindow = MicroMainWindow(self.thisMainWindow, sn[0], sn[1], sn[2], sn[3])
        if len(sc) == 1:
            self.MicroWindow = MicroMainWindow(self.thisMainWindow, conn[sc[0]])
        elif len(sc) == 2:
            self.MicroWindow = MicroMainWindow(self.thisMainWindow, conn[sc[0]], conn[sc[1]])
        elif len(sc) == 3:
            self.MicroWindow = MicroMainWindow(self.thisMainWindow, conn[sc[0]], conn[sc[1]], conn[sc[2]])

        QtCore.QObject.connect(self.btnDeleteNode, QtCore.SIGNAL(_fromUtf8("clicked()")),
                               self.MicroWindow.updateState)


class NodeLabel(QtGui.QLabel):

    # Warning: This class has a secret variable called nodeObject which references the simulation node to which
    # this label corresponds.

    def setMainWindow(self, mainWindow):
        # This is the QWidget which is the parent for the TableWindow associated with this node.
        self.mainWindow = mainWindow

    def setUIMainWindow(self, mw):
        # This is the UI_MainWindow object that displays all the UI stuff.
        self.UImainWindow = mw

    def mouseDoubleClickEvent(self, ev):
        self.mousePressEvent(ev)
        self.window = TableWindow(QtGui.QMainWindow(self.mainWindow), self.nodeObject)

    def mousePressEvent(self, ev):
        # TODO add Shift + Click for multiple selection

        if self.UImainWindow.isNodeSelected(self.nodeObject):
            self.UImainWindow.selectedNodes.pop(self.nodeObject.getIDInt())
        else:
            self.UImainWindow.selectedNodes[self.nodeObject.getIDInt()] = self.nodeObject

        self.highlightSelected()

        self.UImainWindow.checkModifyNode()
        self.UImainWindow.checkDeleteNodes()
        self.UImainWindow.checkModifyConnection()
        self.UImainWindow.checkAddConnection()


    def highlightSelected(self):
        if self.UImainWindow.isNodeSelected(self.nodeObject):
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

    # TODO remove???
    # def getLatency(self):
    #     #TODO make this actually correct should probably talk to simulation connection
    #     #Probably calculate from length and type
    #     return 100
    #
    # def getBandwidth(self):
    #     #TODO make this actually correct should probably talk to simulation connection
    #     #Max bandwidth probably determined by type.
    #     return 200

    def mousePressEvent(self, ev):
        # TODO add Shift + Click for multiple selection

        if self.mainWindow.isConnectionSelected(self.nodeTuple):
            self.mainWindow.selectedConnections.remove(self.nodeTuple)
        else:
            self.mainWindow.selectedConnections.append(self.nodeTuple)

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
            elif connection.connectionType == "Fibre":
                vertical.setStyleSheet(_fromUtf8("color:" + "red"))
                horizontal.setStyleSheet(_fromUtf8("color:" + "red"))
            else:
                vertical.setStyleSheet(_fromUtf8("color:" + "green"))
                horizontal.setStyleSheet(_fromUtf8("color:" + "green"))

