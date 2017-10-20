import configuration
import mq

publisher = None 
outconn = None
bulbs = []
colorlist = {}

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
			"toggleselectall":	toggle_selected_bulbs,
			"activate":		    activate_bulbs,
			"deactivate":	    deactivate_bulbs
	}
    
def set_publisher(event_engine):
    global publisher
    publisher = event_engine
    
    
# -------------------------- Helper functions ---------------------------- #
def load_config():
    global outconn
    conf = configuration.get_module_config(lights)
    outconn = mq.get_publisher_client(conf["server"]["outconn"])
    inconn = mq.get_subscriber_client(conf["server"]["inconn"], "lights")
    mq.run_listener("light_updates", inconn, server_update, lambda msg: json.loads(msg.strip("lights ")))
    
def send_value_update(property, value):
    publisher.update_value(property, value)
    
def send_message(cmd):
    message = json.dumps(cmd)
    conn.send("lights "+message)
    
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
        print("Got an update from the server")
        if msg.get("sync") is not None:
            bulbs = msg["sync"]
            for bulb in bulbs:
                bulb["selected"] = False
        elif msg.get("selected") is not None:
            find_bulb(msg["bulb"])["selected"] = msg["selected"]
            send_value_update("lights.selected."+str(msg["bulb"]), msg["selected"])
        elif msg.get("update") is not None:
            find_bulb(msg["bulb"])[msg["update"]] = msg["value"]
    
# ------------------- Implementation specific functions ------------------ #
def set_color(color):
    send_message({"cmd": "setcolor", "color": color, "bulbs": get_selected_bulb_indexes()})
    
def set_color_by_list(list, index):
    global colorlist
    if not lists_equal(list, colorlist["list"]):
        colorlist["list"] = list
    if type(index) == float:
        index = len(colorlist["list"])*index
        
    colorlist["index"] = index
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
    
            
# ---------------------------------------------------------------------- #
# ---------------------- SELECTION FUNCTIONALITY ----------------------- #
# ---------------------------------------------------------------------- #            
def connect_to_bulb(bulb):
    send_value_update("lights.selecting."+str(bulb["index"]), 1)
    send_message({"cmd": "connect", "bulb": bulb["index"]})
    
def disconnect_from_bulb(bulb):
    bulb["selected"] = False
    send_value_update("lights.selected."+str(bulb["index"]), 0)
    
def announce_connection_attempt(index, response):
    bulb = find_bulb(index)
    bulb["selected"] = bool(json.loads(response)["connected"])
    send_value_update("lights.selecting."+str(index), 0)
    send_value_update("lights.selected."+str(index), bulb["selected"])
    
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