import time
import logging
import ioutil
import threading
from sensor import Sensor

DIFF_LIMIT = 2

class UltraSonic(Sensor):

    def __init__(self, id, trigger, echo,  sleep_time=2, read_freq_time=0.3, mindetect=0, maxdetect=1000, minsleep=-1, maxsleep=-1, allowedmisreads=3):
        Sensor.__init__(self, id)
        self.logger = logging.getLogger(__name__)
        self.trigger = trigger 
        self.echo = echo
        self.continous_measure = False
        self.value = 0
        self.io = ioutil
        
        # Times between reads
        self.sleep_time = sleep_time
        self.read_freq_time = read_freq_time
        # Detection range that is valid
        self.min_distance = mindetect
        self.max_distance = maxdetect
        # Detection range before entering sleep mode (lower bound)
        self.min_sleep_distance = minsleep
        if self.min_sleep_distance < 0:
            self.min_sleep_distance = mindetect
        # Detection range before entering sleep mode (upper bound)
        self.max_sleep_distance = maxsleep
        if self.max_sleep_distance < 0:
            self.max_sleep_distance = maxdetect
        # Number of reads outside sleep interval before sleep mode is entered
        self.allowed_misreads = allowedmisreads
        
        self.init_GPIO()

    def init_GPIO(self):
        self.io.set_direction(self.trigger, self.io.OUT)
        self.io.set_direction(self.echo, self.io.IN)

        self.io.write_pin(self.trigger, self.io.OFF)
        self.logger.debug("Initializing hypersonic sensor, please wait.")
        time.sleep(2)

    def do_measure(self):
        # In case while loops fail (because of timing property)
        pulse_start = 0
        pulse_end = 0
        
        self.io.write_pin(self.trigger, self.io.ON)
        time.sleep(0.00001)
        self.io.write_pin(self.trigger, self.io.OFF)

        start_time = time.time()
        failed_measurement = False
        while self.io.read_pin(self.echo)==0 and not failed_measurement:
            pulse_start = time.time()
            failed_measurement = (pulse_start - start_time) > 0.025
            
        if failed_measurement:
            return 0
          
        start_time = time.time()
        while self.io.read_pin(self.echo)==1 and not failed_measurement:
            pulse_end = time.time()
            failed_measurement = (pulse_end - start_time) > 0.025
            
        if failed_measurement:
            return 0
        
        pulse_duration = pulse_end - pulse_start
        distance = pulse_duration * 17150
        distance = round(distance, 2)

        return max(0, distance)
        
    def get_value(self):
        return self.value
        
    def run_continous_measure(self):
        # Setup variables
        interval_size = self.max_distance-self.min_distance
        sleep_counter = 0
        prev = 0
        
        # Loop for values until explicitly stopped
        while(self.continous_measure):
            self.logger.debug("In ultrasonic loop")
            measure = self.do_measure()
            if measure > self.max_sleep_distance or measure < self.min_sleep_distance:
                sleep_counter += 1
                if sleep_counter > self.allowed_misreads:
                    self.logger.debug('ContinousMeasure: Measurement not in boundaries ({}cm). Waiting 2s'.format(measure))
                    time.sleep(self.sleep_time)
                else:
                    self.logger.debug('Increasing sleep counter to {}'.format(sleep_counter))
                    time.sleep(self.read_freq_time)
            else:
                if self.continous_measure:
                    sleep_counter = 0
                    if abs(prev-measure) < DIFF_LIMIT:
                        ratio = (measure-self.min_distance)/interval_size
                        ratio = min(1, max(0, ratio))                     # Make sure it is between 0 and 1
                        self.value = ratio
                        self.push_event("change")
                    else:
                        self.logger.debug("Ignores value due to error marginal")
                    time.sleep(self.read_freq_time)
            prev = measure
        self.logger.debug("Stopping ultrasonic loop")
        
    def activate(self):
        self.continous_measure = True
        t = threading.Thread(target=self.run_continous_measure, name="Ultrasonic ["+self.get_id()+"]")
        t.daemon = True
        t.start()
        
    def deactivate(self):
        self.continous_measure = False
        self.io.cleanup()
