from sensor import Sensor
from evdev import InputDevice, KeyEvent, categorize, ecodes
import threading

class RFID(Sensor):
    
    def __init__(self, id, device):
        Sensor.__init__(self, id)
        self.input = InputDevice(device)
        self.active = False
        self.word = ""
        
    def continous_read(self):
        while self.active:
            for event in self.input.read_loop():
                if event.type == ecodes.EV_KEY:
                    key_event = categorize(event)
                    if key_event.keystate == KeyEvent.key_up:
                        self.register_stroke(keycodeToChar(key_event.keycode))
    
    def register_stroke(self, key):
        if key == "ENTER":
            word = self.word
            self.word = ""
            self.push_event(word)
        else:
            self.word += key
        
    def activate(self):
        self.active = True
        t = threading.Thread(target=self.continous_read, name="RFIDReader ["+self.get_id()+"]")
        t.daemon = True
        t.start()
        
    def deactivate(self):
        self.active = False
        
        
def keycodeToChar(keycode):
    return keycode[4:]