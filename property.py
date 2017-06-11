
class Property(object):

    def __init__(self, value, type=None):
        self.value = value
        self.type = type
        self.listeners = []
        
    def addListener(self, listener):
        if listener is not None:
            self.listeners.append(listener)
            self.notifyListener(listener, self.value)
            
    def removeListener(self, listener):
        self.listeners.remove(listener)
        
    def getValue(self):
        return self.value
        
    def setValue(self, value):
        if self.type is None or type(value) is self.type:
            if self.value is not value:
                self.value = value
                for listener in self.listeners:
                    self.notifyListener(listener, value)
                    
    def notifyListener(self, listener, value):
        listener(value)

class BoolProperty(Property):

    DOWN = 0b01
    UP = 0b10
    BOTH = 0b11

    def __init__(self, value, eventsDir=BOTH):
        Property.__init__(self, value, bool)
        self.eventsDir = eventsDir
        
    def notifyListener(self, listener, value):
        if self.eventsDir & (0x01 << int(value)) > 0:
            listener(value)