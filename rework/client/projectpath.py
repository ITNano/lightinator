import os

BASE_PATH = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir))

LIB_PATH = os.path.join(BASE_PATH, "client")
SENSOR_PATH = os.path.join(LIB_PATH, "sensors")

CONFIG_PATH = os.path.join(BASE_PATH, ".configuration")