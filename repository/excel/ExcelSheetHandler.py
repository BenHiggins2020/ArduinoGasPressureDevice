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

TAG = "[ExcelSheetHandler]\t"
class ExcelSheetHandler:
    fileNamePrefix = "Gas_Measurment_"
    workbook:Workbook = None

    def __init__(self):
        pass

    def setup(self):
        try:
            print(f"{TAG} Setting up ExcelSheetHandler...")
            self.workbook = self.searchForWorkbook()
            if self.workbook:
                print(f"{TAG} ExcelSheetHandler setup complete.")
            else:
                print(f"{TAG} ExcelSheetHandler setup failed.")
        except Exception as E:
            print(f"{TAG} Exception during setup: {traceback.print_exc()}")
    
    def searchForWorkbook(self):
            print(f"{TAG}Searching for workbook...")
            if not os.path.exists(self.getFileNameWithSuffix()):
                print(f"{TAG}Workbook not found, creating work book.")
                self.createNewWorkbook()
            else:
                print(f"{TAG}Workbook found: {self.getFileNameWithSuffix()}")
                
                try:
                    self.workbook = openpyxl.load_workbook(self.getFileNameWithSuffix())
                    print(f"{TAG}Sheets found: {self.workbook.sheetnames}")
                
                    # If a sheet for today is found, we want to open it and use it, otherwise create new sheet. 
                    if self.getSheetName() in self.workbook.sheetnames:
                        print(f"{TAG}Sheet with for date (name) {self.getSheetName()} was found.")
                        self.sheet = self.workbook[self.getSheetName()]
                        self.workbook.active = self.sheet
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

                        self.workbook.save(self.getFileNameWithSuffix())
                        self.isSetup = True
                        print(f"{TAG}Workbook setup complete.")
                        return self.workbook
                    else:
                        print(f"{TAG}Sheet with for date (name) {self.getSheetName()} was NOT found.")
                        self.sheet = self.createSheet(self.workbook)
                        self.workbook.active = self.sheet
                        self.workbook.save(self.getFileNameWithSuffix())
                        self.isSetup = True
                        print(f"{TAG}Workbook setup complete.")
                        return self.workbook

                except Exception as E:
                    print(f"{TAG}Failed to load workbook from existing file. {traceback.print_exc()}")
                    # TODO: Handle corrupted file case.

    def createNewWorkbook(self): # This is called inside searchForWorkbook
        try:
            self.workbook = openpyxl.Workbook()
            sheet = self.workbook.active
            sheet.title = self.getFileName()+"_"+self.getDayMonthYear()
            sheet = self.createSheet(self.workbook)
            self.workbook.save(self.getFileNameWithSuffix())
        except Exception as E:
            print(f"{TAG}Failed to setup workbook from scratch. Exception: \n\n {E.with_traceback}")

    def createSheet(self,wb:Workbook):
        print(f"{TAG}createSheet name={self.getSheetName()}")
        sheet = self.workbook.create_sheet(self.getSheetName())
        self.workbook.active = sheet
        self.workbook.active.append(["Time","Raw Sensor Value","Threshold","valveState"])
        return sheet    

    def setHeaders(self,headers:list): # This is used in setup and createSheet
        if(not self.workbook):
            print(f"{TAG}Workbook not setup, cannot set headers. ")
            return
        
        print(f"{TAG}Setting headers {headers}")
        try:
            # for col, header in enumerate(headers, start=1):
            #     self.workbook.active.cell(row=1, column=col, value=header)
             self.workbook.active.append(headers)
        except Exception as e:
            print(f"{TAG}Failed to append to workbook w/ "+traceback.print_exc())

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
    
    def is_row_empty(self, row_num):
        for cell in self.workbook.active[row_num]:
            if cell.value not in (None, '') and str(cell.value).strip():
                return False
        return True
      