import logging
import pkgutil
import inspect
import client.projectpath as projectpath

class Core(object):

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.sensor_types = self.get_sensor_types()
        self.sensors = []

    """
      Loads the available sensor modules from static path. Code inspired by the Brain
      class in the jasper project by Shubhro Saha, Charles Marsh and Jan Holthuis.
      https://github.com/jasperproject/jasper-client/blob/master/client/brain.py
    """
    def get_sensor_types(self):
        sensor_path = projectpath.SENSOR_PATH
        self.logger.debug("Searching for sensor modules in folder: "+sensor_path);
        sensor_types = {}
        for finder, name, ispkg, in pkgutil.walk_packages([sensor_path]):
            try:
                loader = finder.find_module(name)
                mod = loader.load_module(name)
                
                self.logger.info("Loaded sensor type '%s'", name)
                sensor_types[name] = mod
            except:
                self.logger.warning("Skipped module '%s' due to mysterious error", name, exc_info=True)
                    
        return sensor_types
        
        
    def load_sensor(self, sensor_type, args):
        try:
            sensor_mod = self.sensor_types[sensor_type]
            sensor_class = [obj for (name, obj) in inspect.getmembers(sensor_mod) if name.lower() == sensor_type.lower()][0]
            instance = sensor_class(**args)
            self.sensors.append(instance)
            return instance
        except:
            self.logger.warning("Could not load sensor of type '%s'", type, exc_info=True)
            
    
    def activate_sensors(self):
        for sensor in self.sensors:
            sensor.activate()
    
    def deactivate_sensors(self):
        for sensor in self.sensors:
            sensor.deactivate()