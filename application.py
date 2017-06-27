import util
import lights
import json
import sound
from property import Property,BoolProperty
import resourcelist
import msgqueue
import sys


selectedBulbs = resourcelist.MultiChoiceResourceList(data=[])

def clearConfig():
    lights.unload_config()
    global selectedBulbs
    selectedBulbs = resourcelist.MultiChoiceResourceList(data=[])

def loadConfig(config):
    global selectedBulbs
    lights.load_config(config)
    selectedBulbs = resourcelist.MultiChoiceResourceList(data=lights.get_all_bulbs())
    
def receiveCommand(src, commands):
    print "Got a command: {}".format(commands)
    handleCommands(json.loads(commands))
    
def handleCommands(commandList):
    for command in commandList:
        ## Handle command here ##
        if command is not None:
            cmd = command.get("command")
            if cmd == "loadhardware":
                loadConfig(command.get("hardware"))
            elif cmd == "clearconfig":
                clearConfig()
            elif cmd == "registerreslist":
                resourcelist.registerList(command["name"], resourcelist.ResourceList(command["list"], command.get("start", 0)))
            elif cmd == "loadsound":
                sound.loadSound(command["name"], command["path"], command.get("start", 0), command.get("end", 0))
            elif cmd == "setcolor":
                if command.get("color") is not None:
                    color = command.get("color")
                elif command.get("colorlist") is not None:
                    colorlist = resourcelist.getListByName("colorlist_{0}".format(command.get("colorlist")))
                    if colorlist is not None:
                        mode = {"value": "scale"}.get(command.get("mode"), command.get("mode"))
                        colorlist.select(mode, command.get("value"))
                        color = colorlist.getSelectedData()
                setColor(color)
            elif cmd == "setdimmer":
                mode = command.get("mode")
                if mode == "relative":
                    increaseBrightness(command.get("value"))
                elif mode == "absolute" or mode == "scale":
                    setBrightness(command.get("value"))
            elif cmd == "setmode":
                mode = command.get("mode")
                if mode == "absolute" or mode == "value":
                    setMode(command.get("value"))
            elif cmd == "setspeed":
                mode = command.get("mode")
                if mode == "absolute" or mode == "value":
                    setSpeed(command.get("value"))
            elif cmd == "setetd":
                mode = command.get("mode")
                if mode == "absolute" or mode == "value":
                    setEffectTimeDifference(command.get("value"))
            elif cmd == "select":
                for value in util.getList(command.get("value")):
                    index = selectedBulbs.select(command.get("mode"), value)
                    if index is not None:
                        connected = lights.connect_to_bulb(lights.get_bulb_by_index(index))
                        if not connected:
                            selectedBulbs.unselect(index)
            elif cmd == "unselect":
                for index in util.getList(command.get("value")):
                    selectedBulbs.unselect(index)
            elif cmd == "toggleselect":
                for value in util.getList(command.get("value")):
                    selectedBulbs.toggleSelect(value)
            elif cmd == "activate":
                activateBulbs()
            elif cmd == "deactivate":
                deactivateBulbs()
            elif cmd == "stopsounds":
                sound.stopSounds()
            elif cmd == "restartnic":
                util.resetNICs(command.get('nic', 'wlan'))
            
            if command.get("sound") is not None:
                sound.playSound(command.get("sound"), command.get('loop'))
            elif command.get("soundlist") is not None:
                soundlist = resourcelist.getListByName("soundlist_{0}".format(command.get("soundlist")))
                soundlist.select(command.get("soundmode"), command.get("soundvalue"))
                sound.playSound(soundlist.getSelectedData(), command.get('loop'))
                
    print("All commands has now been handled")
    
def isValidIndex(index):
    return index >= 0 and index<selectedBulbs.size()
    
def addSelectionListener(selectingCallback, selectedCallback, index):
    if isValidIndex(index):
        selectedBulbs.selected[index].addListener(selectedCallback)
    
def getSelectedBulbList():
    return [lights.get_bulb_by_name(bulb["name"]) for bulb in selectedBulbs.getSelectedData()]
    
def activateBulbs():
    lights.activate_bulbs(getSelectedBulbList())
    
def deactivateBulbs():
    lights.deactivate_bulbs(getSelectedBulbList())
    
def setColor(color):
    lights.set_color(getSelectedBulbList(), color.get("red", 0), color.get("green", 0), color.get("blue", 0), color.get("white", 0))
    
def increaseBrightness(increase=0.1):
    for bulb in getSelectedBulbList():
        lights.set_strength([bulb], int(max(0.0, min(1.0, (bulb["strength"]/lights.MAX_STRENGTH)+increase))*MAX_STRENGTH))
    
def setBrightness(brightness):
    for bulb in getSelectedBulbList():
        lights.set_strength([bulb], int(max(0.0, min(1.0, brightness))*lights.MAX_STRENGTH))

def setMode(mode):
    if type(mode) == float:
        lights.set_mode(getSelectedBulbList(), int(mode*lights.NBR_OF_MODES))
    else:
        lights.set_mode(getSelectedBulbList(), mode)
    
def setSpeed(speed):
    if type(speed) == float:
        lights.set_speed(getSelectedBulbList(), int(speed*lights.MAX_SPEED))
    else:
        lights.set_speed(getSelectedBulbList(), speed)
        
def setEffectTimeDifference(etd):
    if type(etd) == float:
        lights.set_effect_time_difference(getSelectedBulbList(), int(etd*lights.MAX_ETD))
    else:
        lights.set_effect_time_difference(getSelectedBulbList(), etd)
        
if __name__ == "__main__":
    if len(sys.argv) == 3:
        msgqueue.runServer(msgqueue.getAddress(sys.argv[1], sys.argv[2]), receiveCommand)
        while True:
            cmd = raw_input()
            if cmd == "end":
                break
    else:
        print("Invalid call. Usage: python application.py [protocol] [address or path]")