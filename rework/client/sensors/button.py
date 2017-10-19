from sensor import Sensor
import event

class Button(Sensor):

    def __init__(self, id, pin, power=0, holdInterval=1):
        Sensor.__init__(self, id)
        self.pin = pin
        self.power = power
        self.holdInterval = holdInterval
        self.holdTime = 0
    
    def check_valid(self, event_name, command):
        success = True
        if event_name == "hold":
            if command.get("holdMinInclusive") is not None:
                success = success and self.holdTime >= float(command["holdMinInclusive"])
            elif command.get("holdMin") is not None:
                success = success and self.holdTime > float(command["holdMin"])
            elif command.get("holdMaxInclusive") is not None:
                success = success and self.holdTime <= float(command["holdMaxInclusive"])
            elif command.get("holdMax") is not None:
                success = success and self.holdTime < float(command["holdMax"])
            
        return success
        