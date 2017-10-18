import time
from sensor import Sensor

class UltraSonic(Sensor):

    def __init__(self, id, trigger, echo,  minDetect=0, maxDetect=1000, minSleep=-1, maxSleep=-1, allowedMisreads=3):
        Sensor.__init__(self, id)
        self.trigger = trigger 
        self.echo = echo
        self.continousMeasure = False
        self.value = 0
        # Detection range that is valid
        self.minDetect = minDetect
        self.maxDetect = maxDetect
        # Detection range before entering sleep mode (lower bound)
        self.minSleep = minSleep
        if self.minSleep < 0:
            self.minSleep = self.minDetect
        # Detection range before entering sleep mode (upper bound)
        self.maxSleep = maxSleep
        if self.maxSleep < 0:
            self.maxSleep = self.maxDetect
        # Number of reads outside sleep interval before sleep mode is entered
        self.allowedMisreads = allowedMisreads