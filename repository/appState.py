from threading import Event
from repository.BoardInteractor import BoardInteractor

class AppState:

    isConnected_Callback_List:list = list()
    callback_isBoardSetup:list = list()
    interactor:BoardInteractor = None

    def __init__(self):
        self.isConnected:Event = Event() # Dont reall need an event

        self.boardSetupEvent:Event = Event()

    def addToIsConnectedCallback(self,callback):
        self.isConnected_Callback_List.append(callback)
        print(f"callback added: {len(self.isConnected_Callback_List)}")
    
    def addToIsBoardSetupCallback(self,callback):
        self.callback_isBoardSetup.append(callback)
        print(f"callback added: {len(self.isConnected_Callback_List)}")


    # This is called from other classes. 
    def setIsConnected(self):
        self.invokeConnectionCallbacks()

    def setBoardIsSetup(self):
        self.invokeBoardSetupCallbacks()

    def setBoardInteractor(self,bi:BoardInteractor):
        self.interactor = bi
    
    def injectBoardInteractor(self):
        return self.interactor

    def invokeConnectionCallbacks(self):
        print(f"Invoking callbacks (connection) {len(self.isConnected_Callback_List)}")

        for cb in self.isConnected_Callback_List:
            cb()

    def invokeBoardSetupCallbacks(self):
        print(f"Invoking callbacks (board setup) {len(self.callback_isBoardSetup)}")
        for cb in self.callback_isBoardSetup:
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