from repository.BoardInteractor import BoardInteractor
from repository.appState import AppState
from repository.excel.ExcelSheetHandler import ExcelSheetHandler
import openpyxl
from openpyxl import *
from datetime import datetime
import os
import queue
import threading
from queue import *
from collections import namedtuple
import traceback
from dataclasses import dataclass

SensorData = namedtuple("SensorData", ["raw", "threshold", "timestamp", "valveState"])
@dataclass
class SensorRecord:
    raw: float
    threshold: float
    timestamp: str
    valveState: str

    def to_row(self):
        """Convert the record to a list suitable for Excel appending."""
        return [ self.timestamp, self.raw, self.threshold, self.valveState]

TAG = "[DataHandler]\t"

# This class will be used to read data from the BoardInteractor, And store it to an excel file.
class DataHandler:
    # writeLock = threading.Lock()
    # setupLock = threading.Lock()
    saveLock = threading.Lock()
    shouldSavePeriodically = True
    saveInterval = 1 # second
    isSetup = False

    def __init__(self,boardInteractor:BoardInteractor,appState:AppState):
        self.appState = appState
        self.interactor = boardInteractor
        self.excelSheetHandler = ExcelSheetHandler()

    def connect(self):
        print(f"{TAG} Starting Excel Writing program. ")
        if not self.isSetup:
            print(f"{TAG} Workbook not successfully setup...")
            self.workbook = self.excelSheetHandler.setup()
            self.isSetup = True
        print(f"{TAG} Workbook is setup successfully.")
        self.stream = threading.Thread(target=self.readDataStream,daemon=True)
        self.stream.start()

        # periodicSave = threading.Thread(target=self.periodicSave,daemon=True)
        # periodicSave.start()
        
    def stopStream(self):
        with self.saveLock:
            print(f"{TAG} Stopping data stream...")
            self.stream.join(timeout=1)
            self.interactor.running = False


    def append(self,value:SensorRecord): ##This is called from beginDataStream@Tyler
        if(not self.excelSheetHandler.workbook):
            print(f"{TAG}Workbook not setup, cannot append data. ")
            return
        with self.saveLock:           
            print(f"{TAG}Append value {value}")
            try:
                self.excelSheetHandler.workbook.active.append(value.to_row())
            except Exception as e:
                print(f"{TAG}Failed to append to workbook w/ "+traceback.print_exc())

    def save(self):
        with self.saveLock:
            print(f"{TAG}Saving... ")
            self.excelSheetHandler.workbook.save(self.excelSheetHandler.getFileNameWithSuffix())
            print(f"{TAG}Save complete. ")

    def setSaveInterval(self,interval:int):
        with self.saveLock:
            print(f"{TAG}setSaveInterval({interval})")
            self.saveInterval = interval

    def periodicSave(self):
        with self.saveLock:
            print(f"{TAG}periodicSave()")   
            if not self.isSetup:
                print(f"{TAG}Workbook not setup, attempting to setup...")
                return
            else:
                print(f"{TAG}Workbook is setup, beginning periodic save...")

            try:
                while self.shouldSavePeriodically:
                    
                    with self.saveLock:
                        print(f"{TAG}Periodic save triggered. ")
                        self.save()
                        threading.Event().wait(self.saveInterval) # wait 5 minutes before saving again.
            except Exception as E:
                print("Exception on periodic save: \n"+traceback.print_exc())


    def startStream(self):
        try:
            self.interactor.running = True
            dataCollectionThread = threading.Thread(target=self.interactor.run, daemon=True)
            dataCollectionThread.start()
        except Exception as E:
            print("Failed to begin data collection: "+str(E))

    def readDataStream(self):
        print(f"{TAG}beginDataStream")
        if not self.isSetup:
            print(f"{TAG}Workbook not setup, attempting to setup...")
            return
        else:
            print(f"{TAG}Workbook is setup, beginning data stream...")

        try:
            queue:Queue = self.interactor.getData()
            value = None
            while True:

                newValue = queue.get()
                if not newValue == value: # Do not add new values to workbook if they are duplicates. 
                    value = newValue
                    sensorRecord = SensorRecord(**value)
                    self.append(sensorRecord)
               
                # else:
                    # print(f"new value is duplicate of value.\n Old Value: {value} \n New Value {newValue}")    
        except Exception as E:
            print("Exception on data stream: \n"+traceback.print_exc())