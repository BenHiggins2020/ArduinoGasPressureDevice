
from tkinter import * 
from tkinter import ttk
import tkinter as tk
from repository.BoardSetupHandler import BoardSetupHandler
from serial.tools.list_ports_common import *
import threading
from repository.BoardSetupHandler import *
from repository.BoardInteractor import *

## This will create the tkinter ui for the controls tab. 
# the controls tab includes connecting to the arduino
# and modifying the sensor values.
class SetupFrame:
    def __init__(self, tab:Frame, boardSetupHandler):
        self.controls_tab = tab
        self.boardSetterUpper:BoardSetupHandler = boardSetupHandler
        self.selectedPort = tk.StringVar()
        self.connectionMessage = tk.StringVar()
        self.triggerValue = tk.DoubleVar()
        # self.isConnected = tk.BooleanVar()
        self.isConnected = False
        self.boardInteractor:BoardInteractor = None

        self.ports = self.boardSetterUpper.getAllPortNamesAndDevices()
        self.createConnectionSubFrame()
        self.createArduinoControllerFrame()

        

    def createConnectionSubFrame(self):
        print("Creating connection frame")
        # Subframe inside Controls tab
        self.connection_frame = tk.Frame(self.controls_tab, bg="#E0E0E0")
        self.connection_frame.pack(padx=20, pady=20)
        tk.Label(self.connection_frame, text="Select COM PORT").grid(row=0, column=0, padx=5, pady=5)

        # Dropdown menu for selecting the com port for the arduino:
        self.combo = ttk.Combobox(self.connection_frame, values=self.ports, state="readonly", textvariable=self.selectedPort, width=45)
        self.combo.grid(row=0,column=1,columnspan=3)
        self.selectedPort.set(self.boardSetterUpper.ArduinoPort)


        ##Connection indicator light
        self.lightCanvas:Canvas = tk.Canvas(self.connection_frame, width=100, height=50, bg="#E0E0E0", highlightthickness=0)
        self.lightCanvas.grid(row=1,column=1)
        self.greenLight = self.lightCanvas.create_oval(25, 10, 55, 40, fill="gray", outline="black",)
        self.connectionMessage.set("Arduino not connected")
        self.connectionLabel = tk.Label(self.connection_frame,textvariable=self.connectionMessage)
        self.connectionLabel.grid(row =1, column=2)

        def connect():
            print("connect")
            map = self.boardSetterUpper.portMap
            value = map.get( self.selectedPort.get())
            print(f"value = {value} ")
            self.connectionMessage.set("Connecting... Please wait")
            self.connectionLabel.update_idletasks()
            self.isConnected = self.boardSetterUpper.connect(value)
            
            if self.isConnected:   
                self.lightCanvas.itemconfig(self.greenLight,fill="green")
                # self.connection_frame.config(self.connectionLabel,text="Arduino Connected.")
                
                # self.boardInteractor = BoardInteractor(self.boardSetterUpper.board) 
                self.connectionMessage.set("Arduino Connected.")
                self.connectionLabel.update_idletasks()
                self.submitBtn.config(state="active")
                self.beginDataCollectionBtn.config(state="active")
                self.printDataBtn.config(state="active")
                self.boardInteractor = BoardInteractor(self.boardSetterUpper.board) 


            else:
                self.lightCanvas.itemconfig(self.greenLight,fill="red")
                self.connectionMessage.set("Arduino Connection Failed.\n Please make sure arduino is connected or try refreshing port list.")
                self.connectionLabel.update_idletasks()

        def refreshPortList():
            self.ports = self.boardSetterUpper.getAllPortNamesAndDevices()
            self.selectedPort.set(self.boardSetterUpper.ArduinoPort)
            # self.combo.config(values = self.ports,textvariable=self.selectedPort)
            self.combo = ttk.Combobox(self.connection_frame, values=self.ports, state="readonly", textvariable=self.selectedPort, width=45)
            self.combo.grid(row=0,column=1,columnspan=3)

            self.isConnected = self.boardSetterUpper.isConnected

            if self.isConnected:   
                # self.lightCanvas.itemconfig(self.greenLight,fill="green")
                # self.connection_frame.config(self.connectionLabel,text="Arduino Connected.")
                
                self.connectionMessage.set("Arduino Connected.")
                self.connectionLabel.update_idletasks()
               
            else:
                self.lightCanvas.itemconfig(self.greenLight,fill="grey")
                self.submitBtn.config(state="disabled")
                self.beginDataCollectionBtn.config(state="disabled")
                self.printDataBtn.config(state="disabled")

                self.connectionMessage.set("Arduino not connected")
                self.connectionLabel.update_idletasks()


        tk.Button(self.connection_frame, text="Connect",command=connect).grid(row=1, column=0, pady=10)
        tk.Button(self.connection_frame, text="Refresh List",command=refreshPortList).grid(row=2, column=0, pady=10)
    

    def createArduinoControllerFrame(self):
        print("Creating Arduino frame")

        self.dataVar = tk.StringVar()
        self.dataVar.set("Press \"Begin Data Collection\" to start reading ")

        self.arduino_controller = tk.LabelFrame(self.controls_tab, bg="#8A9A5B",text="Arduino Controls")
        self.arduino_controller.pack(padx=20,pady=20)
        # tk.Label(self.arduino_controller,text="Arduino Controls").grid(row=0,column=0,padx=10,pady=5)

        lf = tk.Label(self.arduino_controller, text="Threshold Value")
        lf.grid(row=2,column=0,padx=5,pady=5)

        entry = tk.Entry(self.arduino_controller,bg="lightgrey",textvariable=self.triggerValue)
        entry.grid(row=2,column=1,padx=5,pady=5)

        if self.isConnected:
            self.boardInteractor = BoardInteractor(self.boardSetterUpper.board)

        def submit():
            try:
                if self.isConnected:
                    value = float(self.triggerValue.get())
                    self.boardInteractor.setThreshold(value)
                else:
                    print("Could not set threshold because board is not connected.")
            except Exception as E:
                print("Failed to set threshold. "+E.with_traceback)

        def recurringcall():
            while True:
                data = self.boardInteractor.getData()
                value = data.get_nowait()
                self.dataValue.config(text=value)
                print(f"data = {value}")

        def pullDataQueue():
           threading.Thread(target=recurringcall,daemon=True).start()

        def beginDataCollection():
            try:
                if self.isConnected:
                    self.boardInteractor.running = True
                    dataCollectionThread = threading.Thread(target=self.boardInteractor.run, daemon=True)
                    dataCollectionThread.start()
                else:
                    print("Failed to start data collection. ")
            except Exception as E:
                print("Failed to begin data collection: "+E.with_traceback)

        # self.currentDataValue = tk.LabelFrame(self.arduino_controller,text="Current Sensor Reading",bg="#C5CBA4")
        self.currentDataValue = tk.LabelFrame(self.arduino_controller, bg="#C5CBA4",text="Current Sensor Reading")
        self.currentDataValue.grid(row=3, column=0, columnspan=2)

        self.dataValue= tk.Label(self.currentDataValue,text="Please select begin data collection and output data. ")
        self.dataValue.grid(row=0, column=0,padx=5,pady=5)

        self.submitBtn = tk.Button(self.arduino_controller,text="submit",command=submit, state="disabled")
        self.submitBtn.grid(row=2,column=2,padx=5,pady=5)

        self.beginDataCollectionBtn = tk.Button(self.arduino_controller,text="begin data collection",command=beginDataCollection, state="disabled")
        self.beginDataCollectionBtn.grid(row=3,column=2,padx=5,pady=5)

        self.printDataBtn = tk.Button(self.arduino_controller,text="output data",command=pullDataQueue, state="disabled")
        self.printDataBtn.grid(row=4,column=2,padx=5,pady=5)
        #Start program the board
      


        #Begin collecting data

    def getFrame(self):
        return self.connection_frame
