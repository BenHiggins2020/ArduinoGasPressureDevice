from pyfirmata import Arduino, util
import queue
import threading
from datetime import datetime
# This class simply interacts with the Arduino board. 
# it will read sensor values and write to the digital pin.
# It will output values to a queue.
# It will use a threading lock to determine most up to date valve actuation threshold  
class BoardInteractor:
    
    valueChangedLock = threading.Lock()

    # TODO: Add criteria to connect to the board. 
    def __init__(self,board:Arduino, triggerValue:float = None):
        self.board = board
        self.writePin = self.board.get_pin('d:9:o')
        self.readPin = self.board.get_pin('a:0:i')
        self.it = util.Iterator(self.board)
        self.it.start()
        self.running = False # running value will determine whether or not data is being read.
        self.dataQueue = queue.Queue() #data queue will receive raw values ONLY

        if(triggerValue == None):
            self.ValveTriggerValue = 2.5 # This will be a default value for the valve   
        else:
            self.ValveTriggerValue = triggerValue
       

    def getData(self):
        return self.dataQueue       

    def setThreshold(self,newValue:float):
        with self.valueChangedLock:
            self.ValveTriggerValue = newValue
        print(f"thresholdValue updated: {self.ValveTriggerValue}")
    
    def getThreshold(self):
        with self.valueChangedLock:
            print(self.ValveTriggerValue)
            return self.ValveTriggerValue
    
    #This command will read sensor data only
    def run(self):
        valveState = "CLOSED"
        while self.running:
            raw = self.readPin.read()
            if(raw is not None):
                
                threshold = self.getThreshold()
                # print(f"sensor: {raw} , threshold: {threshold}")
                if(raw >= threshold):
                    self.writePin.write(1)
                    valveState = "OPEN"
                    # print("OPEN")
                else:
                    self.writePin.write(0)
                    valveState = "CLOSED"

                self.dataQueue.put({"raw":raw, "threshold":threshold, "timestamp":datetime.now().strftime("%H:%M:%S.%f")[:-3], "valveState":valveState})



                #for this case we are reading valid values.

        