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

        self.lf = LabelFrame(frame,text="Run ExcelSheet. ")
        self.lf.grid(column=0,columnspan=5,row=0,padx=10,pady=10)

        self.runBtn = tk.Button(self.lf,text="Connect to Spreadsheet")
        self.runBtn.grid(column=0,row=1,columnspan=2, padx=5,pady=5)
        self.runBtn.config(state="disabled")

        self.saveBtn = tk.Button(self.lf,text="Save")
        self.saveBtn.grid(column=0,row=3,columnspan=2,padx=5,pady=5)
        self.saveBtn.config(state="disabled")

        tk.Label(self.lf,text="Set Auto-Save Interval (s)").grid(column=0,row=4,columnspan=2,padx=5,pady=5)

        self.entry = tk.Entry(self.lf,bg="lightgrey",textvariable=self.interval)
        self.entry.grid(column=3,row=4,columnspan=2,padx=5,pady=5)


        self.selfSaveIntervalBtn = tk.Button(self.lf,text="Set Save Interval")
        self.selfSaveIntervalBtn.grid(column=0,row=5,columnspan=4,padx=5,pady=5)
        self.selfSaveIntervalBtn.config(state="disabled")

        print("adding callbacks to list! ")
        appState.addToIsBoardSetupCallback(self.inject)
        appState.addToIsBoardSetupCallback(self.setupExcelButton)

    # This set after board is setup (through threading Event flag)
    def setInteractor(self,boardInteractor:BoardInteractor):
        self.dataHandler = DataHandler(boardInteractor)

    def inject(self):
        self.interactor = self.appState.injectBoardInteractor()
        self.setInteractor(self.interactor)

    def setupExcelButton(self):
        self.runBtn.config(state="active",command=self.dataHandler.connect)
        self.saveBtn.config(state="active",command=self.dataHandler.save)
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

        
         