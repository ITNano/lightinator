from hardware import Hardware
import time
import threading

class LED(Hardware):
    
    def __init__(self, iolib, id, pin, defaultValue=0):
        Hardware.__init__(self, id, "LED")
        self.pin = pin
        self.blinking = False
        self.overrideBlinkEndState = False
        self.io = iolib
        self.io.setDirection(self.pin, self.io.OUT)
        self.setValue(defaultValue)
        
    def getValue(self):
        return self.io.readPin(self.pin)
        
    def turnOn(self):
        self.setValue(1)
        
    def turnOff(self):
        self.setValue(0)
        
    def toggle(self):
        self.setValue((self.getValue()+1)%2)
        
    def setValue(self, value, overrideBlink=True):
        if overrideBlink:
            self.overrideBlinkEndState = True
            self.stopBlink()
        self.io.writePin(self.pin, value)
        
    # Note that the interval is for an entire cycle (on + off)    
    def blink(self, interval=1.0, endState=0):
        interval = float(interval)
        if self.blinking:
            self.blinkInterval = interval
            self.blinkEndState = endState
        else:
            self.blinking = True
            self.overrideBlinkEndState = False
            self.blinkInterval = interval
            self.blinkEndState = endState
            
            def runBlink(self):
                while(self.blinking):
                    self.setValue(1, False)
                    time.sleep(self.blinkInterval/2)
                    if self.blinking:                       # Make sure blink not cancelled
                        self.setValue(0, False)
                        time.sleep(self.blinkInterval/2)
                if not self.overrideBlinkEndState:
                    self.setValue(self.blinkEndState)
            t = threading.Thread(target=runBlink, args=(self,))
            t.daemon = True
            t.start()
            
    def stopBlink(self):
        self.blinking = False