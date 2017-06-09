
import RPi.GPIO as GPIO
from i2c import ExtensionCard

extensionCards = []
IN = 1
OUT = 0
ON = 1
OFF = 0
PUD_DOWN = GPIO.PUD_DOWN

def init():
    GPIO.setmode(GPIO.BCM)

def addExtensionCard(card):
    if card is not None:
        extensionCards.append(card)
        
def getExtensionCard(pin):
    for card in extensionCards:
        if card.pinIsInCard(pin):
            return card
        
def setDirection(pin, dir, pull_up_down=None):
    cardname = "[card]"
    card = getExtensionCard(pin)
    if card is not None:
        cardname = card.name
        card.setPinDirection(pin, dir)
    else:
        cardname = "GPIO"
        if pull_up_down is None:
            GPIO.setup(pin, dir)
        else:
            GPIO.setup(pin, dir, pull_up_down=pull_up_down)
    print "Pin "+str(pin)+"\t"+cardname+"\t"+("\t"*int(5/len(cardname)))+"DIR="+["OUT", "IN"][dir]          # Adds extra tab if cardname < 5chars
    
def writePin(pin, value):
    card = getExtensionCard(pin)
    if card is not None:
        card.writeBit(pin, value)
    else:
        GPIO.output(pin, value)

def readPin(pin):
    card = getExtensionCard(pin)
    if card is not None:
        return card.readBit(pin)
    else:
        return GPIO.input(pin)
    
def registerForChangeEvent(pin, callback):
    card = getExtensionCard(pin)
    if card is not None:
        print("WARNING: Event detection not yet implemented for extension cards!")
    else:
        GPIO.add_event_detect(pin, GPIO.BOTH)
        GPIO.add_event_callback(pin, callback)
        
def unregisterFromChangeEvent(pin):
    card = getExtensionCard(pin)
    if card is not None:
        print("WARNING: Event detection not yet implemented for extension cards!")
    else:
        GPIO.remove_event_detect(pin)
        
def cleanup():
    global extensionCards
    extensionCards = []
    GPIO.cleanup()
    