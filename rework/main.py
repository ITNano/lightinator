import os
import sys
import logging

# Setup so that imports be happy.
from client import projectpath
sys.path.append(projectpath.LIB_PATH)
sys.path.append(projectpath.SENSOR_PATH)
sys.path.append(projectpath.FUNC_PATH)

from client import configuration as conf
from client import event
from client import core
from client.sensors import sensor

def keep_server_alive():
    print("")
    print("=================================")
    print("======== SERVER ONLINE ==========")
    print("=================================")
    while(True):
        cmd = input(" > ")
        if cmd == 'end':
            break
        elif cmd == 'easteregg':
            print("Wohooo, hello :D")
        else:
            print("Unknown command, try again?")
            
    return

if __name__ == "__main__":
    print("=================================")
    print("===== STARTING IOT SERVER =======")
    print("=================================")
    logging.basicConfig(level=10)
        
    # Initial load of configs
    conf.load_config()
    
    # Startup sequence
    curr_core = core.Core()
    curr_core.setup_hardware(conf.get_conf('sensors'), conf.get_conf('statusindicators'))
    event.setup_events(conf.get_conf('variables'), conf.get_conf('events'))
    curr_core.activate_sensors()
    
    # Available for commands
    keep_server_alive()
    
    # Cleanup sequence
    curr_core.deactivate_sensors()