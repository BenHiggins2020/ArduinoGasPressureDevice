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
        self.lf.grid(column=0,sticky="nsew",row=0, pady=10,padx=10)

        self.connectBtn = tk.Button(self.lf,text="Connect to Spreadsheet")
        self.connectBtn.grid(column=0,row=1,columnspan=2, padx=5,pady=5)
        self.connectBtn.config(state="disabled")

        self.lightCanvas:Canvas = tk.Canvas(self.lf, width=100, height=50, highlightthickness=0)
        self.lightCanvas.grid(row=1,column=3)
        self.lighIndicator = self.lightCanvas.create_oval(25, 10, 55, 40, fill="gray", outline="black",)

        self.saveBtn = tk.Button(self.lf,text="Save")
        self.saveBtn.grid(column=1,row=4,padx=5,pady=5)
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

        print("adding callbacks to list! ")
        appState.addBoardSetupListener(self.inject)
        appState.addBoardSetupListener(self.setupExcelButton)

    # This set after board is setup (through threading Event flag)
    def setInteractor(self,boardInteractor:BoardInteractor):
        self.dataHandler = DataHandler(boardInteractor,self.appState)

    def inject(self):
        self.interactor = self.appState.injectBoardInteractor()
        self.setInteractor(self.interactor)

    def setupExcelButton(self):
        self.connectBtn.config(state="active",command=self.dataHandler.connect)
        self.saveBtn.config(state="active",command=self.dataHandler.save)
        self.stopStream.config(state="active",command=self.dataHandler.stopStream)
        self.startStream.config(state="active",command=self.dataHandler.startStream)

        # self.entry.config(state="active",textvariable=self.interval)
        self.selfSaveIntervalBtn.config(state="normal",command=self.setSaveInterval)

    
    def setSaveInterval(self):
        self.dataHandler.setSaveInterval(self.interval.get())

    def close(self):
        print("Closing Excel Frame...")
        if self.dataHandler:
            self.dataHandler.shouldSavePeriodically = False
            self.dataHandler.save()
            self.dataHandler.workbook.close()

        
         