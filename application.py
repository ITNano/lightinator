import lights
from property import Property,BoolProperty

selectedBulbs = []
selectingBulbs = []

def clearConfig():
    lights.unload_config()
    global selectedBulbs
    selectedBulbs = []
    global selectingBulbs
    selectingBulbs = []

def loadConfig(config):
    global selectedBulbs
    global selectingBulbs
    lights.load_config(config)
    selectedBulbs = [Property(False, bool) for i in range(len(lights.get_all_bulbs()))]
    selectingBulbs = [BoolProperty(False, BoolProperty.UP) for i in range(len(lights.get_all_bulbs()))]
    
def isValidIndex(index):
    return index >= 0 and index<len(selectedBulbs)
    
def isSelected(index):
    return isValidIndex(index) and selectedBulbs[index].getValue() == True
    
def addSelectionListener(selectingCallback, selectedCallback, index):
    if isValidIndex(index):
        selectingBulbs[index].addListener(selectingCallback)
        selectedBulbs[index].addListener(selectedCallback)

def selectBulb(index):
    if isValidIndex(index) and not isSelected(index):
        selectingBulbs[index].setValue(True)
        connected = lights.connect_to_bulb(lights.get_bulb_by_index(index))
        selectingBulbs[index].setValue(False)
        # Trigger the change, and then set as it should
        #(in order to always trigger change event)
        selectedBulbs[index].setValue(True)
        if not connected:
            deselectBulb(index)

def deselectBulb(index):
    if isValidIndex(index):
        selectedBulbs[index].setValue(False)
        
def toggleSelect(index):
    if isValidIndex(index):
        if isSelected(index):
            deselectBulb(index)
        else:
            selectBulb(index)
        
def unselectAllBulbs():
    for index in range(len(selectedBulbs)):
        deselectBulb(index)
        
def selectPrevBulb():
    lowestSelected = 0
    for i in range(len(selectedBulbs)):
        if selectedBulbs[i].getValue():
            lowestSelected = i
            break
    unselectAllBulbs()
    selectBulb((lowestSelected-1)%len(selectedBulbs))
    
def selectNextBulb():
    highestSelected = -1
    for i in range(len(selectedBulbs)):
        if selectedBulbs[i].getValue():
            highestSelected = i
    unselectAllBulbs()
    selectBulb((highestSelected+1)%len(selectedBulbs))
    
def getSelectedBulbList():
    bulbs = []
    for index in range(len(selectedBulbs)):
        if selectedBulbs[index].getValue():
            bulbs.append(lights.get_bulb_by_index(index))
    return bulbs
    
def activateBulbs():
    lights.activate_bulbs(getSelectedBulbList())
    
def deactivateBulbs():
    lights.deactivate_bulbs(getSelectedBulbList())
    
def setColor(color):
    lights.set_color(getSelectedBulbList(), color.get("red", 0), color.get("green", 0), color.get("blue", 0), color.get("white", 0))
    
def increaseBrightness(increase=0.1):
    for bulb in getSelectedBulbList():
        lights.set_strength([bulb], int(max(0.0, min(1.0, (bulb["strength"]/lights.MAX_STRENGTH)+increase))*MAX_STRENGTH))
    
def decreaseBrightness(decrease=0.1):
    for bulb in getSelectedBulbList():
        lights.set_strength([bulb], int(max(0.0, min(1.0, (bulb["strength"]/lights.MAX_STRENGTH)-decrease))*MAX_STRENGTH))
    
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