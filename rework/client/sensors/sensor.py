import logging

class Sensor(object):

    def __init__(self, id):
        self.logger = logging.getLogger(__name__)
        self.id = id
        
    def set_publisher(self, event_engine):
        self.publisher = event_engine
        
    def get_id(self):
        return self.id
        
    def get_value(self):
        return 0
        
    def push_event(self, event_name):
        self.publisher.push_event(self, event_name)
        
    def extra_event_properties(self):
        return []
        
    def check_valid(self, event_name, command):
        return True
        
        
    def activate(self):
        pass
        
    def deactivate(self):
        pass