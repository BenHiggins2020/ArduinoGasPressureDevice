from tkinter import * 
from tkinter import ttk
from tkinter import font
import tkinter as tk
from repository.BoardSetupHandler import BoardSetupHandler
from serial.tools.list_ports_common import *
import threading
from repository.BoardSetupHandler import *
from repository.BoardInteractor import *


class HelpFrame:

    def __init__(self, frame:Frame):
        self.help_tab = frame
        
        labelFrame = tk.LabelFrame(self.help_tab,text="User Guide:", bg="#A8C3A0")
        labelFrame.grid(row=0,column=0)

        textWidget = tk.Text(labelFrame, wrap="word",width=55)
        textWidget.grid(column=3,row=2,padx=5,pady=5)
        
        bold_font = font.Font(family="Helvetica", size=10, weight="bold")
        underline_font = font.Font(family="Helvetica", size=10, underline=True)

        textWidget.tag_configure("bold", font=bold_font)
        textWidget.tag_configure("underline", font=underline_font)

        textWidget.insert("end","Getting Started: \n\n","bold")
        textWidget.insert("end","1. Connecting.\n\n" \
        "Selecte the board from the dropdown menu, if not found automatically. Then press 'connect'. \n\n" \
        "If no board is found please make sure the board is connected and the press the 'refresh list' button, or restart the program. \n\n\n")
        textWidget.insert("end","2. Being collection.\n\n" \
        "Once the board has connected successfully, you can set the threshold value with the submit button \n\n" \
        "Then press 'Begin Data Collection' to program the sensor and begin reading values. \n " \
        "To read some of the more recent values press the 'output data' button," \
        " but this may be delayed and not show the most recent or relevant data.")


        textWidget.config(state="disabled")

    

    