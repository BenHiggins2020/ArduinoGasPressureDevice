from repository.BoardInteractor import BoardInteractor
import openpyxl
from openpyxl import *
from datetime import datetime
import os
import queue
import threading
from queue import *
from collections import namedtuple

SensorData = namedtuple("SensorData", ["raw", "threshold", "timestamp", "valveState"])

# This class will be used to read data from the BoardInteractor, And store it to an excel file.
class DataHandler:
    
    fileNamePrefix = "Gas_Measurment_"
    writeLock = threading.Lock()

    def __init__(self,boardInteractor:BoardInteractor):
        self.interactor = boardInteractor
        self.workbook = self.searchForWorkbook()

    def connect(self):
        print("Starting Excel Writing program. ")
        self.workbook = self.searchForWorkbook()
        print("Workbook is setup successfully.")
        stream = threading.Thread(target=self.beginDataStream,daemon=True)
        stream.start()
        
    def append(self,value): ##This is called from beginDataStream
        with self.writeLock:
            data = SensorData(*value)
            self.workbook.active.append(list(data))

    def save(self):
        print(f"attempting save.. ")
        with self.writeLock:
            print("Saving... ")
            self.workbook.save(self.getFileNameWithSuffix())

    def beginDataStream(self):
        try:
            queue:Queue = self.interactor.dataQueue
            value = None
            while True:
                
                newValue = queue.get_nowait()
                if not newValue == value: # Do not add new values to workbook if they are duplicates. 
                    value = newValue
                    self.append(value)
               
                # else:
                    # print(f"new value is duplicate of value.\n Old Value: {value} \n New Value {newValue}")    
        except Exception as E:
            print("Exception on data stream. ")

    def createSheet(self,wb:Workbook):
        sheet = wb.create_sheet(self.getDayMonthYear())
        return sheet

    def searchForWorkbook(self):
        if not os.path.exists(self.getFileNameWithSuffix()):
            print("Workbook not found, creating work book.")
            self.createNewWorkbook()
        else:
            print("Workbook found.")
            try:
                workbook = openpyxl.load_workbook(self.getFileNameWithSuffix())
                print(f"Sheets found: {workbook.sheetnames}")

                # If a sheet for today is found, we want to open it and use it, otherwise create new sheet. 
                if self.getDayMonthYear() in workbook.sheetnames:
                    print(f"Sheet with for date (name) {self.getDayMonthYear()} was found.")
                    sheet = workbook[self.getDayMonthYear()]
                    workbook.active = sheet
                else:
                    print(f"Sheet with for date (name) {self.getDayMonthYear()} was NOT found.")
                    print(f"Sheets found: {workbook.sheetnames}")
                    sheet = self.createSheet(workbook)
                    workbook.active = sheet
              
                columns = {
                    'raw': 'A',
                    'threshold': 'B',
                    'timestamp': 'C',
                    'valveState': 'D'
                }
                sheet.append(list(columns))
                return workbook
            except Exception as E:
                print("Filed to load workbook from existing file. "+E.with_traceback())
            
    def createNewWorkbook(self): # This is called inside searchForWorkbook
        try:
            workbook = openpyxl.Workbook()
            sheet = workbook.active
            sheet.title = self.getFileName()+"_"+self.getDayMonthYear()
            sheet = self.createSheet(workbook)
            workbook.save(self.getFileNameWithSuffix())
        except Exception as E:
            print("Failed to setup workbook from scratch. Exception: \n\n "+E.with_traceback)

    def getSheetName(self): # The most recent sheet will be named after todays date. (day_month)
        return str(datetime.now().day)+"_"+str(datetime.now().month)

    def getDayMonthYear(self):
        return str(datetime.now().day)+"_"+str(self.getMonthYear())
    
    def getMonthYear(self):
        return str(datetime.now().month)+"_"+str(datetime.now().year)

    def getFileName(self):
        return self.fileNamePrefix + str(datetime.now().month)+"_"+str(datetime.now().year)

    def getFileNameWithSuffix(self):
        return self.getFileName()+".xlsx"
        
    