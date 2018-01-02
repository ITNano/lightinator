import mq
import json
import logging
import bulb as bulbmodule

logger = logging.getLogger(__name__)

publisher = None
responsers = {}
bulbs = []
    
def handle_command(name, msg):
    responsers[name].send_string("ok")
    msg = str(msg)
    cmd = json.loads(msg)
    if type(cmd) == str:
        cmd = json.loads(cmd)
        
    logger.info("Handling command: %s", cmd)
        
    if cmd.get("sync") is not None:
        publisher.send_string(json.dumps({"sync":True, "bulbs":[bulb.get_bulb_as_data() for bulb in bulbs]}))
    elif cmd.get("cmd") == "setcolor":
        res = do_multiple_bulbs(cmd.get("bulbs"), cmd.get("color"), lambda bulb, color: bulb.set_color(color), lambda bulb: bulb.get_color())
        send_prop_update(res["bulbs"], "color", res["values"])
    elif cmd.get("cmd") == "setdimmer":
        res = do_multiple_bulbs(cmd.get("bulbs"), cmd.get("value"), lambda bulb, strength: bulb.set_strength(strength), lambda bulb: bulb.get_strength())
        send_prop_update(res["bulbs"], "strength", res["values"])
    elif cmd.get("cmd") == "setmode":
        res = do_multiple_bulbs(cmd.get("bulbs"), cmd.get("mode"), lambda bulb, mode: bulb.set_mode is not None and bulb.set_mode(mode), lambda bulb: bulb.get_mode())
        send_prop_update(res["bulbs"], "mode", res["values"])
    elif cmd.get("cmd") == "setspeed":
        res = do_multiple_bulbs(cmd.get("bulbs"), cmd.get("speed"), lambda bulb, speed: bulb.set_speed is not None and bulb.set_speed(speed), lambda bulb: bulb.get_speed())
        send_prop_update(res["bulbs"], "speed", res["values"])
    elif cmd.get("cmd") == "setetd":
        res = do_multiple_bulbs(cmd.get("bulbs"), cmd.get("etd"), lambda bulb, etd: bulb.set_etd is not None and bulb.set_etd(etd), lambda bulb: bulb.get_etd())
        send_prop_update(res["bulbs"], "etd", res["values"])
    elif cmd.get("cmd") == "connect":
        for bulb in get_bulbs_by_ids(cmd.get("bulbs")):
            connected = bulb.connect is not None and bulb.connect()
            publisher.send_string(json.dumps({"connected": connected, "bulb": bulb.get_id()}))
    elif cmd.get("cmd") == "activate":
        res = do_multiple_bulbs(cmd.get("bulbs"), None, lambda bulb, x: bulb.activate(), lambda bulb: bulb.get_color())
        send_prop_update(res["bulbs"], "color", res["values"])
    elif cmd.get("cmd") == "deactivate":
        res = do_multiple_bulbs(cmd.get("bulbs"), None, lambda bulb, x: bulb.deactivate(), lambda bulb: bulb.get_color())
        send_prop_update(res["bulbs"], "color", res["values"])
    elif cmd.get("cmd") == "resetnetworks":
        res = do_multiple_bulbs(cmd.get("bulbs"), None, lambda bulb, x: bulb.reset_network() if hasattr(bulb, 'reset_network') else False, lambda bulb: True)
        publisher.send_string(json.dumps({"response": "resetnw", "result": res}))
    else:
        logger.warning("Got unknown command: ", cmd)
        
def do_multiple_bulbs(ids, parameter, action, value_retriever):
    if not type(parameter) == list:
        parameter = [parameter]*len(ids)
        
    res = {"bulbs": [], "values": []}
    for index, bulb in enumerate(get_bulbs_by_ids(ids)):
        if action(bulb, parameter[index]):
            res["bulbs"].append(bulb.get_id())
            res["values"].append(value_retriever(bulb))
    return res
            
        
def send_prop_update(bulbs, prop, values):
    if not type(bulbs) == list or len(bulbs) > 0:
        publisher.send_string(json.dumps({"update": prop, "value": values, "bulbs": bulbs}))
    
# ====================================== HELPERS ================================= #
def init():
    with open("setup.conf") as conf_file:
        conf = json.loads(conf_file.read())

    global publisher
    global bulbs
    publisher = mq.get_publisher_server(conf["publisher"])
    for address in conf["responseaddr"]:
        response_server = mq.get_response_server(address)
        mq.run_listener(address, response_server, handle_command)
        responsers[address] = response_server
        
    bulbs = load_bulbs(conf["hardware"])

def load_bulbs(conf):
    bulbs = []
    for bulb in conf["bulbs"]:
        bulbs.append(create_bulb(bulb, conf))
    return bulbs
        
def create_bulb(bulb_conf, conf):
    network = get_network(bulb_conf, conf.get("defaultnetwork", {}))
    id = bulb_conf.get("id", max([bulb.get_id() for bulb in bulbs]+[0])+1)
    return bulbmodule.ChinaBulb(id, bulb_conf.get("name", "Bulb_"+str(id)), network)
    
def get_network(custom, default):
    if custom is None:
        custom = {}
        if default is None:
            logger.warning("WARNING: No available network description found. Please check configuration!")
        
    return {prop: custom.get(prop, default.get(prop)) for prop in ["nic", "ssid", "address", "port"]}
    
def get_bulbs_by_ids(ids):
    if not type(ids) == list:
        ids = [ids]
    return sorted([bulb for bulb in bulbs if bulb.get_id() in ids], key=bulb_sort_order)
    
def get_bulbs_by_names(names):
    if not type(names) == list:
        names = [names]
    return sorted([bulb for bulb in bulbs if bulb.get_name() in names], key=bulb_sort_order)
    
def bulb_sort_order(bulb):
    return "" if bulb.is_connected is not None and bulb.is_connected() else bulb.get_name() 
 