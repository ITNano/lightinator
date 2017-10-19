from sensor import Sensor
import event
import ioutil
import time
import threading

class Button(Sensor):

    def __init__(self, id, pin, power=0, holdInterval=1):
        Sensor.__init__(self, id)
        self.pin = pin
        self.power = power
        self.hold_interval = holdInterval
        self.press_time = -1
        self.hold_time = 0
        self.hold_timer = None
        self.io = ioutil
        self.init_GPIO()
        
    def extra_event_properties(self):
        return ["holdMinInclusive", "holdMin", "holdMaxInclusive", "holdMax"]
    
    def check_valid(self, event_name, bounds):
        success = True
        if event_name == "hold":
            if bounds.get("holdMinInclusive") is not None:
                success = success and self.hold_time >= float(bounds["holdMinInclusive"])
            if bounds.get("holdMin") is not None:
                success = success and self.hold_time > float(bounds["holdMin"])
            if bounds.get("holdMaxInclusive") is not None:
                success = success and self.hold_time <= float(bounds["holdMaxInclusive"])
            if bounds.get("holdMax") is not None:
                success = success and self.hold_time < float(bounds["holdMax"])
            
        return success

    def init_GPIO(self):
        if self.power is not None:
            self.io.set_direction(self.power, self.io.OUT)
            self.io.write_pin(self.power, self.io.ON)

        self.io.set_direction(self.pin, self.io.IN, pull_up_down=self.io.PUD_DOWN)
        self.io.register_for_change_event(self.pin, self.changed_state)
        
    def get_value(self):
        return self.io.read_pin(self.pin)
        
    def changed_state(self, channel):
        if channel == self.pin:
            if self.is_active():   # Button pressed
                self.hold_time = 0
                self.press_time = time.time()
                self.start_hold_timer()
                self.push_event('press')
            else:                 # Button released
                if self.hold_timer is not None:
                    self.hold_timer.cancel()
                    self.hold_timer = None
                if self.press_time == -1:
                    self.hold_time = 0
                else:
                    self.hold_time = time.time() - self.press_time
                self.push_event('release')
    
    def start_hold_timer(self):
        self.hold_timer = threading.Timer(self.hold_interval, self.hold_timer_triggered)
        self.hold_timer.start()
    
    def hold_timer_triggered(self):
        if self.is_active():
            self.start_hold_timer()
            self.hold_time = time.time() - self.press_time
            self.push_event('hold')

    def is_active(self):
        return self.get_value() == 1
        
    def terminate(self):
        self.io.unregister_from_change_event(self.pin)