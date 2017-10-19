import logging
import inspect
import projectpath
import util

class Core(object):

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.sensor_modules = util.load_folder_modules(projectpath.SENSOR_PATH)
        self.status_indicator_modules = util.load_folder_modules(projectpath.STATUS_INDICATOR_PATH)
        self.sensors = []
        self.indicators = []
        
    
    def setup_hardware(self, sensors, status_indicators, event_engine):
        for sensor in sensors:
            sensor_type = sensor.pop("type", None)
            if sensor_type is not None:
                sensor_obj = self.load_hardware(event_engine, self.sensor_modules, sensor_type, sensor)
                self.sensors.append(sensor_obj)
            else:
                self.logger.warning("Sensor without specified type found in configuration!")
                
        for indicator in status_indicators:
            indicator_type = indicator.pop("type", None)
            if indicator_type is not None:
                indicator_obj = self.load_hardware(event_engine, self.status_indicator_modules, indicator_type, indicator)
                self.indicators.append(indicator_obj)
            else:
                self.logger.warning("Status indicator without specified type found in configuration!")
        
        
    def load_hardware(self, event_engine, modules, hardware_type, args):
        try:
            mod = modules[hardware_type]
            device_class = [obj for (name, obj) in inspect.getmembers(mod) if name.lower() == hardware_type.lower()][0]
            instance = device_class(**args)
            instance.set_publisher(event_engine)
            self.logger.info("Device of type %s added with ID %s", hardware_type, instance.get_id())
            return instance
        except:
            self.logger.warning("Could not load device of type '%s'", type, exc_info=True)
            
    
    def activate_sensors(self):
        for sensor in self.sensors:
            sensor.activate()
    
    def deactivate_sensors(self):
        for sensor in self.sensors:
            sensor.deactivate()