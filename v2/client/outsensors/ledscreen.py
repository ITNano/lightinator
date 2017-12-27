from statusindicator import StatusIndicator
import ioutil

class LEDScreen(StatusIndicator):

    def __init__(self, id, rs, en, data):
        StatusIndicator.__init__(self, id)
        self.bind_values = [("screen", self.update_screen)]
        self.rs = rs
        self.en = en
        self.data = data
        
    def get_bind_values(self):
        return self.bind_values
    
    
    def update_screen(self, prop, value):
        print("Screen prints: "+','.join(value.split('\n')))