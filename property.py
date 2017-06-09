
class Property(object):

    def __init__(self, value, type=None):
        self.value = value
        self.type = type
        self.listeners = []
        
    def addListener(self, listener):
        if listener is not None:
            self.listeners.append(listener)
            listener(self.value)
            
    def removeListener(self, listener):
        self.listeners.remove(listener)
        
    def getValue(self):
        return self.value
        
    def setValue(self, value):
        if self.type is None or type(value) is self.type:
            if self.value is not value:
                self.value = value
                for listener in self.listeners:
                    listener(value)