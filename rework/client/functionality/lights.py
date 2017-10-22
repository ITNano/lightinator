import configuration
import mq
import json
import logging

publisher = None 
outconn = None
bulbs = []
colorlist = {"list": [], "index":0}
logger = logging.getLogger(__name__)

# --------------------- Compulsory functions ----------------------- #
def get_functions():
	return {
			"setcolor":		    set_color,
			"setcolorlist":	    set_color_by_list,
            "setrelcolorlist":  set_color_by_list_relative,
			"setdimmer":	    set_dimmer,
            "incdimmer":        inc_dimmer,
            "decdimmer":        dec_dimmer,
			"setmode":		    set_mode,
			"setspeed":		    set_speed,
			"incspeed":	        inc_speed,
			"decspeed":     	dec_speed,
			"setetd":		    set_effect_time_difference,
			"select":		    select_bulb,
			"selectbyname":		select_bulb_by_name,
			"unselect":		    unselect_bulb,
			"unselectbyname":	unselect_bulb_by_name,
            "toggleselect":     toggle_bulb,
            "toggleselectbyname":toggle_bulb_by_name,
			"activate":		    activate_bulbs,
			"deactivate":	    deactivate_bulbs
	}
    
def set_publisher(event_engine):
    global publisher
    publisher = event_engine
    
    
# -------------------------- Helper functions ---------------------------- #
def load_config():
    global outconn
    conf = configuration.get_module_config("lights")
    outconn = mq.get_request_client(conf["server"]["outconn"])
    inconn = mq.get_subscriber_client(conf["server"]["inconn"], "lights")
    mq.run_listener("light_updates", inconn, server_update, lambda msg: json.loads(msg.strip("lights ")))
    send_message(json.dumps({"sync":1}))
    
def send_value_update(property, value):
    publisher.update_value(property, value)
    
def send_message(cmd):
    outconn.send_string(json.dumps(cmd))
    read = outconn.recv_string()
    logger.debug("Got response from service: "+read)
    
def find_bulb(index):
    for bulb in bulbs:
        if bulb["index"] == index:
            return bulb
            
def find_bulb_by_name(name):
    for bulb in bulbs:
        if bulb["name"] == name:
            return bulb
            
def get_selected_bulbs():
    res = []
    for bulb in bulbs:
        if bulb["selected"]:
            res.append(bulb)
    return res
            
def get_selected_bulb_indexes():
    res = []
    for bulb in bulbs:
        if bulb["selected"]:
            res.append(bulb["index"])
    return res
    
def lists_equal(list1, list2):
    if not len(list1) == len(list2):
        return False
        
    for entry in list1:
        if not entry in list2:
            return False
    for entry in list2:
        if not entry in list1:
            return False
    return True
    

    
# ------------------- Handle server updates ------------------ #
def server_update(name, msg):
    global bulbs
    if name == "light_updates":
        if msg.get("sync") is not None:
            bulbs = msg["bulbs"]
            for i in range(len(bulbs)):
                bulbs[i]["selected"] = False
                bulbs[i]["index"] = i
        elif msg.get("connected") is not None:
            find_bulb(msg["bulb"])["selected"] = msg["connected"]
            send_value_update("lights.selected."+str(msg["bulb"]), msg["connected"])
        elif msg.get("update") is not None:
            if msg.get("bulb") is not None:
                updated_bulbs = [msg.get("bulb")]
            else:
                updated_bulbs = msg.get("bulbs")
            if not type(msg.get("value")) == list:
                msg["value"] = len(msg["value"])*[msg["value"]]
            for i in range(len(updated_bulbs)):
                find_bulb(updated_bulbs[i])[msg["update"]] = msg["value"][i]
    
# ------------------- Implementation specific functions ------------------ #
def set_color(color):
    send_message({"cmd": "setcolor", "color": color, "bulbs": get_selected_bulb_indexes()})
    
def set_color_by_list(list, index):
    global colorlist
    if not lists_equal(list, colorlist["list"]):
        colorlist["list"] = list
    if type(index) == float:
        index = round(len(colorlist["list"])*index)
        
    colorlist["index"] = index
    logger.debug("Setting colorlist: %s with index %s", colorlist["list"], colorlist["index"])
    set_color(colorlist["list"][colorlist["index"]])
    
