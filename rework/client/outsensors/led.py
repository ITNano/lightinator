from statusindicator import StatusIndicator

class LED(StatusIndicator):

    def __init__(self, id, pin, blink, static):
        StatusIndicator.__init__(self, id)
        self.blink_property = blink
        self.static_property = static
        
    def set_publisher(self, event_engine):
        StatusIndicator.set_publisher(self, event_engine)
        if not self.blink_property is None:
            self.publisher.add_property_listener(self.blink_property, self.on_blink)
        if not self.static_property is None:
            self.publisher.add_property_listener(self.static_property, self.on_static)
    
    
    def on_blink(self, prop, value):
        if value:
            self.blink()
        else:
            self.off()
            
    def on_static(self, prop, value):
        if value:
            self.on()
        else:
            self.off()
            
    def blink(self):
        print("BLINK BLINK")
        
    def on(self):
        print("LED IS ON")
        
    def off(self):
        print("LED IS OFF")