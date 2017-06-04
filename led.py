import RPi.GPIO as GPIO

class LED(object):
    
    def __init__(self, id, pin):
        self.id = id
        self.pin = pin
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pin, GPIO.OUT)
        
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
        
    def terminate(self):
        pass