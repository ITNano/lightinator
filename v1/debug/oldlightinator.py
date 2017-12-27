import button
import ultrasonic
import ir
import application
import threading
import logging

# Init sensor
usSensor1 = ultrasonic.UltraSonicSensor(id=1, trigger=23, echo=24)
buttonSel1 = button.Button(id=1, pin=22)
irSensor = ir.InfraRedSensor(id=1)

active = True
buttonColors = [[255, 0, 0], [0, 255, 0], [0, 0, 255], [255, 255, 0]]
ultrasonicColors = [[0, 0, 0], [255, 0, 0], [0, 255, 0], [0, 0, 255], [255, 255, 0], [0, 200, 80], [20, 20, 20], [150, 0, 150], [0, 0, 0]]
currentColorIndex = 0

#####################################################
# ------------------ BUTTONS ---------------------- #
#####################################################
def handleButtonPress(button):
    if button.id == 1:
        #application.toggleSelect(0)
        application.setColor(255, 0, 0)
    elif button.id == 2:
        application.toggleSelect(1)
    elif button.id == 3:
        application.toggleSelect(2)
    elif button.id == 4:
        application.activateBulbs()
    elif button.id == 5:
        application.deactivateBulbs()
    elif button.id >= 6 and button.id <= 9:
        color = buttonColors[button.id-6]
        application.setColor(color[0], color[1], color[2])

def handleButtonRelease(button, pressTime):
    logging.info('Released button with id ',button.id)

buttonSel1.onPress(handleButtonPress)
buttonSel1.onRelease(handleButtonRelease)


#####################################################
# ------------------ ULTRASONIC ------------------- #
#####################################################
def handleDimmerValue(sensor, value):
    application.setBrightness(value)

def handleRainbowColorSelect(sensor, value):
    color = ultrasonicColors[int(value*(len(ultrasonicColors)-1))]
    application.setColor(color[0], color[1], color[2])
    
t = threading.Thread(target=usSensor1.startContinousMeasure, name='UltraSonic 1', args=(4, 50, handleRainbowColorSelect, 5, 120, 5))
t.daemon = True
t.start()


#####################################################
# ------------------ IR CONTROL ------------------- #
#####################################################
def handleIREvent(sensor, event):
    global active
    global currentColorIndex
    if event == "toggleActive":
        active = not active
    elif active:
        if event == "right":
            application.selectNextBulb()
        elif event == "left":
            application.selectPrevBulb()
        elif event == "up":
            #application.increaseBrightness()
            currentColorIndex = (currentColorIndex+1)%len(ultrasonicColors)
            color = ultrasonicColors[currentColorIndex]
            application.setColor(color[0], color[1], color[2])
        elif event == "down":
            #application.decreaseBrightness()
            currentColorIndex = (currentColorIndex-1)%len(ultrasonicColors)
            color = ultrasonicColors[currentColorIndex]
            application.setColor(color[0], color[1], color[2])

irSensor.addListener(handleIREvent)
irSensor.startListen()


#####################################################
# ------------------ MAIN LOOP -------------------- #
#####################################################
# Main loop to keep program running
while True:
    cmd = raw_input()
    if cmd == 'end':
        logging.info("Ending program")
        usSensor1.stopContinousMeasure()
        ultrasonic.cleanup()
        irSensor.removeListener(handleIREvent)
        irSensor.destroy()
        break
    elif cmd == 'red':
        application.setColor(255,0,0)
    elif cmd[:5] == "color":
        if len(cmd.split()) == 4:
            data = cmd.split()
            application.setColor(int(data[1]), int(data[2]), int(data[3]))
