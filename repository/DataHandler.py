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

import reactivex
from reactivex.scheduler import ThreadPoolScheduler
from reactivex import operators as ops
from .cancellable.cancellable import Cancellable

import time


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
    streamLock = threading.Lock()
    saveLock = threading.Lock()
    scheduler = ThreadPoolScheduler()
    # disposable = None
    saveInterval = 10 # second
    runCancellable = Cancellable()
    periodicSaveCancellable = Cancellable()
    dataStreamCancellable = Cancellable()
    appendStreamCancellable = Cancellable()

    value = None

    def __init__(self,boardInteractor:BoardInteractor,appState:AppState):
        self.appState = appState
        self.interactor = boardInteractor
        self.queue:Queue = self.interactor.getData()

        ## Setup Excel sheet.
        self.excelSheetHandler = ExcelSheetHandler()

        ## Setup cancellable framework for the "run" and "periodic save" commands.
        

        ## Setting the cancellable functions, these will run on threads and can be stopped and handled by the thread pool. 
        self.runCancellable.setCancellable(self.interactor.run2)
        self.periodicSaveCancellable.setCancellable(self.doPeriodicSave)
        self.dataStreamCancellable.setCancellable(self.readDataStream)
        self.appendStreamCancellable.setCancellable(self.append)

    def connect(self):
        print(f"{TAG} Starting Excel Writing program. ")
        if not self.excelSheetHandler.workbook:
            print(f"{TAG} Workbook not successfully setup...")
            self.workbook = self.excelSheetHandler.setup()
            if not self.workbook:
                print(f"{TAG} creating and connecting to workbook failed. ")
                return

        
        print(f"{TAG} Workbook is setup successfully.")
        # self.dataStreamCancellable.start()
        # self.stream = threading.Thread(target=self.initDataStream,daemon=True)
        # self.stream.start()

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

    def saveNoLock(self):
        print(f"{TAG}Saving... ")
        self.excelSheetHandler.workbook.save(self.excelSheetHandler.getFileNameWithSuffix())
        print(f"{TAG}Save complete. ")

    def doPeriodicSave(self):
        print("do Periodic save.")
        # ## If this is on a separate thread. we can sleep it for th interval...
        # print(f"{TAG} do Periodic save.. ")
        # time.sleep(self.saveInterval)
        # print(f"{TAG} do Periodic save.. TIME IS UP! ")
        # t = threading.Thread(daemon=True,target=self.saveNoLock)
        # t.start()
        # t.join()

        # if self.timer:
        #     self.timer.cancel()
        # self.timer = threading.Timer(self.saveInterval,self.save)
        # self.timer.start()
        

    ## You must press start stream to update.
    def setSaveInterval(self,interval:int):
        with self.saveLock:
            self.saveInterval = interval
            print(f"{TAG} PeriodicSaveCancellable -> Start")
            self.periodicSaveCancellable.start()
            # self.saveInterval = interval
            # print(f"{TAG}setSaveInterval({interval})")
            # self.disposable = reactivex.interval(interval).pipe(
            #     ops.map(lambda x : print(f"{TAG}Periodic Save called.. on interval of {interval} s"))
            # ).subscribe(lambda x: self.save())
    
    def startStream(self):
        try:
            print(f"{TAG}Startin dataStreamCancellable...")
            self.dataStreamCancellable.start()
            print(f"{TAG}Starting runCancellable...")
            self.runCancellable.start()
            # self.dataStreamCancellable.start()
            # self.interactor.runningSubj.on_next(True)
            # self.interactor.start()
            # self.dataCollectionThread = threading.Thread(target=self.interactor.run, daemon=True)
            # self.dataCollectionThread.start()
        except Exception as E:
            print("Failed to begin data collection: "+str(E))

    def stopStream(self):
        try:
            print(f"{TAG} Stopping dataStreamCancellable")
            if self.dataStreamCancellable and self.dataStreamCancellable.isCancelled():
                self.dataStreamCancellable.cancel()
                print(f"{TAG} Stopping runCancellable")

            if self.dataStreamCancellable and self.dataStreamCancellable.isCancelled():
                self.dataStreamCancellable.cancel()
                print(f"{TAG} Stopping data stream...")
                
            if self.periodicSaveCancellable and self.periodicSaveCancellable.isCancelled():
                self.periodicSaveCancellable.cancel()
                print(f"{TAG} periodicSaveCancellable")

        except Exception as e:
            print("Exception caught when attempting to cancel events.")
            raise e

    # def initDataStream(self):s
    #     self.dataStreamCancellable.start()


    def readDataStream(self):
        if not self.excelSheetHandler.workbook:
            print(f"{TAG}Workbook not setup, attempting to setup...")
            return

        try:
            newValue = self.queue.get()
            if not newValue == self.value: # Do not add new values to workbook if they are duplicates. 
                value = newValue
                sensorRecord = SensorRecord(**value)
                self.append(sensorRecord)
        except Exception as E:
            print("Exception on data stream: ")
            raise E.with_traceback()

    def close(self):
        try:
            print("Attempting close:")
            with self.saveLock:
                self.stopStream()
                print("Stream stopped. ")
                self.excelSheetHandler.workbook.close()

                print(f"{TAG} excelWorkbook closed.")

            print(f"{TAG} close finished. ")
        except Exception as e:
            raise e

            