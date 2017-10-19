import logging
import RPi.GPIO as GPIO
from i2c import ExtensionCard

print("Someone loaded IOUtil")

extension_cards = []
IN = 1
OUT = 0
ON = 1
OFF = 0
PUD_DOWN = GPIO.PUD_DOWN

def init():
    GPIO.setmode(GPIO.BCM)

def add_extension_card(card):
    if card is not None:
        extension_cards.append(card)
        
def get_extension_card(pin):
    for card in extension_cards:
        if card.pin_is_in_card(pin):
            return card
        
def set_direction(pin, dir, pull_up_down=None):
    cardname = "[card]"
    card = get_extension_card(pin)
    if card is not None:
        cardname = card.name
        card.set_pin_direction(pin, dir)
    else:
        cardname = "GPIO"
        if pull_up_down is None:
            GPIO.setup(pin, dir)
        else:
            GPIO.setup(pin, dir, pull_up_down=pull_up_down)
    logging.debug("Pin {0}\t{1}\t{2}DIR={3}".format(pin, cardname, "\t"*int(5/len(cardname)), ["OUT", "IN"][dir]))       # Adds extra tab if cardname < 5chars
    
def write_pin(pin, value):
    card = get_extension_card(pin)
    if card is not None:
        card.write_bit(pin, value)
    else:
        GPIO.output(pin, value)

def read_pin(pin):
    card = get_extension_card(pin)
    if card is not None:
        return card.read_bit(pin)
    else:
        return GPIO.input(pin)
    
def register_for_change_event(pin, callback):
    card = get_extension_card(pin)
    if card is not None:
        logging.warning("WARNING: Event detection not yet implemented for extension cards!")
    else:
        GPIO.add_event_detect(pin, GPIO.BOTH)
        GPIO.add_event_callback(pin, callback)
        
def unregister_from_change_event(pin):
    card = get_extension_card(pin)
    if card is not None:
        logging.warning("WARNING: Event detection not yet implemented for extension cards!")
    else:
        GPIO.remove_event_detect(pin)
        
def cleanup():
    global extension_cards
    extension_cards = []
    GPIO.cleanup()
    