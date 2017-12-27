import logging
import sys
import projectpath
sys.path.append(projectpath.GPIO_PATH)
sys.path.append(projectpath.PUREIO_PATH)
import Adafruit_GPIO.I2C as I2C

class ExtensionCard(object):
    
    def __init__(self, address, startpin, registers, name="noname"):
        if registers is None:
            raise ValueError('Registers must be defined')
            
        self.logger = logging.getLogger(__name__)
        self.name = name
        self.startpin = startpin
        self.endpin = self.startpin+get_number_of_pins(registers)-1
        
        try:
            self.device = I2C.get_i2c_device(address)
            self.init_registers(registers)
        except:
            self.device = None
            self.logger.error("Could not find extension card with name %s", name)
        
    def init_registers(self, registers):
        self.registers = registers
        index = self.startpin
        for register in self.registers:
            # Handle size
            register['size'] = register.get('size', 8)
            register['startpin'] = index
            # Handle initial values
            register['value'] = register.get('initval', 0x00)
            register['dirvalue'] = 0x00
            self.write_register(register, register['value'])
            if register.get('initval') is not None:
                del register['initval']
            # Prepare for next round
            index = index + register['size']
        
    def pin_is_in_card(self, pin_number):
        return self.device is not None and pin_number >= self.startpin and pin_number <= self.endpin
        
    def find_register(self, pin):
        index = self.startpin
        for register in self.registers:
            if pin >= index and pin < index+register['size']:
                return register
            index = index + register['size']
        return None
        
    def write_register(self, register, value, data=True):
        # Select register function.
        addr = register['datareg']
        if not data:
            addr = register['dirreg']
            
        # Actual write
        if register['size'] <= 8:
            self.device.write8(addr, value)
        else:
            self.device.write16(addr, value)
            
        # Save result
        if data:
            register['value'] = value
        else:
            register['dirvalue'] = value
            
    def read_register(self, register):
        if register['size'] <= 8:
            return self.device.readU8(register['datareg'])
        else:
            return self.device.readU16(register['datareg'])
        
    def write_bit(self, pin, value):
        value = normalize_value(value)
        if self.pin_is_in_card(pin):
            register = self.find_register(pin)
            bitmask = ~(0x01 << (pin-register['startpin']))
            valuemask = value << (pin-register['startpin'])
            self.write_register(register, (register['value'] & bitmask) | valuemask)
            
    def read_bit(self, pin):
        if self.pin_is_in_card(pin):
            register = self.find_register(pin)
            index = pin-register['startpin']
            return (self.read_register(register) >> index) & 0x01
            
    def set_pin_direction(self, pin, value):
        if self.pin_is_in_card(pin):
            register = self.find_register(pin)
            bitmask = ~(0x01 << (pin-register['startpin']))
            valuemask = value << (pin-register['startpin'])
            self.write_register(register, (register['dirvalue'] & bitmask) | valuemask, False)
          
def normalize_value(value):
    if value is False or value is 0:
        return 0
    else:
        return 1
          
def get_number_of_pins(registers):
    count = 0
    for register in registers:
        count = count + register.get('size', 8)
    return count
