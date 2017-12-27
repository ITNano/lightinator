from hardware import Hardware
import time
import threading

class Button(Hardware):
    
    def __init__(self, iolib, id, pin, power, holdInterval=1):
        Hardware.__init__(self, id, "Button")
        self.pin = pin
        self.power = power
        self.holdInterval = holdInterval
        self.pressTime = -1
        self.onPressHandlers = []
        self.onReleaseHandlers = []
        self.onHoldHandlers = []
        self.holdTimer = None
        self.io = iolib
        self.initGPIO()

    def initGPIO(self):
        if self.power is not None:
            self.io.setDirection(self.power, self.io.OUT)
            self.io.writePin(self.power, self.io.ON)

        self.io.setDirection(self.pin, self.io.IN, pull_up_down=self.io.PUD_DOWN)
        self.io.registerForChangeEvent(self.pin, self.changedState)
        
    def getValue(self):
        return self.io.readPin(self.pin)
        
    def onPress(self, handler):
        if handler is not None:
            self.onPressHandlers.append(handler)
        
    def removePressHandler(self, handler):
        self.onPressHandlers.remove(handler)
        
    def onRelease(self, handler):
        if handler is not None:
            self.onReleaseHandlers.append(handler)
        
    def removeReleaseHandler(self, handler):
        self.onReleaseHandlers.remove(handler)
        
    def onHold(self, handler):
        if handler is not None:
            self.onHoldHandlers.append(handler)
            
    def removeHoldHandler(self, handler):
        self.onHoldHandlers.remove(handler)
        
    def changedState(self, channel):
        if channel == self.pin:
            if self.isActive():   # Button pressed
                self.pressTime = time.time()
                self.startHoldTimer()
                for handler in self.onPressHandlers:
                    handler(self)
            else:                 # Button released
                if self.holdTimer is not None:
                    self.holdTimer.cancel()
                    self.holdTimer = None
                if self.pressTime == -1:
                    timeDiff = 0
                else:
                    timeDiff = time.time() - self.pressTime
                for handler in self.onReleaseHandlers:
                    handler(self, timeDiff)
                timeDiff = -1
    
    def startHoldTimer(self):
        self.holdTimer = threading.Timer(self.holdInterval, self.holdTimerTriggered)
        self.holdTimer.start()
    
    def holdTimerTriggered(self):
        if self.isActive():
            self.startHoldTimer()
            for handler in self.onHoldHandlers:
                timeDiff = time.time() - self.pressTime
                handler(self, timeDiff)

    def isActive(self):
        return self.getValue() == 1
        
    def terminate(self):
        self.io.unregisterFromChangeEvent(self.pin)
        del self.onPressHandlers[:]
        del self.onReleaseHandlers[:]