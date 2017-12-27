import RPi.GPIO as GPIO
import logging

TESTPIN = 22
GPIO.setmode(GPIO.BCM)
GPIO.setup(TESTPIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

GPIO.add_event_detect(TESTPIN, GPIO.BOTH)

def test(channel):
    logging.debug("Button got a change of state to "+str(GPIO.input(TESTPIN)))
    
GPIO.add_event_callback(TESTPIN, test)

# Main loop to keep program running
while True:
    cmd = input()
    if cmd == 'end':
        logging.info("Ending button program")
        break
    elif cmd == 'status':
        logging.info("Status: "+str(GPIO.input(TESTPIN)))
