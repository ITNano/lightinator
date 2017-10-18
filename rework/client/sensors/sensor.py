import logging

class Sensor(object):

    def __init__(self, id):
        self.logger = logging.getLogger(__name__)
        self.id = id
        
    def get_id(self):
        return self.id
        
    def get_value(self):
        return 0
        
    def check_valid(self, event_name, command):
        return True
        
        
    def activate(self):
        pass
        
    def deactivate(self):
        pass