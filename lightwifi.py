from subprocess import Popen, PIPE, call
from time import sleep

light_wifis = {'CL_CFD4AA':0, 'CL_CFD4BA':1, 'CL_CFD4FA':2};
current_connection = {}

def init_lightwifi(nic='wlan0'):
    args = "sudo iw dev "+nic+" info | grep ssid | sed -e 's/ssid / /g'"
    proc = Popen(args, stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=True)
    output, err = proc.communicate(b"")
    if proc.returncode == 0:
        set_current_connection(nic, output.decode("utf-8").strip())
        print(nic+" connected to : "+get_current_connection(nic))
    else:
        print("No previous connection found")

def get_wifis(nic='wlan0'):
    args = "sudo iw dev wlan0 scan | grep SSID | sort | uniq | sed -e \"s/SSID: / /g\""
    proc = Popen(args, stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=True)
    output, err = proc.communicate(b"")
    if proc.returncode == 0:
        wifis = []
        for wifi in output.decode("utf-8").split("\n"):
            wifis.append(wifi.strip())
        return wifis
    else:
        print("WARNING: Got an error for the WiFi detection command!")
        return []
        
def wifi_online(name, nic='wlan0'):
    return name in get_wifis(nic)
    
def get_current_connection(nic):
    return current_connection[nic]
    
def set_current_connection(nic, name):
    global current_connection
    current_connection[nic] = name
    
def connect(name, nic='wlan0'):
    if get_current_connection(nic) == name:
        return True
        
    if wifi_online(name, nic):
        index = light_wifis.get(name, -1)
        if index >= 0:
            f_in = open('data/wpa_supplicant.conf', 'r')
            template = f_in.read()
            wpa_supplicant_contents = template.format(*get_priority_list(index, len(light_wifis)))
            f_out = open('/etc/wpa_supplicant/wpa_supplicant_lights.conf', 'w')
            chars_written = f_out.write(wpa_supplicant_contents)
            f_out.close()
            if chars_written > 0 or chars_written is None:
                call(["ifdown", nic])
                call(["ifup", nic])
                res = wait_for_wifi_init(nic)
                if not res:
                    set_current_connection(nic, None)
                    print("Warning: WiFi connection might not be ready.")
                else:
                    set_current_connection(nic, name)
                    # Do some extra sleeping...
                    sleep(0.5)
                return res
            else:
                print("Could not add WiFi configuration. Did you really run with sudo?")
                return False
        else:
            raise ValueError("The given WiFi has not been configured in advance: " + name)
    else:
        print("WARNING: Could not connect to WiFi - not found.")
        return False
        
def wait_for_wifi_init(nic='wlan0'):
    counter = 0
    while(counter < 20):
        proc = Popen("ifconfig "+nic+" | grep 'inet addr'", stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=True)
        output, err = proc.communicate(b"")
        if proc.returncode == 0:
            return True
        else:
            sleep(0.5)
        counter += 1
    return False
        
def get_priority_list(active, length):
    res = []
    for i in range(0, length):
        if i == active:
            res.append(2)
        else:
            res.append(1)
    return res
        
if __name__ == "__main__":
    print(get_wifis())
