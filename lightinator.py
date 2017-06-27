import button
import ultrasonic
import ir
from led import LED
from i2c import ExtensionCard
from property import BoolProperty
import ioutil
import sound
import util
import threading
import json
import math
import time
import msgqueue
import traceback

sensors = []
irSensor = None
events = {}
services = {"button": BoolProperty(True), "ultrasonic": BoolProperty(True), "ir": BoolProperty(True)}
state = "default"
connection = None

def evaluateCommand(commandList, sensor, allowCommands):
    if commandList is None:
        return
        
    # Do internal command functionality
    externalCommands = []
    for command in util.getList(commandList):
        if command is not None:
            cmd = command.get("command")
            if cmd == "toggleservice":
                services[command.get("service")].setValue(not services[command.get("service")].getValue())
                print("Service state ["+command.get("service")+"]: "+str(services[command.get("service")].getValue()))
            elif allowCommands:
                if cmd == "setstate":
                    global state
                    state = command["state"]
                    print "Using state '{}'".format(state)
                else:
                    externalCommands.append(command)
            else:
                externalCommands.append(command)
    
    # Do external command handling (at light server)
    if allowCommands:
        for command in externalCommands:
            if command.get("mode") is not None and command["mode"] == "value":
                command["value"] = sensor.getValue()
            if command.get("soundmode") is not None and command["soundmode"] == "value":
                command["soundvalue"] = sensor.getValue()
        sendCommands(externalCommands)
        
def buttonPressed(button):
    commandList = getCommandList(button, "onpress")
    evaluateCommand(commandList, button, services["button"].getValue())
    
def buttonReleased(button, holdTime):
    commandList = getCommandList(button, "onrelease")
    if commandList is not None:
        onButtonTimeEvent(button, commandList, holdTime)
        
def buttonHold(button, holdTime):
    commandList = getCommandList(button, "onhold")
    if commandList is not None:
        onButtonTimeEvent(button, commandList, holdTime)

def onButtonTimeEvent(button, commandList, holdTime):
    if not type(commandList) is list:
        commandList = [commandList]
    
    for command in commandList:
        valid = True
        if command.get("holdMax") is not None:
            valid &= holdTime < command.get("holdMax")
        if command.get("holdMaxInclusive") is not None:
            valid &= holdTime <= command.get("holdMaxInclusive")
        if command.get("holdMin") is not None:
            valid &= holdTime > command.get("holdMin")
        if command.get("holdMinInclusive") is not None:
            valid &= holdTime >= command.get("holdMinInclusive")
        if valid:
            evaluateCommand(command, button, services["button"].getValue())
    
def ultrasonicChanged(ultrasonic, value):
    commandList = getCommandList(ultrasonic, "onchange")
    evaluateCommand(commandList, ultrasonic, services["ultrasonic"].getValue())
    
def irKeyPress(trigger):
    commandList = getCommandList(irSensor, "onpress")
    if not type(commandList) is list:
        commandList = [commandList]
    
    triggered = False
    for command in commandList:
        if command.get("key") == trigger:
            triggered = True
            evaluateCommand(command, irSensor, services["ir"].getValue())
            
    # If no custom event was triggered, try to use 'default' as trigger
    if not triggered and trigger != "default":
        irKeyPress("default")
    
def getCommandList(sensor, eventType):
    print "{} active".format(sensor.id)
    eventKey = "default"
    if events.get(state) is not None:
        eventKey = state
    return events[eventKey].get("{}.{}".format(sensor.id, eventType))
   
def byteify(input):
    if isinstance(input, dict):
        return {byteify(key): byteify(value)
                for key, value in input.iteritems()}
    elif isinstance(input, list):
        return [byteify(element) for element in input]
    elif isinstance(input, unicode):
        return input.encode('utf-8')
    else:
        return input
        
def setConnection(addr):
    resetConnection()
    global connection
    connection = msgqueue.getClientConn(addr)
    
def resetConnection():
    if connection is not None:
        connection.close()

def sendCommands(commands):
    connection.send(json.dumps(util.getList(commands)))
     
