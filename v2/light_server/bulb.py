import logging
import lightwifi
import color

def get_scaled_value(val, max):
    if type(val) == float:
        return int(round(val * max))
    return val

class Bulb(object):

    def __init__(self, id, name, color, strength):
        self.logger = logging.getLogger(__name__)
        self.id = id
        self.name = name
        self.color = color
        self.prev_color = color
        self.strength = min(strength, self.get_max_strength())
        
    def get_id(self):
        return self.id
        
    def get_name(self):
        return self.name
        
    def get_color(self):
        return self.color
        
    def set_color(self, color):
        success = self.set_safe_property("color", color)
        self.prev_color = color
        return success
        
    def get_strength(self):
        return self.strength
        
    def set_strength(self, strength):
        new_strength = get_scaled_value(strength, self.get_max_strength())
        return self.set_safe_property("strength", new_strength)

    def get_max_strength(self):
        return 10
        
    def activate(self):
        return self.set_safe_property("color", self.prev_color)
        
    def deactivate(self):
        if color.colors_equal(self.color, color.get_black_color()):
            return True
        else:    
            self.prev_color = self.color
            return self.set_safe_property("color", color.get_black_color())
        
    def set_safe_property(self, prop, new_value):
        old_value = getattr(self, prop)
        setattr(self, prop, new_value)
        
        print("Update: "+prop)
        print("OldVal: "+str(old_value))
        print("NewVal: "+str(new_value))
        
        success = self.send_update(prop)
        if not success:
            setattr(self, prop, old_value)
        return success
        
    def send_update(self, property):
        self.logger.info("Updated {} of bulb!".format(property))
        return True
        
    def get_bulb_as_data(self):
        return {"id": self.id, "name": self.name, "color": color.get_complete_rgbw_color(self.color), "strength": self.strength}
        
        
        
class WifiBulb(Bulb):

    def __init__(self, id, name, network, color=color.get_black_color(), strength=100):
        Bulb.__init__(self, id, name, color, strength)
        self.network = network
        lightwifi.init_nic_info(self.get_nic())
        
    def get_nic(self):
        return self.network["nic"]
        
    def get_ssid(self):
        return self.network["ssid"]
        
    def get_network_passkey(self):
        return self.network.get("passkey")
        
    def get_network_address(self):
        if self.network["address"] == "broadcast":
            return lightwifi.get_broadcast_address(self.get_nic())
        else:
            return self.network["address"]
        
    def get_network_port(self):
        return self.network["port"]
        
    def connect(self):
        return lightwifi.connect(self.get_ssid(), self.get_network_passkey(), self.get_nic())
        
    def is_connected(self):
        return lightwifi.is_connected(self.get_ssid(), self.get_nic())
        
    def send_message(self, msg):
        if not self.is_connected():
            if not self.connect():
                return False
        lightwifi.send_message(msg, self.get_nic(), self.get_network_address(), self.get_network_port())
        return True

        
    
class ChinaBulb(WifiBulb):
    
    def __init__(self, id, name, network, color=color.get_black_color(), strength=100, mode=0x00, speed=0x04, etd=0x01):
        WifiBulb.__init__(self, id, name, network, color, strength)
        self.mode = mode
        self.speed = speed
        self.etd = etd
        self.identifier = []
        for num in reversed([name[i:i+2] for i in range(3, len(name), 2)]):
            self.identifier.append(int('0x'+num, 16))
        self.identifier.append(0x00)
        
    def get_max_strength(self):
        return 52
        
    def get_mode(self):
        return self.mode
        
    def set_mode(self, mode):
        new_mode = get_scaled_value(mode, self.get_nbr_of_modes())
        return self.set_safe_property("mode", new_mode)
        
    def get_nbr_of_modes(self):
        return 17
        
    def get_speed(self):
        return self.speed
        
    def set_speed(self, speed):
        new_speed = get_scaled_value(speed, self.get_max_speed())
        return self.set_safe_property("speed", new_speed)
        
    def get_max_speed(self):
        return 5
        
    def get_etd(self):
        return self.etd
        
    def set_etd(self, etd):
        new_etd = get_scaled_value(etd, self.get_max_etd())
        return self.set_safe_property("etd", new_etd)
        
    def get_max_etd(self):
        return 64
        
    def send_update(self, property):
        if property == "color":
            return self.send_message(self.get_color_packet_data())
        else:
            return self.send_message(self.get_control_packet_data())
        
    def get_color_packet_data(self):
        full_color = color.get_complete_rgbw_color(self.color)
        return [0xFB, 0xEB, full_color["red"], full_color["green"], full_color["blue"], full_color["white"], 0x00] + self.identifier
                
    def get_control_packet_data(self):
        return [0xFB, 0xEC, self.get_mode(), self.get_speed(), self.get_etd(), 0x02, self.get_strength()] + self.identifier
    
    def get_bulb_as_data(self):
        data = WifiBulb.get_bulb_as_data(self)
        data["mode"] = self.get_mode()/self.get_nbr_of_modes()
        data["speed"] = self.get_speed()/self.get_max_speed()
        data["etd"] = self.get_etd()/self.get_max_etd()
        return data
    
    
