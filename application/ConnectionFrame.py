
from tkinter import * 
from tkinter import ttk
import tkinter as tk
from repository.BoardSetupHandler import BoardSetupHandler
from serial.tools.list_ports_common import *
import threading
from threading import Event
from queue import Empty
from repository.BoardSetupHandler import *
from repository.BoardInteractor import *
from repository.appState import AppState
from repository.listeners.BoardConnectionListener import ConnectionState, ConnectionStateListener
from application.subframe.ExcelFrame import ExcelFrame
## This will create the tkinter ui for the controls tab. 
# the controls tab includes connecting to the arduino
# and modifying the sensor values.
TAG = "[ConnectionFrame]\t"
class ConnectionFrame:
    def __init__(self, tab:Frame, boardSetupHandler, appState:AppState):
        self.appState = appState

        print(f"{TAG} adding onConnectListener")

        self.appState.onConnectListener.onConnectedCallbacks.append(self.doOnConnect) # There is a race condition between initializing callbacks. 
        self.appState.onConnectListener.onDisconnectedCallbacks.append(self.doOnDisconnect)

        self.controls_tab = tab
        self.boardSetterUpper:BoardSetupHandler = boardSetupHandler
        self.selectedPort = tk.StringVar()
        self.connectionMessage = tk.StringVar()
        self.triggerValue = tk.DoubleVar()
        self.boardSetup = threading.Event() # This is the local event which will trigger the parent event.
        self.isConnected = tk.BooleanVar()

        self.boardInteractor:BoardInteractor = None

        self.ports = self.boardSetterUpper.getAllPortNamesAndDevices()
        self.setupConnectFrame()

        excel_tab = LabelFrame(self.controls_tab,text="Excel Setup", bg="#F8F8F8")
        excel_tab.pack(padx=20,pady=20,fill="x")
        # IF THIS IS CALLED BEFORE CONNECTIONLISTENER THERE WILL BE A RACE CONDITION! 
        excel_frame = ExcelFrame(excel_tab,appState=appState)



    def doOnConnect(self):
        print(f"{TAG} doOnConnect ")
        self.lightCanvas.itemconfig(self.greenLight,fill="green")
        self.connectionMessage.set("Arduino Connected.")
        self.connectionLabel.update_idletasks()
        ## Setup board interactor , apply callbacks to trigger board setup events. 
        self.boardInteractor = BoardInteractor(self.boardSetterUpper.board) 
        print("BEN -> boardInteracter created and registered.")
        self.appState.dependencyInjection.register("BI",self.boardInteractor,tag=TAG)
        print(f"{TAG}board setup. (Interactor Created.)")
            
    def doOnDisconnect(self):
        self.lightCanvas.itemconfig(self.greenLight,fill="red")
        self.connectionMessage.set("Arduino Connection Failed.\n Please make sure arduino is connected or try refreshing port list.")
        self.connectionLabel.update_idletasks()
        self.boardSetup.clear()
    

    def refreshPortList(self):
        self.ports = self.boardSetterUpper.getAllPortNamesAndDevices()
        self.selectedPort.set(self.boardSetterUpper.ArduinoPort)
        print(f"{TAG}Selected Port: "+self.selectedPort.get())
        self.combo.config(values = self.ports, textvariable=self.selectedPort)

        self.setConnectionState( self.boardSetterUpper.isConnected )

        if self.isConnected.get(): ## This shouldn't happen...
            self.connectionMessage.set("Arduino Connected.")
            self.connectionLabel.update_idletasks()
            self.boardSetup.set()
            
        else:
            self.lightCanvas.itemconfig(self.greenLight,fill="grey")
            self.connectionMessage.set("Arduino not connected")
            self.connectionLabel.update_idletasks()
            self.boardSetup.clear()

    # The ultimate connection state. This is where things the state is actually set from. 
    def connect(self):
        print(f"{TAG}connecting")
        map = self.boardSetterUpper.getAllPortsMap()
        value = map.get( self.selectedPort.get())
        self.connectionMessage.set("Connecting... Please wait")
        self.connectionLabel.update_idletasks()
        self.setConnectionState( self.boardSetterUpper.connect(value) )
        self.appState.onConnectListener.source.on_next( ConnectionState.CONNECTED if self.isConnected.get() else ConnectionState.DISCONNECTED )

    def setupConnectFrame(self):
        print(f"{TAG}Creating connection frame")
        # Subframe inside Controls tab
        self.connection_frame = tk.LabelFrame(self.controls_tab,text="Arduino Connection" ,bg="#E0E0E0")
        self.connection_frame.pack(padx=20, pady=20)
        tk.Label(self.connection_frame, text="Select COM PORT").grid(row=0, column=0, padx=5, pady=5)

        # Dropdown menu for selecting the com port for the arduino:
        self.combo = ttk.Combobox(self.connection_frame, values=self.ports, state="readonly", textvariable=self.selectedPort, width=45)
        self.combo.grid(row=0,column=1,columnspan=3)
        self.selectedPort.set(self.boardSetterUpper.ArduinoPort)

        # Connection indicator light
        self.lightCanvas:Canvas = tk.Canvas(self.connection_frame, width=100, height=50, bg="#E0E0E0", highlightthickness=0)
        self.lightCanvas.grid(row=1,column=1)
        self.greenLight = self.lightCanvas.create_oval(25, 10, 55, 40, fill="gray", outline="black",)
        self.connectionMessage.set("Arduino not connected")
        self.connectionLabel = tk.Label(self.connection_frame,textvariable=self.connectionMessage)
        self.connectionLabel.grid(row =1, column=2)

        tk.Button(self.connection_frame, text="Connect",command=self.connect).grid(row=1, column=0, pady=10)
        tk.Button(self.connection_frame, text="Refresh List",command=self.refreshPortList).grid(row=2, column=0, pady=10)
    
        #Begin collecting data

    def setConnectionState(self, connectionState:bool):
            self.isConnected.set(connectionState)

    def getFrame(self):
        return self.connection_frame
