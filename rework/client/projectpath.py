import os

BASE_PATH = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir))

LIB_PATH = os.path.join(BASE_PATH, "client")

SENSOR_PATH = os.path.join(LIB_PATH, "sensors")
STATUS_INDICATOR_PATH = os.path.join(LIB_PATH, "outsensors")
FUNC_PATH = os.path.join(LIB_PATH, "functionality")

CONFIG_PATH = os.path.join(BASE_PATH, "main.conf")

def get_config_file(name):
    return os.path.join(BASE_PATH, name)