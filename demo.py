from tkinter import * 
from tkinter import ttk
import tkinter as tk
from repository.BoardSetupHandler import BoardSetupHandler
from serial.tools.list_ports_common import *
from application.setupFrame import SetupFrame
import threading

root = tk.Tk()
root.geometry("600x600")
root.title("Pressure Measurement Controller")

# Creating Global Events:
# onConnect = threading.Event()

boardSetterUpper = BoardSetupHandler()

# Main frame
main_frame = tk.Frame(root, bg="#DDEEFF")
main_frame.pack(fill="both", expand=True)

# Notebook widget
notebook = ttk.Notebook(main_frame)
notebook.pack(fill="both", expand=True, padx=10, pady=10)

# === Tab 1: Controls ===
controls_tab = tk.Frame(notebook, bg="#F0F0F0")
notebook.add(controls_tab, text="Controls")
print("Creating setup frame")
setupFrame = SetupFrame(controls_tab,boardSetterUpper)
# === Tab 2: Plot ===
plot_tab = tk.Frame(notebook, bg="#FFFFFF")
notebook.add(plot_tab, text="Live Plot")

# You could embed a matplotlib canvas here later

# === Tab 3: Settings ===
settings_tab = tk.Frame(notebook, bg="#F8F8F8")
notebook.add(settings_tab, text="Settings")

tk.Label(settings_tab, text="Refresh Rate (ms):").pack(pady=10)
tk.Entry(settings_tab).pack()

# canvas = tk.Canvas(root, width=200, height=100, bg="white")
# canvas.create_line(0, 0, 200, 100)
# canvas.pack()

# notebook = ttk.Notebook(root)
# tab1 = tk.Canvas(notebook,background="#8A9A5B")
# tab2 = tk.Frame(notebook,background="#C5CBA4")



# pane1 = tk.PanedWindow(notebook, orient=tk.VERTICAL)
# pane2 = tk.PanedWindow(notebook, orient=tk.VERTICAL)


# pane1.pack()
# pane.pack(expand=False)

# left_frame = tk.Frame(notebook,background="#B2AC88")
# right_frame = tk.Frame(notebook,background="#A8C3A0")
# left_frame.pack(fill="both",expand=True)

# tk.Label(left_frame, text = "Select Sensor com port").grid(row=0,column=0,padx=10,pady=5)
# tk.Entry(left_frame).grid(row=0,column=1,padx=10,pady=5)
# tk.Button(left_frame, text = "Start").grid(row=1,column=1,columnspan=2,pady=10)

# pane1.add(tk.Label(pane1, text = "This is text for the first pane"))
# pane1.add(tk.Label(pane1, text = "This is text for the first pane"))
# pane1.add(tk.Label(pane1, text = "This is text for the first pane"))
# pane1.add(tk.Label(pane1, text = "This is text for the first pane"))
# pane1.add(tk.Label(pane1, text = "This is text for the first pane"))
# pane1.add(tk.Label(pane1, text = "This is text for the first pane"))
# pane1.add(tk.Label(pane1, text = "This is text for the first pane"))
# pane1.add(tk.Label(pane1, text = "This is text for the first pane"))

# pane2.add(tk.Label(pane2, text = "This is text for the first pane 2"))


# notebook.add(left_frame, text="Pane1")
# notebook.add(right_frame, text="Settings")
# notebook.pack(fill="both", expand=True)


# tree = ttk.Treeview(root, columns=("Time", "Value"), show="headings")
# tree.heading("Time", text="Time")
# tree.heading("Value", text="Value")
# tree.insert("", "end", values=("12:00", "23.5"))
# tree.pack()
# ttk.Separator(root, orient="horizontal").pack(fill="x", pady=10)

root.mainloop()


