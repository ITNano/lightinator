from sensor import Sensor
import pylirc
import time
import threading
import logging

UPDATE_FREQ = 100

class IR(Sensor):

    def __init__(self, id, configuration):
        Sensor.__init__(self, id)
        self.value = None
        self.listening = False
        if not self.init_pylirc(configuration):
            logging.warning("Warning: Could not load IR dependencies")
            
    def init_pylirc(self, configuration_path):
        try:
            pylirc.init("pylirc", configuration_path, False)
            return True
        except:
            return False
            
    def get_value(self):
        return self.value
        
        
    def activate(self):
        self.listening = True
        t = threading.Thread(target=self.listen_loop, name="IR Thread")
        t.daemon = True
        t.start()
        
    def deactivate(self):
        self.listening = False
        pylirc.exit()

    def listen_loop(self):
        while(not self.listening):
            s = pylirc.nextcode(1)
            if s is not None:
                for signal in s:                
                    if self.listening and signal is not None:
                        self.value = signal["config"]
                        self.push_event(signal["config"])
            time.sleep(0.040)