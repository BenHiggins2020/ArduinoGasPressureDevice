import threading
from threading import *

TAG = "[ThreadManager]\t"
class ThreadManager:
    threadPool:list = []
    threadPoolDict:dict = {}
    def __init__(self):
        pass

    def addThread(self,thread:Thread,name:str = None):
        if name:
            self.threadPoolDict[name] = thread
            return
        self.threadPoolDict[thread.name] = thread

    def getThread(self,name:str)-> Thread:
        return self.threadPoolDict[name]
    
    def killThread(self,name:str,thread:Thread):
        self.getThread(name=name).join()

    def cancel(self):
        threadList:list[Thread] = self.threadPoolDict.values()
        for thread in threadList:
            thread.join()
        print(f"{TAG} All threads cancelled.")

    def creatThread(self,name:str, cb, shouldStart:bool=False):
        t = threading.Thread(target=cb,daemon=True,name=name)
        self.addThread(t)
        if shouldStart:
            self.getThread(name=name).start()



    