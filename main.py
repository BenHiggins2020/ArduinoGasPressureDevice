from tkinter import * 
from tkinter import ttk
import tkinter as tk
from repository.BoardSetupHandler import BoardSetupHandler
from repository.BoardInteractor import BoardInteractor
from repository.appState import AppState
from serial.tools.list_ports_common import *
import threading
from application import *
from application.setupFrame import SetupFrame
from application.helpTab import HelpFrame
from application.subframe.ExcelFrame import ExcelFrame
from application.ConnectionFrame import ConnectionFrame

#TODO: Create a settings file which can be configured and parsed to that things like file location, can be saved like persistant data...
root = tk.Tk()
root.geometry("600x600")
root.title("Pressure Measurement Controller")

appState = AppState()
boardSetterUpper = BoardSetupHandler()

# Main frame
main_frame = tk.Frame(root, bg="#DDEEFF")
main_frame.pack(fill="both", expand=True)

# Notebook widget
notebook = ttk.Notebook(main_frame)
notebook.pack(fill="both", expand=True, padx=10, pady=10)

# === Tab 0: Setup / Connection  ===
connection_tab = tk.Frame(notebook, bg="#F0F0F0")
notebook.add(connection_tab, text="Setup / Connection")
connectionFrame = ConnectionFrame(connection_tab,boardSetterUpper,appState=appState)

# === Tab 1: Controls ===
controls_tab = tk.Frame(notebook, bg="#F0F0F0")
notebook.add(controls_tab, text="Controls")
print("creating setup frame")
setupFrame = SetupFrame(controls_tab,boardSetterUpper,appState=appState)

# === Tab 2: Plot ===
plot_tab = tk.Frame(notebook, bg="#FFFFFF")
notebook.add(plot_tab, text="Live Plot")

# You could embed a matplotlib canvas here later

# === Tab 3: Settings ===
# excel_tab = tk.Frame(notebook, bg="#F8F8F8")
# notebook.add(excel_tab, text="Excel")
# excel_frame = ExcelFrame(excel_tab,appState=appState)

# if appState.boardSetupEvent.is_set():
    # print("Main: is setup, inject into excel dataHandler. ")
    # excel_frame.setInteractor(setupFrame.boardInteractor)

# === Tab 4: Help ===
help_tab = tk.Frame(notebook, bg="#F8F8F8")
notebook.add(help_tab, text="Help")
helpFrame = HelpFrame(help_tab)



def closeGracefully():
    print("Closing gracefully... ")

    try:
        if excel_frame.dataHandler:
            print("Saving workbook before exit... ")
            excel_frame.close()
    except Exception as e:
        print(f"Failed to save workbook on exit... Exception: \n\n{e.with_traceback}")
        
    root.destroy()

root.protocol("WM_DELETE_WINDOW", closeGracefully)

root.mainloop()


