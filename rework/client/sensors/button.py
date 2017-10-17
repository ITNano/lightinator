import logging

class Button(object):

    def __init__(self, id, pin, power, holdInterval=1):
        self.logger = logging.getLogger(__name__)
        self.id = id
        self.pin = pin
        self.power = power
        self.holdInterval = holdInterval
        
    def activate(self):
        self.logger.debug("Activate button")
        
    def deactivate(self):
        self.logger.debug("Deactivate button")