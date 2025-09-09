from tkinter import * 
from tkinter import ttk
from tkinter import font
import tkinter as tk
from repository.BoardSetupHandler import BoardSetupHandler
from repository.appState import AppState
from serial.tools.list_ports_common import *
import threading
from threading import Event
from repository.BoardSetupHandler import *
from repository.BoardInteractor import *
from repository.DataHandler import DataHandler
from reactivex.observer import Observer
from repository.listeners.BoardConnectionListener import *

TAG = "[ExcelFrame]\t"
class ExcelFrame:
    interactor:BoardInteractor = None
    dataHandler:DataHandler = None
    def __init__(self, frame:Frame,appState:AppState):
        self.excel_tab = frame
        self.appState = appState
        self.interval = tk.IntVar()

        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)
        self.lf = Frame(frame,bg="#E0E0E0",relief="groove",borderwidth=2)
        self.setupUi()

        # There is an race condition between excel frame and ConnectionFrame
        print(f"{TAG} adding onConnectListener")
        self.appState.onConnectListener.addOnConnectedListener(self.setupExcelButton)


    # This set after board is setup (through threading Event flag)
    def setupDataHandler(self,boardInteractor:BoardInteractor):
        self.dataHandler = DataHandler(boardInteractor,self.appState)

    def resolveBoardInteractor(self,depednecy:BoardInteractor):
        self.interactor = self.appState.dependencyInjection.resolve("BI",tag=TAG)
        self.dataHandler = DataHandler(self.interactor,self.appState)
        self.appState.dependencyInjection.register("DataHandler",self.dataHandler,tag=TAG)
        # self.setInteractor(self.interactor)

    def setupExcelButton(self):
        self.connectBtn.config(state="active")
        self.saveBtn.config(state="active")
        self.stopStream.config(state="active")
        self.startStream.config(state="active")
        self.selfSaveIntervalBtn.config(state="normal",command=self.setSaveInterval)

        interactor:BoardInteractor = self.appState.dependencyInjection.resolve("BI",tag=TAG)
        self.dataHandler = DataHandler(interactor,self.appState)

        self.connectBtn.config(command=self.dataHandler.connect)
        self.saveBtn.config(command=self.dataHandler.save)
        self.stopStream.config(command=self.dataHandler.stopStream)
        self.startStream.config(command=self.dataHandler.startStream)


        # self.entry.config(state="active",textvariable=self.interval)

    
    def setSaveInterval(self):
        self.dataHandler.setSaveInterval(self.interval.get())

    def close(self):
        print("Closing Excel Frame...")
        if self.dataHandler:
            self.dataHandler.close()
           

    def setupUi(self):  
        self.lf.grid(column=0,sticky="nsew",row=0, pady=10,padx=10)

        self.connectBtn = tk.Button(self.lf,text="Connect to Spreadsheet")
        self.connectBtn.grid(column=0,row=1,columnspan=2, padx=5,pady=5)
        self.connectBtn.config(state="disabled")

        self.lightCanvas:Canvas = tk.Canvas(self.lf, width=100, height=50, highlightthickness=0)
        self.lightCanvas.grid(row=1,column=3)
        self.lighIndicator = self.lightCanvas.create_oval(25, 10, 55, 40, fill="gray", outline="black",)

        self.saveBtn = tk.Button(self.lf,text="Save")
        self.saveBtn.grid(column=0,row=5,padx=5,pady=5)
        self.saveBtn.config(state="disabled")

        self.startStream = tk.Button(self.lf,text="Start Stream")
        self.startStream.grid(column=0,row=3,padx=5,pady=5)
        self.startStream.config(state="disabled")

        self.stopStream = tk.Button(self.lf,text="Stop Stream")
        self.stopStream.grid(column=1,row=3,padx=5,pady=5)
        self.stopStream.config(state="disabled")

        tk.Label(self.lf,text="Set Auto-Save Interval (s)").grid(column=0,row=4,columnspan=2,padx=5,pady=5)

        self.entry = tk.Entry(self.lf,bg="lightgrey",textvariable=self.interval)
        self.entry.grid(column=3,row=4,columnspan=2,padx=5,pady=5)


        self.selfSaveIntervalBtn = tk.Button(self.lf,text="Set Save Interval")
        self.selfSaveIntervalBtn.grid(column=0,row=5,columnspan=4,padx=5,pady=5)
        self.selfSaveIntervalBtn.config(state="disabled")
        
         