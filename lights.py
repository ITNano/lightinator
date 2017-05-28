import json
from socket import *
import netifaces
from lightwifi import connect,get_current_connection,init_lightwifi
from time import sleep

PYTHON3 = False

def add_bulb(name, network, nic):
    bulb = {}
    bulb["name"] = name
    bulb["identifier"] = []
    for num in reversed([name[i:i+2] for i in range(3, len(name), 2)]):
        bulb["identifier"].append(int('0x'+num, 16))
    bulb["color"] = [0x00, 0x00, 0x00, 0xDD, 0x00]
    bulb["actual_color"] = None
    bulb["network"] = network
    bulb["nic"] = nic
    
    all_bulbs.append(bulb)
    
def get_all_bulbs():
    return all_bulbs

def get_bulb_by_index(index):
    if index >= 0 and index < len(all_bulbs):
        return all_bulbs[index]
    
def get_bulb_by_name(name):
    for bulb in all_bulbs:
        if bulb["name"] == name:
            return bulb
    return None
    
def get_bulbs_by_names(names):
    bulbs = []
    for name in names:
        bulb = get_bulb_by_name(name)
        if bulb is not None:
            bulbs.append(bulb)
    return sorted(bulbs, key=bulb_sort_order)
    
def get_bulbs_by_room(room_name):
    return sorted(rooms.get(room_name, []), key=bulb_sort_order)
    
def get_rooms_of_bulb(bulb):
    bulb_rooms = []
    for (name, bulbs) in rooms.items():
        if bulb in bulbs:
            bulb_rooms.append(name)
    return bulb_rooms
    
def bulb_sort_order(bulb):
    return "" if bulb["name"] == get_current_connection() else bulb["name"]
    
def activate_bulbs(bulbs):
    success = True
    for bulb in bulbs:
        res = set_color([bulb], bulb["color"][0], bulb["color"][1], bulb["color"][2], bulb["color"][3], bulb["color"][4], False)
        success = success and res
    return success
    
def deactivate_bulbs(bulbs):
    return set_color(bulbs, 0x00, 0x00, 0x00, 0x00, 0x00, False)

def set_color(bulbs, red, green, blue, white, strength, save_result = True):
    data = [0xFB, 0xEB, red, green, blue, white, strength]
    for bulb in bulbs:
        data.extend(bulb["identifier"])
        data.append(0x00)
            
    success = True
    for bulb in bulbs:
        if not bulb["actual_color"] == [red, green, blue, white, strength]:
            print("Handling "+bulb["name"]+", setting color "+str((red, green, blue))+" [white="+str(white)+"]")
            if connect_to_bulb(bulb):
                actual_strength = strength
                if strength == -1:
                    actual_strength = bulb["color"][4]
                    data[6] = actual_strength
                if save_result:
                    bulb["color"] = [red, green, blue, white, actual_strength]
                bulb["actual_color"] = [red, green, blue, white, actual_strength]
                packet_data = getPacketData(data)
                send_message(packet_data, bulb["nic"]["broadcast"], bulb["nic"]["port"])
            else:
                print("\tNo change due to connection errors.")
                success = False
        else:
            print("Color already set. Ignoring bulb "+bulb["name"])
    return success

def getPacketData(data):
    if PYTHON3:
        return bytes(data)
    else:
        return bytearray(data)
    
def connect_to_bulb(bulb):
    global sock
    network = bulb["network"]
    nic = bulb["nic"]["name"]
    if(connections.get(nic) is None or connections[nic].get("network") != network):
        success = connect(network, nic)
        sock = socket(AF_INET, SOCK_DGRAM)
        sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        sock.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
        connections[nic] = {"sock":sock, "network": network}
        return success
    else:
        sock = connections[nic]["sock"]
        return True
    
def send_message(content, addr, port, retransmits=3):
    if sock is not None:
        for i in range(0, retransmits):
            sock.sendto(content, (addr, port))
            if i < retransmits-1:
                sleep(0.1)
    else:
        print("Error: Uninitialized socket!")
    
def load_config(conf):
    for bulb in conf["bulbs"]:
        nic = bulb.get("nic", conf.get("defaultnic", { "name": "wlan0", "broadcast": "192.168.4.255", "port": 30977 }))
        add_bulb(bulb["name"], bulb.get("network", bulb["name"]), nic)
        if connections.get(nic["name"]) is None:
            init_lightwifi(nic["name"])
            
all_bulbs = []
connections = {}
sock = None

