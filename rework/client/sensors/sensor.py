import logging

class Sensor(object):

    def __init__(self, event_engine, id):
        self.logger = logging.getLogger(__name__)
        self.event_engine = event_engine
        self.id = id
        
    def get_id(self):
        return self.id
        
    def get_value(self):
        return 0
        
    def push_event(self, event_name):
        self.event_engine.push_event(self, event_name)
        
    def check_valid(self, event_name, command):
        return True
        
        
    def activate(self):
        pass
        
    def deactivate(self):
        pass