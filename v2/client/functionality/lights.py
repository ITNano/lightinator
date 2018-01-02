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
    
def find_bulb(id):
    for bulb in bulbs:
        if bulb["id"] == id:
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
            
def get_selected_bulb_ids():
    res = []
    for bulb in bulbs:
        if bulb["selected"]:
            res.append(bulb["id"])
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
    print("Got a message from server: ", msg)
    if name == "light_updates":
        if msg.get("sync") is not None:
            bulbs = msg["bulbs"]
            for bulb in bulbs:
                bulb["selected"] = False
                bulb["selecting"] = False
        elif msg.get("connected") is not None:
            b = find_bulb(msg["bulb"])
            b["selected"] = msg["connected"]
            b["selecting"] = False
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
    send_message({"cmd": "setcolor", "color": color, "bulbs": get_selected_bulb_ids()})
    
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
    send_message({"cmd": "setdimmer", "value": value, "bulbs": get_selected_bulb_ids()})
    
def inc_dimmer(increase):
    dimmers = []
    ids = []
    for bulb in bulbs:
        if bulb["selected"]:
            dimmer = max(0, min(1, bulb["dimmer"]+increase))
            dimmers.append(dimmer)
            ids.append(bulb["id"])
    send_message({"cmd": "setdimmer", "value": dimmers, "bulbs": ids})
    
def dec_dimmer(decrease):
    inc_dimmer(-decrease)
    
def set_mode(mode):
    send_message({"cmd": "setmode", "mode": mode, "bulbs":get_selected_bulb_ids()})
    
def set_speed(speed):
    send_message({"cmd": "setspeed", "speed": speed, "bulbs": get_selected_bulb_ids()})
    
def inc_speed(increase):
    speeds = []
    ids = []
    for bulb in bulbs:
        if bulb["selected"]:
            speed = max(0, min(1, bulb["speed"] + increase))
            speeds.append(speed)
            ids.append(bulb["ids"])
    send_message({"cmd": "setspeed", "speed": speeds, "bulbs": ids})
    
def dec_speed(decrease):
    inc_speed(-decrease)
    
def set_effect_time_difference(etd):
    send_message({"cmd": "setetd", "etd": etd, "bulbs": get_selected_bulb_ids()})
    
def activate_bulbs():
    send_message({"cmd": "activate", "bulbs": get_selected_bulb_ids()})
    
def deactivate_bulbs():
    send_message({"cmd": "deactivate", "bulbs": get_selected_bulb_ids()})
    
            
# ---------------------------------------------------------------------- #
# ---------------------- SELECTION FUNCTIONALITY ----------------------- #
# ---------------------------------------------------------------------- #            
def connect_to_bulb(bulb):
    if not bulb["selecting"]:
        bulb["selecting"] = True
        send_value_update("lights.selecting."+str(bulb["id"]), 1)
        send_message({"cmd": "connect", "bulbs": bulb["id"]})
    
def disconnect_from_bulb(bulb):
    if not bulb["selecting"]:
        bulb["selected"] = False
        send_value_update("lights.selected."+str(bulb["id"]), 0)
    
def select_bulb(id):
    bulb = find_bulb(id)
    if bulb is not None and not bulb["selected"]:
        connect_to_bulb(bulb)
    
def select_bulb_by_name(name):
    bulb = find_bulb_by_name(name)
    if bulb is not None and not bulb["selected"]:
        connect_to_bulb(bulb)
    
def unselect_bulb(id):
    bulb = find_bulb(id)
    if bulb is not None and bulb["selected"]:
        disconnect_from_bulb(bulb)
    
def unselect_bulb_by_name(name):
    bulb = find_bulb_by_name(name)
    if bulb is not None and bulb["selected"]:
        disconnect_from_bulb(bulb)
    
def toggle_bulb(id):
    bulb = find_bulb(id)
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