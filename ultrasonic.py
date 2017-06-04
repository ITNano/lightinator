from hardware import Hardware
import RPi.GPIO as GPIO
import time

DEBUG = False

class UltraSonicSensor(Hardware):

    def __init__(self, id, trigger, echo):
        Hardware.__init__(self, id, "UltraSonic")
        self.trigger = trigger 
        self.echo = echo
        self.continousMeasure = False
        self.initGPIO()
        self.value = 0

    def initGPIO(self):
        GPIO.setmode(GPIO.BCM)

        GPIO.setup(self.trigger,GPIO.OUT)
        GPIO.setup(self.echo,GPIO.IN)

        GPIO.output(self.trigger, False)
        print("Waiting For Sensor To Settle")
        time.sleep(2)

    def doMeasure(self):
        # In case while loops fail (because of timing property)
        pulse_start = 0
        pulse_end = 0
        
        GPIO.output(self.trigger, True)
        time.sleep(0.00001)
        GPIO.output(self.trigger, False)

        while GPIO.input(self.echo)==0:
            pulse_start = time.time()
          
        while GPIO.input(self.echo)==1:
            pulse_end = time.time()
        
        pulse_duration = pulse_end - pulse_start
        distance = pulse_duration * 17150
        distance = round(distance, 2)

        return max(0, distance)
        
    def getValue(self):
        return self.value
        
    def startContinousMeasure(self, minDistance, maxDistance, callback, minSleepDistance=-1, maxSleepDistance=-1, allowedSleepTimes=3):
        # Init arguments
        if minSleepDistance == -1:
            minSleepDistance = minDistance
        if maxSleepDistance == -1:
            maxSleepDistance = maxDistance
            
        # Setup variables
        self.continousMeasure = True
        intervalSize = maxDistance-minDistance
        sleepCounter = 0
        
        # Loop for values until explicitly stopped
        while(self.continousMeasure):
            measure = self.doMeasure()
            if measure > maxSleepDistance or measure < minSleepDistance:
                sleepCounter += 1
                if sleepCounter > allowedSleepTimes:
                    if DEBUG:
                        print('ContinousMeasure: Measurement not in boundaries (',measure,'cm). Waiting 2s')
                    time.sleep(2)
                else:
                    if DEBUG:
                        print('Increasing sleep counter to ',sleepCounter)
                    time.sleep(0.01)
            else:
                if self.continousMeasure:
                    sleepCounter = 0
                    ratio = (measure-minDistance)/intervalSize
                    ratio = min(1, max(0, ratio))                     # Make sure it is between 0 and 1
                    self.value = ratio
                    callback(self, ratio)
                    time.sleep(0.01)
                
    def stopContinousMeasure(self):
        self.continousMeasure = False

    def terminate(self):
        self.continousMeasure = False
        GPIO.cleanup()

def cleanup():
    GPIO.cleanup()
