import logging
import json
import projectpath

conf = {}

def load_config():
    global conf
    with open(projectpath.CONFIG_PATH) as conf_file:
        conf = json.load(conf_file)
        
    for name, obj in conf.get("events").items():
        if type(obj) == "str":
            with open(projectpath.get_config_file(obj)) as external_conf_file:
                conf["events"][name] = json.load(external_conf_file)
        
def get_conf(prop):
    return conf[prop]