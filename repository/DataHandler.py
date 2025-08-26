from repository.BoardInteractor import BoardInteractor
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
        return [self.raw, self.threshold, self.timestamp, self.valveState]

TAG = "[DataHandler]\t"

# This class will be used to read data from the BoardInteractor, And store it to an excel file.
class DataHandler:
    fileNamePrefix = "Gas_Measurment_"
    writeLock = threading.Lock()
    setupLock = threading.Lock()
    isSetup = False

    def __init__(self,boardInteractor:BoardInteractor):
        self.interactor = boardInteractor
        self.workbook = self.searchForWorkbook()

    def connect(self):
        print(f"{TAG} Starting Excel Writing program. ")
        if not self.isSetup:
            print("Workbook not successfully setup...")
            self.workbook = self.searchForWorkbook()
        print(f"{TAG} Workbook is setup successfully.")
        stream = threading.Thread(target=self.beginDataStream,daemon=True)
        stream.start()
        
    def setHeaders(self,headers:list): # This is used in setup and createSheet
        with self.writeLock:
            if(not self.workbook):
                print(f"{TAG}Workbook not setup, cannot set headers. ")
                return
            
            print(f"{TAG}Setting headers {headers}")
            try:
                for col, header in enumerate(headers, start=1):
                    self.workbook.active.cell(row=1, column=col, value=header)                # self.workbook.active.append(headers)
            except Exception as e:
                print(f"{TAG}Failed to append to workbook w/ "+traceback.print_exc())

    def append(self,value:SensorRecord): ##This is called from beginDataStream
        with self.writeLock:
            if(not self.workbook):
                print(f"{TAG}Workbook not setup, cannot append data. ")
                return
            
            print(f"{TAG}Append value {value}")
            try:
                self.workbook.active.append(value.to_row())
            except Exception as e:
                print(f"{TAG}Failed to append to workbook w/ "+traceback.print_exc())

    def save(self):
        print(f"{TAG}attempting save.. ")
        with self.writeLock:
            print(f"{TAG}Saving... ")
            self.workbook.save(self.getFileNameWithSuffix())

    def beginDataStream(self):
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

    def createSheet(self,wb:Workbook):
        print(f"{TAG}createSheet name={self.getSheetName()}")
        sheet = self.workbook.create_sheet(self.getSheetName())
        columns = {
                    'Raw Sensor Value': 'A',
                    'Threshold': 'B',
                    'timestamp': 'C',
                    'valveState': 'D'
                }
        self.setHeaders(list(columns))
        return sheet

    def searchForWorkbook(self):
        with self.setupLock:
            print(f"{TAG}Searching for workbook...")
            if not os.path.exists(self.getFileNameWithSuffix()):
                print(f"{TAG}Workbook not found, creating work book.")
                self.createNewWorkbook()
            else:
                print(f"{TAG}Workbook found.")
                
                try:
                    workbook = openpyxl.load_workbook(self.getFileNameWithSuffix())
                    print(f"{TAG}Sheets found: {workbook.sheetnames}")
                    self.workbook = workbook
                
                    # If a sheet for today is found, we want to open it and use it, otherwise create new sheet. 
                    if self.getSheetName() in workbook.sheetnames:
                        print(f"{TAG}Sheet with for date (name) {self.getSheetName()} was found.")
                        self.sheet = workbook[self.getSheetName()]
                        workbook.active = self.sheet
                        # if sheet is found, check to make sure firs
                        # t row is not empty, and if so add headers.
                        if self.is_row_empty(1):
                            print(f"{TAG} Sheet was empty, adding headers. ")
                            columns = {
                                'Raw Sensor Value': 'A',
                                'Threshold': 'B',
                                'timestamp': 'C',
                                'valveState': 'D'
                            }
                            self.setHeaders(list(columns))
                            workbook.save(self.getFileNameWithSuffix())
                    else:
                        print(f"{TAG}Sheet with for date (name) {self.getSheetName()} was NOT found.")
                        self.sheet = self.createSheet(workbook)
                        workbook.active = self.sheet
                        workbook.save(self.getFileNameWithSuffix())

                except Exception as E:
                    print(f"{TAG}Filed to load workbook from existing file. "+traceback.print_exc())
                
                
                workbook.save(self.getFileNameWithSuffix())
                self.isSetup = True
                self.workbook = workbook
                print(f"{TAG}Workbook setup complete.")
                return self.workbook
            

    def is_row_empty(self, row_num):
        for cell in self.workbook.active[row_num]:
            if cell.value not in (None, '') and str(cell.value).strip():
                return False
        return True
      
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
        
    