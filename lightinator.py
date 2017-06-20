import button
import ultrasonic
import ir
from led import LED
from i2c import ExtensionCard
from property import BoolProperty
import ioutil
import sound
import util
import application
import threading
import json
import math

sensors = []
irSensor = None
events = {}
colorLists = {}
services = {"button": BoolProperty(True), "ultrasonic": BoolProperty(True), "ir": BoolProperty(True)}
state = "default"

def evaluateCommand(commandList, sensor, allowCommands):
    if commandList is None:
        return
        
    if not type(commandList) is list:
        commandList = [commandList]
        
    for command in commandList:
        ## Handle command here ##
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
                elif cmd == "setcolor":
                    if command.get("color") is not None:
                        color = command.get("color")
                    elif command.get("colorlist") is not None:
                        mode = command.get("mode")
                        name = command.get("colorlist")
                        if mode == "relative":
                            setColorListIndex(name, getColorListIndex(name) + command.get("value"))
                        elif mode == "value":
                            setColorListIndex(name, (len(colorLists.get(name)["colors"])-1)*sensor.getValue())
                        elif mode == "absolute":
                            setColorListIndex(name, command.get("value"))
                        color = getColorFromList(name)
                    application.setColor(color)
                elif cmd == "setdimmer":
                    mode = command.get("mode")
                    if mode == "relative":
                        application.increaseBrightness(command.get("value"))
                    elif mode == "absolute":
                        application.setBrightness(command.get("value"))
                    elif mode == "value":
                        application.setBrightness(sensor.getValue())
                elif cmd == "setmode":
                    mode = command.get("mode")
                    if mode == "absolute":
                        application.setMode(command.get("value"))
                    elif mode == "value":
                        application.setMode(sensor.getValue())
                elif cmd == "setspeed":
                    mode = command.get("mode")
                    if mode == "absolute":
                        application.setSpeed(command.get("value"))
                    elif mode == "value":
                        application.setSpeed(sensor.getValue())
                elif cmd == "setetd":
                    mode = command.get("mode")
                    if mode == "absolute":
                        application.setEffectTimeDifference(command.get("value"))
                    elif mode == "value":
                        application.setEffectTimeDifference(sensor.getValue())
                elif cmd == "select":
                    mode = command.get("mode")
                    if mode == "relative":
                        value = command.get("value")
                        while(value != 0):
                            if value < 0:
                                application.selectPrevBulb()
                                value += 1
                            else:
                                application.selectNextBulb()
                                value -= 1
                    elif mode == "absolute":
                        value = command.get("value")
                        if not type(value) is list:
                            value = [value]
                        for val in value:
                            application.selectBulb(val)
                elif cmd == "unselect":
                    mode = command.get("mode")
                    if mode == "absolute":
                        value = command.get("value")
                        if not type(value) is list:
                            value = [value]
                        for val in value:
                            application.unselectBulb(val)
                elif cmd == "toggleselect":
                    mode = command.get("mode")
                    if mode == "absolute":
                        value = command.get("value")
                        if not type(value) is list:
                            value = [value]
                        for val in value:
                            application.toggleSelect(val)
                elif cmd == "activate":
                    application.activateBulbs()
                elif cmd == "deactivate":
                    application.deactivateBulbs()
                elif cmd == "stopsounds":
                    sound.stopSounds()
                elif cmd == "restartnic":
                    util.resetNICs(command.get('nic', 'wlan'))
                
                if command.get("sound") is not None:
                    sound.playSound(command.get("sound"), command.get('loop'))
        
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
    
def getColorListIndex(name):
    return colorLists.get(name)["current"]
    
def setColorListIndex(name, index):
    colorLists.get(name)["current"] = int(math.floor(index)) % len(colorLists.get(name)["colors"])
    
def getColorFromList(name):
    return colorLists.get(name)["colors"][colorLists.get(name)["current"]]

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
     
def loadConfiguration(file):     
    with open(file) as conf_file:    
        configuration = byteify(json.load(conf_file))
        
    print("Using configuration by %s from %s (version %s)" % (configuration["author"], configuration["date"], configuration["version"]))
    
    if configuration.get("debug") is not None and configuration["debug"].lower() == "on":
        sound.DEBUG = True
    
    application.loadConfig(configuration["hardware"])
    print "Loaded hardware specs"

    global colorLists
    colorLists = {key: {"colors":configuration["colors"][key], "current": 0} for key in configuration["colors"]}
    print "Loaded color lists"
    
    if configuration.get("sounds") is not None:
        for clip in configuration["sounds"]:
            sound.loadSound(clip["name"], clip["path"], clip.get("start"), clip.get("end"))
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
                application.addSelectionListener(led.blink, led.setValue, item["bindkey"])
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
    application.clearConfig()
    sound.cleanup()
    
def cleanup():
    for sensor in sensors:
        sensor.terminate()
    ioutil.cleanup()

#####################################################
# ------------------ MAIN LOOP -------------------- #
#####################################################
try:
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
                application.setColor({"red":int(data[1]), "green":int(data[2]), "blue":int(data[3])})
except Exception as e:
    print("Caught an exception during runtime, shutting down. Error as given below.")
    cleanup()
    raise e
    
