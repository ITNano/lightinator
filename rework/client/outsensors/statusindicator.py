import logging

class StatusIndicator(object):

    def __init__(self, id):
        self.logger = logging.getLogger(__name__)
        self.id = id
        
    def set_publisher(self, event_engine):
        self.publisher = event_engine
        
        
    def get_id(self):
        return self.id