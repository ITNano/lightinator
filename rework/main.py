import os
import sys
import logging

from client import projectpath
from client import core

# Add lib path
sys.path.append(projectpath.LIB_PATH)


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
        
    curr_core = core.Core()
    curr_core.load_sensor("button", {"id":1, "pin":18, "power":1, "holdInterval":0.5})

    curr_core.activate_sensors()
    keep_server_alive()
    curr_core.deactivate_sensors()