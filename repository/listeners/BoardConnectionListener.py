import rx
# from rx.subject import Subject
# from rx import Observable 
# from rx import of

import reactivex
from reactivex import create
from reactivex import of, operators as op
from reactivex.subject import Subject
from reactivex.observer import Observer

import traceback

from enum import Enum

class ConnectionState(Enum):
    CONNECTED = 1
    DISCONNECTED = 2

TAG = "[ConnectionStateListener]\t"   

# Add callback to onConnectedCallback list which should be executed on connection 
# Add callback to onDisconnectedCallback list which should be executed on disconnection. 
# Source should be used to make connection state.
#  ie) source.on_next(ConnectionState.CONNECTED)
class ConnectionStateListener:

    onConnectedCallbacks = []
    onDisconnectedCallbacks = []
    source = Subject[ConnectionState]()

    def __init__(self): 
        composed = self.source.pipe(
            op.map(lambda state: self.doOnNext(state))
        )

        composed.subscribe(
            on_next = lambda value: print(f"{TAG}[onNext] {value}"),
            on_error = lambda e: self.handleError(e),
            on_completed = lambda: print(f"{TAG}Done!"),
        )

    def handleError(self, error):
        print(f"{TAG} Error occurred: {error}")
        traceback.print_exception(type(error),error,error.__traceback__)

    def addOnConnectedListener(self,callback):
        self.onConnectedCallbacks.append(callback)
        print(f"{TAG}callback added [connection listener]: {len(self.onConnectedCallbacks)}")

    def addOnDisconnectedListener(self,callback):
        self.onDisconnectedCallbacks.append(callback)
        print(f"{TAG}callback added [disconnection listener]: {len(self.onDisconnectedCallbacks)}")

    
    def doOnNext(self,state: ConnectionState):
        print(f"{TAG}[doOnNext] {state}")
        if state == ConnectionState.CONNECTED:
            print(f"{TAG}Connected!")
            self.onConnect()

        elif state == ConnectionState.DISCONNECTED:
            print(f"{TAG}Disconnected!")
            self.onDisconnect()
        return state

    

    def onConnect(self):
        for cb in self.onConnectedCallbacks:
            cb()

    def onDisconnect(self):
        for cb in self.onDisconnectedCallbacks:
            cb()


def handleError(error):
    print(f"{TAG} Error occurred: {error}")
    traceback.print_exception(type(error),error,error.__traceback__)

BTAG = "[Listener]\t"
# Generic listener which is used to create listeners for different events. 
# ex) ConnectionListener = Listener()

class Listener:
    onInvoke = []
    subject = Subject()

    def __init__(self):
        
        composed = self.subject.pipe(
            op.map(lambda value: self.doOnNext())
        )

        composed.subscribe(
            on_next = lambda value: print(f"{BTAG}[onNext]"),
            on_error = lambda e: print(f"{BTAG}Error Occurred: {e}"),
            on_completed = lambda: print(f"{BTAG}Done!"),
        )

    def addObserver(self, observer:Observer):
        self.subject.observers.append(observer)


    def doOnNext(self):
        print(f"{BTAG}[doOnNext]")
    
        self.invokeCallback()
        return

    def invokeCallback(self):
        for cb in self.onInvoke:
            cb()



class DependencyInjection:
    instances = {}
    
    @classmethod
    def register(cls, key, dependency,tag=""):
        # print(f"{tag} DI called: register:")
        # print(f"DI: attempt to register {key} to {dependency}")
        # print(f"DI: adding instance: {cls.instances.__sizeof__}")
        
        cls.instances[key] = dependency
    
    @classmethod
    def resolve(cls, key, tag=""):
        val = cls.instances.get(key)
        # print(f"{tag} DI: resolving({key}): {val}")

        return cls.instances.get(key)
    



#Example: 
# listener = Listener()

# observer = Observer(
#     on_next=lambda value: print(f"Observer received: {value}"),
#     on_error=lambda e: print(f"Observer error: {e}"),
#     on_completed=lambda: print(f"Observer completed"),
# )
# observer2 = Observer(
#     on_next=lambda value: print(f"Observer2 received: {value}"),
#     on_error=lambda e: print(f"Observer error: {e}"),
#     on_completed=lambda: print(f"Observer completed"),
# )


# listener.addObserver(observer)
# listener.addObserver(observer2)

# listener.subject.on_next("Test Event")

# observer2.dispose()

# listener.subject.on_next("Test Event2")


