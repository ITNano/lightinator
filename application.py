import lights

selectedBulbs = []

def loadConfig(config):
    global selectedBulbs
    lights.load_config(config)
    selectedBulbs = [False]*len(lights.get_all_bulbs())

def selectBulb(index):
    if index >= 0 and index<len(selectedBulbs):
	    selectedBulbs[index] = True

def deselectBulb(index):
    if index >= 0 and index<len(selectedBulbs):
	    selectedBulbs[index] = False
        
def toggleSelect(index):
    if index >= 0 and index<len(selectedBulbs):
	    selectedBulbs[index] = not selectedBulbs[index]
        
def unselectAllBulbs():
    for index in range(len(selectedBulbs)):
        selectedBulbs[index] = False
        
def selectPrevBulb():
    lowestSelected = 1
    for i in range(len(selectedBulbs)):
        if selectedBulbs[i]:
            lowestSelected = i
    unselectAllBulbs()
    selectBulb((lowestSelected-1)%len(selectedBulbs))
    
def selectNextBulb():
    highestSelected = -1
    for i in range(len(selectedBulbs)):
        if selectedBulbs[i]:
            highestSelected = i
    unselectAllBulbs()
    selectBulb((highestSelected+1)%len(selectedBulbs))
    
def getSelectedBulbList():
    bulbs = []
    for index in range(len(selectedBulbs)):
        if selectedBulbs[index]:
            bulbs.append(lights.get_bulb_by_index(index))
    return bulbs
    
def activateBulbs():
    lights.activate_bulbs(getSelectedBulbList())
    
def deactivateBulbs():
    lights.deactivate_bulbs(getSelectedBulbList())
    
def setColor(red, green, blue):
    lights.set_color(getSelectedBulbList(), red, green, blue, 0, -1)
    
def increaseBrightness(increase=0.1):
    for bulb in getSelectedBulbList():
        lights.set_color([bulb], bulb["color"][0], bulb["color"][1], bulb["color"][2], bulb["color"][3], max(0, min(1, (bulb["color"][4]/255.0)+increase))*255)
    
def decreaseBrightness(decrease=0.1):
    for bulb in getSelectedBulbList():
        lights.set_color([bulb], bulb["color"][0], bulb["color"][1], bulb["color"][2], bulb["color"][3], max(0, min(1, (bulb["color"][4]/255.0  )-decrease))*255)
    
def setBrightness(brightness):
    for bulb in getSelectedBulbList():
        lights.set_color([bulb], bulb["color"][0], bulb["color"][1], bulb["color"][2], bulb["color"][3], int(max(0, min(1, brightness))*255))
