from threading import Event
from repository.BoardInteractor import BoardInteractor

class AppState:

    onConnectCallback:list = list()
    onExcelConnectedCallback:list = list()
    callback_isBoardSetup:list = list()
    interactor:BoardInteractor = None

    def __init__(self):
       pass

    
    def addOnExcelConnectedListener(self,callback):
        self.onExcelConnectedCallback.append(callback)
        print(f"callback added [excel setup]: {len(self.onConnectCallback)}")
    
    def addOnConnectedListener(self,callback):
        self.onConnectCallback.append(callback)
        print(f"callback added [connection listener]: {len(self.onConnectCallback)}")
    
    def addBoardSetupListener(self,callback):
        self.callback_isBoardSetup.append(callback)
        print(f"callback added [board setup]: {len(self.onConnectCallback)}")


    def setExcelConnected(self):
        self.invokeOnExcelConnected()

    # Called from other classes once connection to arduino is made.
    # This invokes the onConnectedListener callbacks to run. 
    def setIsConnected(self):
        self.invokeOnConnected()

    def setBoardIsSetup(self):
        self.invokeBoardSetupCallbacks()

    # Dependency Injection of BoardInteractor.
    # once called, injectBoardInteractor is able to be used to return an instance of the BoardInteractor.
    def setBoardInteractor(self,bi:BoardInteractor):
        self.interactor = bi
    
    def injectBoardInteractor(self):
        return self.interactor

    # invoke onConnected callbacks. 
    def invokeOnConnected(self):
        print(f"Invoking callbacks (connection) {len(self.onConnectCallback)}")

        for cb in self.onConnectCallback:
            cb()

    def invokeBoardSetupCallbacks(self):
        print(f"Invoking callbacks (board setup) {len(self.callback_isBoardSetup)}")
        for cb in self.callback_isBoardSetup:
            cb()

    def invokeOnExcelConnected(self):
        print(f"Invoking callbacks (excel setup) {len(self.onExcelConnectedCallback)}")
        for cb in self.onExcelConnectedCallback:
            cb()


    # def setConnection(self,isConnected:bool):
    #     if isConnected:
    #         self.isConnected.set()
    #     else:
    #         self.isConnected.clear()
    
    # def setBoardSetup(self,isSetup:bool):
    #     if isSetup:
    #         self.boardSetupEvent.set()
    #     else:
    #         self.boardSetupEvent.clear()