def set_color_by_list_relative(list, change):
    global colorlist
    if not lists_equal(list, colorlist["list"]):
        colorlist["list"] = list
        if change < 0:
            colorlist["index"] = (change+1)%len(colorlist["list"])
        else:
            colorlist["index"] = (change-1)%len(colorlist["list"])
    else:
        colorlist["index"] = (colorlist["index"]+change)%len(colorlist["list"])
    set_color(colorlist["list"][colorlist["index"]])
    
def set_dimmer(value):
    send_message({"cmd": "setdimmer", "value": value, "bulbs": get_selected_bulb_indexes()})
    
def inc_dimmer(increase):
    dimmers = []
    indexes = []
    for bulb in bulbs:
        if bulb["selected"]:
            dimmer = max(0, min(1, bulb["dimmer"]+increase))
            dimmers.append(dimmer)
            indexes.append(bulb["index"])
    send_message({"cmd": "setdimmer", "value": dimmers, "bulbs": indexes})
    
def dec_dimmer(decrease):
    inc_dimmer(-decrease)
    
def set_mode(mode):
    send_message({"cmd": "setmode", "mode": mode, "bulbs":get_selected_bulb_indexes()})
    
def set_speed(speed):
    send_message({"cmd": "setspeed", "speed": speed, "bulbs": get_selected_bulb_indexes()})
    
def inc_speed(increase):
    speeds = []
    indexes = []
    for bulb in bulbs:
        if bulb["selected"]:
            speed = max(0, min(1, bulb["speed"] + increase))
            speeds.append(speed)
            indexes.append(bulb["index"])
    send_message({"cmd": "setspeed", "speed": speeds, "bulbs": indexes})
    
def dec_speed(decrease):
    inc_speed(-decrease)
    
def set_effect_time_difference(etd):
    send_message({"cmd": "setetd", "etd": etd, "bulbs": get_selected_bulb_indexes()})
    
def activate_bulbs():
    send_message({"cmd": "activate", "bulbs": get_selected_bulb_indexes()})
    
def deactivate_bulbs():
    send_message({"cmd": "deactivate", "bulbs": get_selected_bulb_indexes()})
    
            
# ---------------------------------------------------------------------- #
# ---------------------- SELECTION FUNCTIONALITY ----------------------- #
# ---------------------------------------------------------------------- #            
def connect_to_bulb(bulb):
    send_value_update("lights.selecting."+str(bulb["index"]), 1)
    send_message({"cmd": "connect", "bulb": bulb["index"]})
    
def disconnect_from_bulb(bulb):
    bulb["selected"] = False
    send_value_update("lights.selected."+str(bulb["index"]), 0)
    
def select_bulb(index):
    bulb = find_bulb(index)
    if bulb is not None and not bulb["selected"]:
        connect_to_bulb(bulb)
    
def select_bulb_by_name(name):
    bulb = find_bulb_by_name(name)
    if bulb is not None and not bulb["selected"]:
        connect_to_bulb(bulb)
    
def unselect_bulb(index):
    bulb = find_bulb(index)
    if bulb is not None and bulb["selected"]:
        disconnect_from_bulb(bulb)
    
def unselect_bulb_by_name(name):
    bulb = find_bulb_by_name(name)
    if bulb is not None and bulb["selected"]:
        disconnect_from_bulb(bulb)
    
def toggle_bulb(index):
    bulb = find_bulb(index)
    if bulb is not None:
        if bulb["selected"]:
            disconnect_from_bulb(bulb)
        else:
            connect_to_bulb(bulb)
    
def toggle_bulb_by_name(name):
    bulb = find_bulb_by_name(name)
    if bulb is not None:
        if bulb["selected"]:
            disconnect_from_bulb(bulb)
        else:
            connect_to_bulb(bulb)
            
            
            
# ---------------------------------------------------------------------- #
# -------------- Load connections and other config stuff --------------- #
# ---------------------------------------------------------------------- #  
load_config()