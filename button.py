import RPi.GPIO as GPIO
import time
import threading

class Button(object):
    
    def __init__(self, id, pin, power, holdInterval=1):
        self.id = id
        self.pin = pin
        self.power = power
        self.holdInterval = holdInterval
        self.pressTime = -1
        self.onPressHandlers = []
        self.onReleaseHandlers = []
        self.onHoldHandlers = []
        self.holdTimer = None
        self.initGPIO()

    def initGPIO(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        if self.power is not None:
            GPIO.setup(self.power, GPIO.OUT)
            GPIO.output(self.power, 1)

        GPIO.add_event_detect(self.pin, GPIO.BOTH)
        GPIO.add_event_callback(self.pin, self.changedState)
        
    def getValue(self):
        return GPIO.input(self.pin)
        
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
        return GPIO.input(self.pin) == 1
        
    def terminate(self):
        GPIO.remove_event_detect(self.pin)
        del self.onPressHandlers[:]
        del self.onReleaseHandlers[:]