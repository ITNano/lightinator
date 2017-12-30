import os
import sys
import logging
import logging.config

# Setup so that imports be happy.
from client import projectpath
sys.path.append(projectpath.LIB_PATH)
sys.path.append(projectpath.SENSOR_PATH)
sys.path.append(projectpath.STATUS_INDICATOR_PATH)
sys.path.append(projectpath.FUNC_PATH)

from client import configuration as conf
from client import event
from client.core import Core
from client.event import EventEngine
from client.sensors import sensor

history = []

def keep_server_alive():
    print("")
    print("=================================")
    print("======== SERVER ONLINE ==========")
    print("=================================")
    while(True):
        global history
        cmd = input(" > ")
        
        if cmd == "prev":
            cmd = history.pop()
        
        if cmd == 'end':
            break
        elif cmd == 'easteregg':
            print("Wohooo, hello :D")
        elif cmd == 'test':
            event_engine.push_event(sensor.Sensor('ir'), 'up')
            event_engine.push_event(sensor.Sensor('ir'), 'up')
            event_engine.push_event(sensor.Sensor('ir'), 'toggleActiveOld')
            event_engine.push_event(sensor.Sensor('ir'), 'up')
            event_engine.push_event(sensor.Sensor('ir'), 'toggleActiveOld')
            event_engine.push_event(sensor.Sensor('ir'), 'up')
        elif cmd[:6] == "event ":
            data = cmd.split()
            if not trigger_sensor(data[1], data[2]):
                logging.warning("Could not find the requested sensor")
                
        elif cmd[:2] == "b ":
            if not trigger_sensor("button"+cmd[2:], "press"):
                logging.warning("Could not find the requested button")
        elif cmd[:4] == "upd ":
            data = cmd[4:].split()
            if len(data) == 2:
                if data[1][0] == "i":
                    event_engine.update_value(data[0], int(data[1][1:]))
                else:
                    event_engine.update_value(data[0], data[1])
            else:
                logging.warning("Invalid cmd. Syntax: upd [prop] [value]")
        else:
            print("Unknown command, try again?")
        history.append(cmd)
            
    return
    
def trigger_sensor(sensor_id, event):
    for sensor in core.sensors:
        if sensor.get_id() == sensor_id:
            event_engine.push_event(sensor, event)
            return True
    return False

if __name__ == "__main__":
    print("=================================")
    print("===== STARTING IOT SERVER =======")
    print("=================================")
    logging.config.fileConfig(projectpath.LOGGING_CONFIG_PATH)
        
    # Initial load of configs
    conf.load_config()
    
    # Startup sequence
    event_engine = EventEngine(conf.get_conf('variables'), conf.get_conf('events'))
    core = Core()
    core.setup_hardware(conf.get_conf('extensioncards'), conf.get_conf('sensors'), conf.get_conf('statusindicators'), event_engine)
    core.activate_sensors()
    
    # Available for commands
    keep_server_alive()
    
    # Cleanup sequence
    core.deactivate_sensors()