def loadConfiguration(file):     
    with open(file) as conf_file:    
        configuration = byteify(json.load(conf_file))
        
    print("Using configuration by %s from %s (version %s)" % (configuration["author"], configuration["date"], configuration["version"]))
    
    if configuration.get("debug") is not None and configuration["debug"].lower() == "on":
        sound.DEBUG = True
        
    server = configuration["server"]
    if server["protocol"].lower() == "tcp":
        setConnection(msgqueue.getTcpAddress(server["ip"], server["port"]))
    elif server["protocol"].lower() == "icp":
        setConnection(msgqueue.getIcpAddress(server["path"]))
    print("Waiting for server connection to be established...")
    time.sleep(2)
    print("Connection established (probably)")
    
    sendCommands({"command": "loadhardware", "hardware": configuration["hardware"]})
    print "Loaded hardware specs"

    if configuration.get("colors") is not None:
        commands = [{"command": "registerreslist", "name": "colorlist_{}".format(name), "list": configuration["colors"][name], "start": 0} for name in configuration["colors"]]
        sendCommands(commands)
        print "Loaded color lists"
    
    if configuration.get("sounds") is not None:
        commands = [{"command": "loadsound", "name": clip["name"], "path": clip["path"], "start": clip.get("start", 0), "end": clip.get("end", 0)} for clip in configuration["sounds"]]
        sendCommands(commands)
        print "Loaded sounds"

    ioutil.init()
    if configuration.get("extensioncards") is not None:
        for card in configuration["extensioncards"]:
            ioutil.addExtensionCard(ExtensionCard(card['address'], card['startpin'], card['registers'], card.get("name", "unknown")))
    print "Loaded extension cards"
    
    print "Registering events..."
    global events
    events = configuration["events"]
    print "Events registered."
    
    leds = 0
    print "Allocating input sensors..."
    for item in configuration["inputs"]:
        if item["type"] == "button":
            b = button.Button(iolib=ioutil, id=item["id"], pin=item["pin"], power=item.get("power"), holdInterval=item.get("holdTime", 1))
            b.onPress(buttonPressed)
            b.onRelease(buttonReleased)
            b.onHold(buttonHold)
            sensors.append(b)
        elif item["type"] == "ultrasonic":
            usSensor = ultrasonic.UltraSonicSensor(iolib=ioutil, id=item["id"], trigger=item["trigger"], echo=item["echo"])
            t = threading.Thread(target=usSensor.startContinousMeasure, name="UltraSonic "+str(usSensor.id), args=(item["minDetect"], item["maxDetect"], ultrasonicChanged, item.get("minSleep", -1), item.get("maxSleep", -1), item.get("sleepTimes", -1)))
            t.daemon = True
            t.start()
            sensors.append(usSensor)
        elif item["type"] == "ir":
            global irSensor
            if irSensor is not None:
                raise ValueError("Only one IR receiver allowed")
            irSensor = ir.InfraRedSensor(id="ir")
            irSensor.addListener(irKeyPress)
            irSensor.startListen()
            sensors.append(irSensor)
        elif item["type"] == "led":
            led = LED(iolib=ioutil, id=leds, pin=item["pin"])
            if item["bind"] == "selection":
                # FIXME
                # application.addSelectionListener(led.blink, led.setValue, item["bindkey"])
                pass
            elif item["bind"] == "service":
                services[item["bindkey"]].addListener(led.setValue)
    print "Loaded input sensors"

def unloadConfiguration():
    # Cleanup GPIO and sensors
    cleanup()
    
    # Reset variables
    for key in services:
        services[key] = BoolProperty(True)
    global sensors
    sensors = []
    global events
    events = {}
    global colorLists
    colorLists = {}
    global irSensor
    irSensor = None
    
    # Clear subconfigs
    sendCommands({"command": "clearconfig"})
    sound.cleanup()
    
def cleanup():
    for sensor in sensors:
        sensor.terminate()
    ioutil.cleanup()

#####################################################
# ------------------ MAIN LOOP -------------------- #
#####################################################
#try:
    # Main loop to keep program running
configFile = "conf/lightinator.conf"
loadConfiguration(configFile)
while True:
    cmd = raw_input()
    if cmd == 'end':
        print("Ending program")
        unloadConfiguration()
        break
    elif cmd == 'selection':
        print(application.getSelectedBulbList())
    elif cmd == 'restart':
        evaluateCommand([{'command':'restartnic'}], None, True)
    elif cmd == 'reload':
        unloadConfiguration()
        print("")
        loadConfiguration(configFile)
    elif cmd[:7] == "trigger":
        parts = cmd.split(" ")
        found = False
        for sensor in sensors:
            if sensor.id == parts[1]:
                for i in range(2, len(parts)):
                    evaluateCommand(getCommandList(sensor, parts[i]), sensor, True)
                found = True
                break
        if not found:
            print "Could not find device with ID "+str(parts[1])
    elif cmd[:5] == "color":
        if len(cmd.split()) == 4:
            data = cmd.split()
            sendCommands({"command": "setcolor", "color":{"red":int(data[1]), "green":int(data[2]), "blue":int(data[3])}})
#except Exception as e:
#    print("Caught an exception during runtime, shutting down. Error as given below.")
#    cleanup()
#    traceback.print_exc()
    
