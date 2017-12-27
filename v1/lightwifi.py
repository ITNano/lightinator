from subprocess import Popen, PIPE, call
from time import sleep
from util import *
import logging

light_wifis = {}
current_connection = {}
registered_networks = {}
        
def register_network(network, nic='wlan0'):
    if registered_networks.get(nic) is None:
        registered_networks[nic] = []
    registered_networks[nic].append(network)
    
def unregister_all_networks():
    global registered_networks
    registered_networks = {}
    global light_wifis
    light_wifis = {}
    
def prepare_for_connections():
    base_wpa_supplicant = readFile('data/wpa_supplicant_base.conf')
    base_interfaces = readFile('data/interfaces_base')
    interfaces = base_interfaces
    network_counter = 0
    for nic in registered_networks:
        # Handle general setup for NIC
        interfaces = interfaces + "allow-hotplug {0}\niface {0} inet manual\n\twpa-conf /etc/wpa_supplicant/wpa_supplicant_{0}.conf\n\n".format(nic)
        # Handle each individual network
        nic_wpa_supplicant = base_wpa_supplicant
        for network in registered_networks[nic]:
            nic_wpa_supplicant = nic_wpa_supplicant + "network={{{{\n\tssid=\"{0}\"\n\tkey_mgmt=NONE\n\tid_str=\"Bulb_{0}\"\n\tpriority={{}}\n}}}}\n\n".format(network["name"])
            interfaces = interfaces + "iface Bulb_{} inet static\n\taddress {}\n\tgateway {}\n\tnetmask {}\n\n".format(network["name"], network["address"], network["gateway"], network["mask"])
            light_wifis[network["name"]] = network_counter
            network_counter = network_counter+1
        # Write to temporary template file and system folder
        writeFile('data/tmp/wpa_supplicant_{}.conf'.format(nic), nic_wpa_supplicant)
        actual_contents = nic_wpa_supplicant.format(*get_priority_list(-1, len(light_wifis)))
        writeFile('/etc/wpa_supplicant/wpa_supplicant_{}.conf'.format(nic), actual_contents)
    # Write to temporary template file (not needed in this case) and system
    writeFile('data/tmp/interfaces_compiled', interfaces)
    writeFile('/etc/network/interfaces', interfaces)

def init_lightwifi(nic='wlan0', network=None):
    args = "sudo iw dev "+nic+" info | grep ssid | sed -e 's/ssid / /g'"
    proc = Popen(args, stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=True)
    output, err = proc.communicate(b"")
    if proc.returncode == 0:
        set_current_connection(nic, str(output.decode("utf-8").strip()))
        logging.debug(nic+" connected to : "+get_current_connection(nic))
    else:
        logging.debug("No previous connection found")
    if network is not None:
        connect(network, nic)

def get_wifis(nic='wlan0'):
    args = "sudo iw dev {} scan | grep SSID | sort | uniq | sed -e \"s/SSID: / /g\"".format(nic)
    proc = Popen(args, stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=True)
    output, err = proc.communicate(b"")
    if proc.returncode == 0:
        wifis = []
        for wifi in output.decode("utf-8").split("\n"):
            wifis.append(wifi.strip())
        return wifis
    else:
        logging.warning("WARNING: Got an error for the WiFi detection command!")
        return []
        
def wifi_online(name, nic='wlan0'):
    return name in get_wifis(nic)
    
def get_current_connection(nic):
    if current_connection.get(nic) is not None:
        return current_connection[nic]
    
def set_current_connection(nic, name):
    global current_connection
    current_connection[nic] = name
    
def connect(name, nic='wlan0'):
    curr_conn = get_current_connection(nic)
    wifi_still_there = wait_for_wifi_init(nic, 1)
    wifi_still_online = wifi_online(name, nic)
    logging.debug("================ Connecting {} at {} ==========================".format(name, nic))
    logging.debug("|| Current connection on {} is {}".format(nic, curr_conn))
    logging.debug("|| Do I have a valid IP address to the connection? {}".format(wifi_still_there))
    logging.debug("|| Do the Wifi still exist on my list of available ones? {}".format(wifi_still_online))
    logging.debug("=========================================================================")
    if curr_conn == name and wifi_still_there:
        return True
        
    if wifi_still_online:
        index = light_wifis.get(name, -1)
        if index >= 0:
            template = readFile('data/tmp/wpa_supplicant_{}.conf'.format(nic))
            wpa_supplicant_contents = template.format(*get_priority_list(index, len(light_wifis)))
            chars_written = writeFile('/etc/wpa_supplicant/wpa_supplicant_{}.conf'.format(nic), wpa_supplicant_contents)
            if chars_written > 0 or chars_written is None:
                call(["ifdown", nic])
                call(["ifup", nic])
                res = wait_for_wifi_init(nic)
                if not res:
                    set_current_connection(nic, None)
                    logging.warning("Warning: WiFi connection might not be ready.")
                else:
                    set_current_connection(nic, name)
                    # Do some extra sleeping...
                    sleep(0.5)
                return res
            else:
                logging.warning("Could not add WiFi configuration. Did you really run with sudo?")
                return False
        else:
            raise ValueError("The given WiFi has not been configured in advance: " + name)
    else:
        logging.warning("WARNING: Could not connect to WiFi - not found.")
        return False
        
def wait_for_wifi_init(nic='wlan0', max_iterations=20):
    counter = 0
    while(counter < max_iterations):
        proc = Popen("ifconfig "+nic+" | grep 'inet addr'", stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=True)
        output, err = proc.communicate(b"")
        if proc.returncode == 0:
            return True
        else:
            counter += 1
            if counter < max_iterations:
                sleep(0.5)
    return False
    
def got_valid_connection(nic='wlan0'):
    return wait_for_wifi_init(nic, 1)
        
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
