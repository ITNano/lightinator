import logging

class StatusIndicator(object):

    def __init__(self, id):
        self.logger = logging.getLogger(__name__)
        self.id = id
        
    def set_publisher(self, event_engine):
        self.publisher = event_engine
        for (prop, func) in self.get_bind_values():
            if prop is not None:
                self.publisher.add_property_listener(prop, func)
                
    def get_bind_values(self):
        return []
        
        
    def get_id(self):
        return self.id