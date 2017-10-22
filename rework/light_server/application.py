import mq
import json
import lights
import logging

logger = logging.getLogger(__name__)

publisher = None
responsers = {}
bulbs = {}

def init():
    with open("setup.conf") as conf_file:
        conf = json.loads(conf_file.read())

    global publisher
    publisher = mq.get_publisher_server(conf["publisher"])
    for address in conf["responseaddr"]:
        response_server = mq.get_response_server(address)
        mq.run_listener(address, response_server, handle_command)
        responsers[address] = response_server
        
    lights.load_config(conf["hardware"])
        
def handle_command(name, msg):
    responsers[name].send_string("ok")
    msg = str(msg)
    cmd = json.loads(msg)
    if type(cmd) == str:
        cmd = json.loads(cmd)
        
    logger.info("Handling command: %s", cmd)
        
    if cmd.get("sync") is not None:
        publisher.send_string(json.dumps({"sync":True, "bulbs":lights.get_all_bulbs()}))
    elif cmd.get("cmd") == "setcolor":
        col = cmd.get("color")
        success = lights.set_color(lights.get_bulbs_by_indexes(cmd.get("bulbs")), col.get("red", 0), col.get("green", 0), col.get("blue", 0), col.get("white", 0))
        if success:
            send_prop_update(cmd.get("bulbs"), "color")
    elif cmd.get("cmd") == "setdimmer":
        dimmer = cmd.get("dimmer")
        success = lights.set_strength(lights.get_bulbs_by_indexes(cmd.get("bulbs")), dimmer)
        if success:
            send_prop_update(cmd.get("bulbs"), "strength")
    elif cmd.get("cmd") == "setmode":
        mode = cmd.get("mode")
        success = lights.set_mode(lights.get_bulbs_by_indexes(cmd.get("bulbs")), mode)
        if success:
            send_prop_update(cmd.get("bulbs"), "mode")
    elif cmd.get("cmd") == "setspeed":
        speed = cmd.get("speed")
        success = lights.set_speed(lights.get_bulbs_by_indexes(cmd.get("bulbs")), speed)
        if success:
            send_prop_update(cmd.get("bulbs"), "speed")
    elif cmd.get("cmd") == "setetd":
        etd = cmd.get("etd")
        success = lights.set_etd(lights.get_bulbs_by_indexes(cmd.get("bulbs")), etd)
        if success:
            send_prop_update(cmd.get("bulbs"), "etd")
    elif cmd.get("cmd") == "connect":
        connected = lights.connect_to_bulb(lights.get_bulb_by_index(cmd.get("bulb")))
        publisher.send_string(json.dumps({"connected": connected, "bulb": cmd.get("bulb")}))
    elif cmd.get("cmd") == "activate":
        success = lights.activate_bulbs(lights.get_bulbs_by_indexes(cmd.get("bulbs")))
        if success:
            send_prop_update(cmd.get("bulbs"), "color")
    elif cmd.get("cmd") == "deactivate":
        success = lights.deactivate_bulbs(lights.get_bulbs_by_indexes(cmd.get("bulbs")))
        if success:
            send_prop_update(cmd.get("bulbs"), "color")
    else:
        print("Got unknown command: ", cmd)
        
def send_prop_update(bulbs, prop):
    publisher.send_string(json.dumps({"update": prop, "value": get_prop_from_bulbs(bulbs, prop), "bulbs": bulbs}))
    
def get_prop_from_bulbs(bulbs, prop):
    res = []
    for index in bulbs:
        bulb = lights.get_bulb_by_index(index)
        res.append(bulb[prop])
    return res