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
        self.lf = LabelFrame(frame,text="Run ExcelSheet. ")
        self.lf.grid(column=0,columnspan=5,row=0,padx=10,pady=10)
        self.runBtn = tk.Button(self.lf,text="Load Excel")
        self.runBtn.grid(column=3,row=1)
        self.runBtn.config(state="disabled")
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
        
         