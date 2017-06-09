import sys
sys.path.append("./Adafruit_Python_GPIO")
sys.path.append("./Adafruit_Python_PureIO")
import Adafruit_GPIO.I2C as I2C

class ExtensionCard(object):
    
    def __init__(self, addr, startpin, registers, name="noname"):
        if registers is None:
            raise ValueError('Registers must be defined')
            
        self.device = I2C.get_i2c_device(addr)
        self.name = name
        self.startpin = startpin
        self.endpin = self.startpin+getNumberOfPins(registers)-1
        self.initRegisters(registers)
        
    def initRegisters(self, registers):
        self.registers = registers
        index = self.startpin
        for register in self.registers:
            # Handle size
            register['size'] = register.get('size', 8)
            register['startpin'] = index
            # Handle initial values
            register['value'] = register.get('initval', 0x00)
            register['dirvalue'] = 0x00
            self.writeRegister(register, register['value'])
            if register.get('initval') is not None:
                del register['initval']
            # Prepare for next round
            index = index + register['size']
        
    def pinIsInCard(self, pinNumber):
        return pinNumber >= self.startpin and pinNumber <= self.endpin
        
    def findRegister(self, pin):
        index = self.startpin
        for register in self.registers:
            if pin >= index and pin < index+register['size']:
                return register
            index = index + register['size']
        return None
        
    def writeRegister(self, register, value, data=True):
        # Select register function.
        addr = register['datareg']
        if not data:
            addr = register['dirreg']
            
        # Actual write
        print self.name+" ACTUALLY writing "+"{0:b}".format(value)+" to addr "+str(addr)
        if register['size'] <= 8:
            self.device.write8(addr, value)
        else:
            self.device.write16(addr, value)
            
        # Save result
        if data:
            register['value'] = value
        else:
            register['dirvalue'] = value
            
    def readRegister(self, register):
        if register['size'] <= 8:
            return self.device.readU8(register['datareg'])
        else:
            return self.device.readU16(register['datareg'])
        
    def writeBit(self, pin, value):
        print self.name+" writing "+str(value)+" to pin "+str(pin)
        if self.pinIsInCard(pin):
            register = self.findRegister(pin)
            bitmask = ~(0x01 << (pin-register['startpin']))
            valuemask = value << (pin-register['startpin'])
            self.writeRegister(register, (register['value'] & bitmask) | valuemask)
            
    def readBit(self, pin):
        if self.pinIsInCard(pin):
            register = self.findRegister(pin)
            index = pin-register['startpin']
            return (self.readRegister(register) >> index) & 0x01
            
    def setPinDirection(self, pin, value):
        if self.pinIsInCard(pin):
            register = self.findRegister(pin)
            bitmask = ~(0x01 << (pin-register['startpin']))
            valuemask = value << (pin-register['startpin'])
            self.writeRegister(register, (register['dirvalue'] & bitmask) | valuemask, False)
            
def getNumberOfPins(registers):
    count = 0
    for register in registers:
        count = count + register.get('size', 8)
    return count
