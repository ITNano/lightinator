from sensor import Sensor

class IR(Sensor):

    def __init__(self, event_engine, id):
        Sensor.__init__(self, event_engine, id)