import logging
import util
import projectpath
import re

VARIABLE_START_INDICATOR = "{"
VARIABLE_END_INDICATOR = "}"
VALUE_INDICATOR = VARIABLE_START_INDICATOR+"VALUE"+VARIABLE_END_INDICATOR

class EventEngine(object):

    def __init__(self, variables, events):
        self.logger = logging.getLogger(__name__)
        self.variables = variables
        self.events = events
        self.disabled_devices = []
        self.prop_listeners = []
        self.state = "default"
        
        # Load generic functionality modules
        def accept(name, mod):
            return hasattr(mod, "get_functions") and hasattr(mod, "set_publisher")
        modules = util.load_folder_modules(projectpath.FUNC_PATH, accept)
        self.modules = {}
        for name, module in modules.items():
            self.modules[name] = module.get_functions()
            module.set_publisher(self)
        self.modules["event"] = {"setstate": self.set_state, "togglesensor": self.toggle_sensor}
        
    # -------------------- Property listeners ----------------------- #    
    def add_property_listener(self, property, listener):
        self.prop_listeners.append((property, listener))
        
    def remove_property_listener(self, property, listener):
        self.prop_listeners.remove((property, listener))
            
    def update_value(self, property, value):
        for (prop, listener) in self.prop_listeners:
            if re.search(prop, property, re.IGNORECASE):
                listener(property, value)
        
        
    # ------------------ Internal exposed functions ----------------- #    
    def set_state(self, state):
        data["state"] = state
        
    def toggle_sensor(self, sensor):
        if sensor in self.disabled_devices:
            self.disabled_devices.remove(sensor)
        else:
            self.disabled_devices.append(sensor)
        
    # ------------------ Execute command on event ------------------- #    
    def is_variable_reference(self, obj):
        return type(obj) == str and obj[:1] == VARIABLE_START_INDICATOR and obj[-1:] == VARIABLE_END_INDICATOR
        
    def get_variable(self, name):
        if name[:1] == VARIABLE_START_INDICATOR and name[-1:] == VARIABLE_END_INDICATOR:
            name = name[1:-1]
            
        current_val = self.variables
        for part in name.split("."):
            try:
                current_val = current_val[part]
            except:
                try:
                    current_val = current_val[int(part)]
                except:
                    return None
                    
        return current_val
        
    def prepare_command(self, cmd, sensor):
        if type(cmd) == dict:
            prep_cmd = {}
            for key, val in cmd.items():
                prep_cmd[key] = self.prepare_command(val, sensor)
            return prep_cmd
        elif type(cmd) == list:
            prep_cmd = []
            for val in cmd:
                prep_cmd.append(self.prepare_command(val, sensor))
            return prep_cmd
        elif type(cmd) == str:
            if cmd == VALUE_INDICATOR:
                return sensor.get_value()
            elif self.is_variable_reference(cmd):
                return self.prepare_command(self.get_variable(cmd), sensor)
                
        return cmd
        
    def state_exists(self):
        return self.events.get(self.state) is not None
        
    def command_exists(self, trigger):
        return self.events[self.state].get(trigger) is not None
        
        
    def push_event(self, sensor, event_name):
        self.logger.debug("Got push event : %s.%s", sensor.get_id(), event_name)
        disabled = sensor.get_id() in self.disabled_devices
        trigger = sensor.get_id()+"."+event_name
        
        # use default actions if specific are not specified for this state
        state = "default"
        if self.state_exists() and self.command_exists(trigger):
            state = self.state
            
        commands = self.events[state].get(trigger, [])
        if not type(commands) == list:
            commands = [commands]
        for command in commands:
            prepared_command = self.prepare_command(command, sensor)
            if (not disabled or command["command"] == "togglesensor") and sensor.check_valid(event_name, prepared_command):
                self.run_command(prepared_command)
            else:
                self.logger.debug("Stopped command from being run")
            
            
    def run_command(self, command):
        self.logger.info("Running command : %s", command)
        try:
            module = self.modules[command["module"]]
            func = module[command["command"]]
            params = {key:value for (key, value) in command.items() if not key == "module" and not key == "command"}
            func(**params)
        except:
            self.logger.warning("Could not run function", exc_info=True)

