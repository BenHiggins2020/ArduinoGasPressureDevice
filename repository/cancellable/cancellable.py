import reactivex
from reactivex import Subject,interval, operators as ops
from reactivex import *
import time
import threading
from threading import *
import tkinter as tk

from ..appState import AppState
from ..threadManager import ThreadManager

class Cancellable:

    ## When Stop Event is set, then the event should be stopped.
    stopEvent = threading.Event()
    eventLock = threading.Lock()
    actionThread:Thread = None

    ## Should appState be in here? 
    def __init__(self):
    # def __init__(self,appState:AppState):
        self.cancel_subject = Subject()
        # self.appState = appState
    
    def setCancellable(self,cb) -> Thread:
        print("setCancellable")
        self.cb = cb
        # self.createActionThread()
        # self.appState.threadManager.addThread(thread = self.actionThread, name = self.actionThread.name)

       
    def createActionThread(self):
        self.actionThread = threading.Thread(daemon=True, target=self.action)

    def start(self):
        print("start")
        self.stopEvent.clear()
        if not self.cb:
            print("No callback found, return.")
            return
        
        self.actionThread = threading.Thread(daemon=True, target=self.action)
        self.actionThread.start()

    
    def action(self):
        print(f"Action: is event triggered: {self.stopEvent.is_set()}")
        while not self.stopEvent.is_set():
            self.cb()
        print("action finished.")

    def isCancelled(self) -> bool:
        with self.eventLock:
            if not self.actionThread:
                return True
            elif self.actionThread.is_alive():
                return True
            
            return False

  
    def cancel(self):
        self.stopEvent.set()
        if not self.actionThread:
            return
        self.oldThread = self.actionThread
        self.oldThread.join()
        # self.actionThread = None

        self.isCancelled()
        # self.closeThread = Thread(target=self.actionThread.join,daemon=True)
        # self.closeThread.start()
        # print(f" Cancelled thread: {self.actionThread.name}")
        # self.closeThread.join()

# root = tk.Tk()


# c = Cancellable()

# def doSomething():
#     print("doing something.")

# c.setCancellable(doSomething)

# btn = tk.Button(root, text="start", command=c.start).pack()

# btn = tk.Button(root, text="cancel", command=c.cancel).pack()
# root.mainloop()
