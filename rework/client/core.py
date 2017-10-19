import logging
import inspect
import projectpath
import util

class Core(object):

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.sensor_modules = util.load_folder_modules(projectpath.SENSOR_PATH)
        self.sensors = []
        
    
    def setup_hardware(self, sensors, status_indicators, event_engine):
        for sensor in sensors:
            sensor_type = sensor.pop("type", None)
            if sensor_type is not None:
                self.load_sensor(event_engine, sensor_type, sensor)
            else:
                self.logger.warning("Sensor without specified type found in configuration!")
                
        self.logger.warning("Ignoring status indicators (during dev)")
        
        
    def load_sensor(self, event_engine, sensor_type, args):
        try:
            sensor_mod = self.sensor_modules[sensor_type]
            sensor_class = [obj for (name, obj) in inspect.getmembers(sensor_mod) if name.lower() == sensor_type.lower()][0]
            instance = sensor_class(**args)
            instance.set_publisher(event_engine)
            self.sensors.append(instance)
            self.logger.info("Sensor of type %s added with ID %s", sensor_type, instance.get_id())
            return instance
        except:
            self.logger.warning("Could not load sensor of type '%s'", type, exc_info=True)
            
    
    def activate_sensors(self):
        for sensor in self.sensors:
            sensor.activate()
    
    def deactivate_sensors(self):
        for sensor in self.sensors:
            sensor.deactivate()