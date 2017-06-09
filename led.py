from hardware import Hardware
import RPi.GPIO as GPIO
import time
import threading

class LED(Hardware):
    
    def __init__(self, id, pin):
        Hardware.__init__(self, id, "LED")
        self.pin = pin
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pin, GPIO.OUT)
        self.blinking = False
        self.setValue(defaultValue)
        
    def getValue(self):
        return GPIO.input(self.pin)
        
    def turnOn(self):
        self.setValue(1)
        
    def turnOff(self):
        self.setValue(0)
        
    def toggle(self):
        self.setValue((self.getValue()+1)%2)
        
    def setValue(self, value):
        GPIO.output(self.pin, value is not 0)
        
    # Note that the interval is for an entire cycle (on + off)    
    def blink(self, interval=1.0, endState=0):
        interval = float(interval)
        if self.blinking:
            self.blinkInterval = interval
            self.blinkEndState = endState
        else:
            self.blinking = True
            self.blinkInterval = interval
            self.blinkEndState = endState
            
            def runBlink(self):
                while(self.blinking):
                    self.turnOn()
                    time.sleep(self.blinkInterval/2)
                    if self.blinking:                       # Make sure blink not cancelled
                        self.turnOff()
                        time.sleep(self.blinkInterval/2)
                self.setValue(self.blinkEndState)
            t = threading.Thread(target=runBlink, args=(self,))
            t.daemon = True
            t.start()
            
    def stopBlink(self):
        self.blinking = False