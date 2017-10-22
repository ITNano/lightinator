from statusindicator import StatusIndicator
import ioutil
import threading
import time

class LED(StatusIndicator):

    def __init__(self, id, pin, blink, static):
        StatusIndicator.__init__(self, id)
        self.bind_values = {
            (blink, self.on_blink), (static, self.on_static)
        }
        self.pin = pin
        self.blinking = False
        self.io = ioutil
        self.io.set_direction(self.pin, self.io.OUT)
        
    def set_publisher(self, event_engine):
        StatusIndicator.set_publisher(self, event_engine)
        for (prop, func) in self.bind_values:
            if prop is not None:
                self.publisher.add_property_listener(prop, func)
    
    
    def on_blink(self, prop, value):
        if value:
            self.start_blink()
        else:
            self.off()
            
    def on_static(self, prop, value):
        if value:
            self.on()
        else:
            self.off()
            
    def start_blink(self):
        if not self.blinking:
            self.blinking = True
            t = threading.Thread(target=self.blink, name="LED Blink")
            t.daemon = True
            t.start()
        
    def blink(self):
        sleep_time = 0.3
        while(self.blinking):
            self.set_value(1)
            time.sleep(sleep_time)
            if self.blinking:
                self.set_value(0)
                time.sleep(sleep_time)
        
    def on(self):
        self.blinking = False
        self.set_value(1)
        
    def off(self):
        self.blinking = False
        self.set_value(0)
        
    def set_value(self, val):
        self.io.write_pin(self.pin, val)