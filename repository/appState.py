from threading import Event
from repository.BoardInteractor import BoardInteractor
from repository.listeners.BoardConnectionListener import ConnectionStateListener, DependencyInjection, Listener

import reactivex
from reactivex import create
from reactivex import of, operators as op
from reactivex.subject import Subject
from reactivex.observer import Observer

class AppState:

    interactor:BoardInteractor = None

    onConnectListener = ConnectionStateListener()

    dependencyInjection = DependencyInjection()

    def __init__(self):
       pass

   



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