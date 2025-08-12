import serial.tools.list_ports
from serial.tools.list_ports_common import *
from pyfirmata import Arduino



# This class will be responsible for connecting to the board itself. 
# It will get the com ports and ideally try to match you to the connected arduino. 
class BoardSetupHandler:

    defaultPort = "No Arduino found, Please make sure it is connected"
    def __init__(self):
        self.COM_PORT:ListPortInfo = None
        self.isConnected = False
        self.ArduinoPort = self.defaultPort
        self.COM_PORT_NAME = ""
        self.ports = self.getAllPorts()
        self.portMap = self.getAllPortsMap()
        self.setCOMPortName(self.COM_PORT_NAME)
        

    def getAllPorts(self):
        portList:list[ListPortInfo] = []
        ports = serial.tools.list_ports.comports()
        for port in ports:
            if "Arduino" in port.description or "CH340" in port.description:
                self.COM_PORT = port
                self.setCOMPortName(port.name)
            portList.append(port)
        return portList
    
    def getAllPortNames(self):
        portList:list = []
        ports = serial.tools.list_ports.comports()
        for port in ports:
            if "Arduino" in port.description or "CH340" in port.description:
                self.COM_PORT = port
                self.setCOMPortName(port.name)
            portList.append(port.name)
        return portList
    
    def getAllPortNamesAndDevices(self):
        portList:list = []
        ports = serial.tools.list_ports.comports()
        self.ArduinoPort = self.defaultPort

        for port in ports:
            if "Arduino" in port.description or "CH340" in port.description:
                self.ArduinoPort = port.name +" "+port.description
                self.setCOMPortName(port.name)
            name = port.name +" "+port.description
            portList.append(name)

        if(self.ArduinoPort == self.defaultPort):
            self.isConnected = False

        return portList        

    def getAllPortsMap(self):
        portMap:dict = {}
        ports = serial.tools.list_ports.comports()
        for port in ports:
            if "Arduino" in port.description or "CH340" in port.description:
                self.COM_PORT = port
                self.setCOMPortName(port.name)

            key =  port.name +" "+port.description
            print(f"key = {key}")
            portMap[key] = port.name
    
        return portMap
    
    def setCOMPortName(self, portName):
        self.COM_PORT_NAME = portName
    
    def connect(self):
        try:
            self.board = Arduino(self.COM_PORT_NAME)   
            if(self.board.firmware_version != None):
                self.isConnected = True
                return self.isConnected
            else:
                self.isConnected = False
                return self.isConnected 
        except Exception as E:
            print("Failed to connect to arduino on selected com port. "+E.with_traceback)
            return False
    
    def connect(self,portName):
        self.COM_PORT_NAME = portName
        try:
            self.board = Arduino(self.COM_PORT_NAME)   
            if(self.board.firmware_version != None):
                self.isConnected = True
                return self.isConnected
            else:
                self.isConnected = False
                return self.isConnected
        except Exception as E:
            print("Failed to connect to arduino on selected com port. ")
            return False
       
