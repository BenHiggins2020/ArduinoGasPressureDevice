from threading import Event
from repository.BoardInteractor import BoardInteractor
from repository.listeners.BoardConnectionListener import ConnectionStateListener, DependencyInjection, Listener
from .threadManager import ThreadManager
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