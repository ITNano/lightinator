import button
import ultrasonic
import threading
import logging

# Init UI stuffs
plusArray = []
plusArray.append('');
for i in range(1, 101):
    plusArray.append(plusArray[i-1]+'+')

# Init sensor
usSensor1 = ultrasonic.UltraSonicSensor(23, 24)
button1 = button.Button(id=1, pin=22);
    
def handleButtonPress(button):
    logging.debug('Pressed button with id {}'.format(button.id))
    
def handleButtonRelease(button):
    logging.debug('Released button with id {}'.format(button.id))
        
button1.onPress(handleButtonPress)
button1.onRelease(handleButtonRelease)

def handleMeasureValue(value):
    logging.debug(plusArray[int(value*100)])
    
t = threading.Thread(target=usSensor1.startContinousMeasure, name='UltraSonic 1', args=(10, 100, handleMeasureValue, 5, 120, 5))
t.daemon = True
t.start()

# Main loop to keep program running
while True:
    cmd = input()
    if cmd == 'end':
        logging.info("Ending program")
        usSensor1.stopContinousMeasure()
        ultrasonic.cleanup()
        break