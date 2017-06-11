import json
from socket import *
import netifaces
import lightwifi
from time import sleep

PYTHON3 = False

MAX_STRENGTH = 52.0
NBR_OF_MODES = 17.0
MAX_SPEED = 5.0
MAX_ETD = 64.0


def add_bulb(name, network, nic):
    bulb = {}
    bulb["name"] = name
    bulb["identifier"] = []
    for num in reversed([name[i:i+2] for i in range(3, len(name), 2)]):
        bulb["identifier"].append(int('0x'+num, 16))
    bulb["identifier"].append(0x00)
    bulb["color"] = [0x00, 0x00, 0x00, 0xDD]
    bulb["prev_color"] = bulb["color"]
    bulb["strength"] = int(MAX_STRENGTH)
    bulb["mode"] = 0x00
    bulb["speed"] = 0x04
    bulb["etd"] = 0x01
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
    return "" if bulb["name"] == lightwifi.get_current_connection() else bulb["name"]
    
def activate_bulbs(bulbs):
    success = True
    for bulb in bulbs:
        res = set_color([bulb], bulb["prev_color"][0], bulb["prev_color"][1], bulb["prev_color"][2], bulb["prev_color"][3], False)
        res = res and set_strength(bulb["strength"])
        success = success and res
    return success
    
def deactivate_bulbs(bulbs):
    return set_color(bulbs, 0x00, 0x00, 0x00, 0x00, False)

def set_color(bulbs, red, green, blue, white, save_result = True):
    success = True
    for bulb in bulbs:
        if save_result:
            bulb["prev_color"] = [red, green, blue, white]
        bulb["color"] = [red, green, blue, white]
        success = success and send_update(bulb, get_color_packet_data)
    return success
    
def set_strength(bulbs, strength):
    return set_control_prop(bulbs, "strength", strength)
        
def set_mode(bulbs, mode):
    return set_control_prop(bulbs, "mode", mode)
    
def set_speed(bulbs, speed):
    return set_control_prop(bulbs, "speed", speed)
    
def set_effect_time_difference(bulbs, etd):
    return set_control_prop(bulbs, "etd", etd)

def set_control_prop(bulbs, prop, value):
    success = True
    value = int(value)
    for bulb in bulbs:
        bulb[prop] = value
        success = success and send_update(bulb, get_control_packet_data)
    return success
    
def get_color_packet_data(bulb):
    return [0xFB, 0xEB, bulb["color"][0], bulb["color"][1], bulb["color"][2], bulb["color"][3], 0x00] + bulb["identifier"]
            
def get_control_packet_data(bulb):
    return [0xFB, 0xEC, bulb["mode"], bulb["speed"], bulb["etd"], 0x02, bulb["strength"]] + bulb["identifier"]
            
def send_update(bulb, data_func):
    if connect_to_bulb(bulb):
        data = data_func(bulb)
        packet_data = getPacketData(data)
        send_message(packet_data, bulb["network"]["broadcast"], bulb["network"]["port"])
        return True
    else:
        return False

def getPacketData(data):
    if PYTHON3:
        return bytes(data)
    else:
        return bytearray(data)
    
def connect_to_bulb(bulb):
    global sock
    network = bulb["network"]["name"]
    nic = bulb["nic"]
    if(connections.get(nic) is None or connections[nic].get("network") != network):
        success = lightwifi.connect(network, nic)
        if success:
            sock = socket(AF_INET, SOCK_DGRAM)
            sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
            sock.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
            sock.setsockopt(SOL_SOCKET, 25, nic)
            connections[nic] = {"sock":sock, "network": network}
        return success
    else:
        sock = connections[nic]["sock"]
        return True
    
def send_message(content, addr, port, retransmits=3):
    #print ''.join('{:02x} '.format(x) for x in content)
    if sock is not None:
        for i in range(0, retransmits):
            sock.sendto(content, (addr, port))
            if i < retransmits-1:
                sleep(0.1)
    else:
        print("Error: Uninitialized socket!")
    
def load_config(conf):
    for bulb in conf["bulbs"]:
        nic = bulb.get("nic", conf.get("defaultnic", "wlan0"))
        network = get_network(bulb["name"], bulb.get("network"), conf.get("defaultnetwork"))
        add_bulb(bulb["name"], network, nic)
        lightwifi.register_network(network, nic)
    lightwifi.prepare_for_connections()
    # Init connections
    for bulb in all_bulbs:
        if connections.get(bulb["nic"]) is None:
            lightwifi.init_lightwifi(bulb["nic"], bulb["network"]["name"])
            
def unload_config():
    global all_bulbs
    all_bulbs = []
    lightwifi.unregister_all_networks()
    
def get_network(bulbName, custom, default):
    if custom is None:
        if default is None:
            print "WARNING: No available network description found. Please check configuration!"
        custom = {}
        
    network = {}
    properties = ["gateway", "address", "mask", "broadcast", "port", "name"]
    for prop in properties:
        network[prop] = custom.get(prop, default.get(prop))
    if network.get("name") is None:
        network["name"] = bulbName
    return network
            
all_bulbs = []
connections = {}
sock = None

