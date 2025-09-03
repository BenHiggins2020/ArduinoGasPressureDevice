
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
from application.subframe.ExcelFrame import ExcelFrame
## This will create the tkinter ui for the controls tab. 
# the controls tab includes connecting to the arduino
# and modifying the sensor values.
class ConnectionFrame:
    def __init__(self, tab:Frame, boardSetupHandler, appState:AppState):
        self.appState = appState        
        self.controls_tab = tab
        self.boardSetterUpper:BoardSetupHandler = boardSetupHandler
        self.selectedPort = tk.StringVar()
        self.connectionMessage = tk.StringVar()
        self.triggerValue = tk.DoubleVar()
        self.boardSetup = threading.Event() # This is the local event which will trigger the parent event.
        self.isConnected = tk.BooleanVar()
        # self.isConnected = isConnectedEvent
        self.boardInteractor:BoardInteractor = None
        self.ports = self.boardSetterUpper.getAllPortNamesAndDevices()
        self.createConnectionSubFrame()

        excel_tab = LabelFrame(self.controls_tab,text="Excel Setup", bg="#F8F8F8")
        excel_tab.pack(padx=20,pady=20,fill="x")
        excel_frame = ExcelFrame(excel_tab,appState=appState)

        

    def createConnectionSubFrame(self):
        print("Creating connection frame")
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

        def connect():
            print("connect")
            map = self.boardSetterUpper.getAllPortsMap()
            port = self.selectedPort.get()
            print(f"port selected = {port} ")
            value = map.get( self.selectedPort.get())
            print(f"value = {value} ")

            self.connectionMessage.set("Connecting... Please wait")
            self.connectionLabel.update_idletasks()
            self.setConnectionState( self.boardSetterUpper.connect(value) )
            
            if self.isConnected.get():   
                self.lightCanvas.itemconfig(self.greenLight,fill="green")
                self.connectionMessage.set("Arduino Connected.")
                self.connectionLabel.update_idletasks()

                self.beginDataCollectionBtn.config(state="active")

                ## Setup board interactor , apply callbacks to trigger board setup events. 
                self.boardInteractor = BoardInteractor(self.boardSetterUpper.board) 
                self.appState.setBoardInteractor(self.boardInteractor)
                print("board setup. invoking callbacks...")
                self.appState.invokeBoardSetupCallbacks()

            else:
                self.lightCanvas.itemconfig(self.greenLight,fill="red")
                self.connectionMessage.set("Arduino Connection Failed.\n Please make sure arduino is connected or try refreshing port list.")
                self.connectionLabel.update_idletasks()
                self.boardSetup.clear()

        def refreshPortList():
            self.ports = self.boardSetterUpper.getAllPortNamesAndDevices()
            self.selectedPort.set(self.boardSetterUpper.ArduinoPort)
            print("Selected Port: "+self.selectedPort.get())
            self.combo.config(values = self.ports, textvariable=self.selectedPort)

            self.setConnectionState( self.boardSetterUpper.isConnected )

            if self.isConnected.get(): ## This shouldn't happen...
                self.connectionMessage.set("Arduino Connected.")
                self.connectionLabel.update_idletasks()
                self.boardSetup.set()
               
            else:
                self.lightCanvas.itemconfig(self.greenLight,fill="grey")
                self.beginDataCollectionBtn.config(state="disabled")
                self.connectionMessage.set("Arduino not connected")
                self.connectionLabel.update_idletasks()
                self.boardSetup.clear()

        ## TODO: Move this to board interactor or data Handler. 
        def beginDataCollection():
            try:
                if self.isConnected.get():
                    self.boardInteractor.running = True
                    dataCollectionThread = threading.Thread(target=self.boardInteractor.run, daemon=True)
                    dataCollectionThread.start()
                else:
                    print("Failed to start data collection. ")
            except Exception as E:
                print("Failed to begin data collection: "+str(E))

        self.beginDataCollectionBtn = tk.Button(self.connection_frame,text="begin data collection",command=beginDataCollection, state="disabled")
        self.beginDataCollectionBtn.grid(row=3,column=1,padx=5,pady=5)


        tk.Button(self.connection_frame, text="Connect",command=connect).grid(row=1, column=0, pady=10)
        tk.Button(self.connection_frame, text="Refresh List",command=refreshPortList).grid(row=2, column=0, pady=10)
    
        #Begin collecting data

    def setConnectionState(self, connectionState:bool):
            self.isConnected.set(connectionState)

    def getFrame(self):
        return self.connection_frame
