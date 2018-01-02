from wifi import Cell, Scheme
from socket import *
from subprocess import Popen, PIPE
from time import sleep
import logging
import platform
import sys

logger = logging.getLogger(__name__)
current_connection = {}

def get_current_ssid(nic='wlan0'):
    return current_connection[nic]["ssid"]
    
def get_socket_for_nic(nic='wlan0'):
    return current_connection[nic]["socket"]
    
def get_default_socket(nic):
    sock = socket(AF_INET, SOCK_DGRAM)
    sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    sock.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
    sock.setsockopt(SOL_SOCKET, 25, bytes(nic, 'utf-8'))
    return sock
      
def init_nic_info(nic='wlan0', create_socket=get_default_socket):
    if current_connection.get(nic) is None:
        current_connection[nic] = {"ssid": None, "socket": create_socket(nic), "broadcast": None}

        ## Init current network connection.
        if platform.system() == "Linux":
            current_connection[nic]["ssid"] = run_native_command("sudo iw dev {} info | grep ssid | sed -e 's/ssid / /g'".format(nic))
            logger.info("Found existing connection for {}: {}".format(nic, current_connection[nic]["ssid"]))
        else:
            logger.warning("Beware: Network card init only available for Linux!")
            
def get_broadcast_address(nic='wlan0', buffer_disallowed=False):
    if not buffer_disallowed and not current_connection[nic]["broadcast"] is None:
        return current_connection[nic]["broadcast"]
        
    if platform.system() == "Linux":
        res = run_native_command("ifconfig {} | sed 's/ /\\n/g' | grep Bcast | sed -e 's/Bcast://g'".format(nic))
        print("Found address '{}'".format(res))
        return res
    else:
        logger.warning("Generic broadcast address retrieval only available on Linux")
        return None
        
def update_broadcast_address(nic='wlan0'):
    current_connection[nic]["broadcast"] = get_broadcast_address(nic, True)

def connect(ssid, passkey=None, nic='wlan0', force_reconfig=False):
    online = wifi_online(ssid, nic)
    if get_current_ssid(nic) == ssid and online:
        if current_connection[nic]["broadcast"] is None:
            update_broadcast_address(nic)
        return True
        
    if online:
        try:
            scheme = Scheme.find(nic, ssid)
            if scheme is not None and not force_reconfig:
                scheme.activate()
                current_connection[nic]["ssid"] = ssid
                update_broadcast_address(nic)
                return True
            else:
                matching_cells = [cell for cell in Cell.all(nic) if cell.ssid == ssid]
                if len(matching_cells) > 0:
                    scheme = Scheme.for_cell(nic, ssid, matching_cells[0], passkey)
                    scheme.save()
                    scheme.activate()
                    current_connection[nic]["ssid"] = ssid
                    update_broadcast_address(nic)
                    return True
        except Exception as e:
            logger.warning("Could not connect to wifi: "+str(e))
            return False
                
    current_connection[nic]["ssid"] = None
    return False
            
def wifi_online(ssid, nic='wlan0'):
    return ssid in [cell.ssid for cell in Cell.all(nic)]
    
def is_connected(ssid, nic='wlan0'):
    return get_current_ssid(nic) == ssid
    
def send_message(content, nic, addr, port, retransmits=3):
    logger.info("Sending packet to "+addr+":"+str(port))
    sock = get_socket_for_nic(nic)
    packet = get_packet_data(content)
    if sock is not None:
        for i in range(0, retransmits):
            sock.sendto(packet, (addr, port))
            if i < retransmits-1:
                sleep(0.1)
    else:
        logger.warning("Error: Uninitialized socket!")
        
            
def run_native_command(cmd):
    proc = Popen(cmd, stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=True)
    output, err = proc.communicate(b"")
    if proc.returncode == 0:
        return str(output.decode("utf-8").strip())
    else:
        logger.warning("Could not execute native command: "+err)
        return ""
        
def get_packet_data(data):
    if sys.version_info > (3, 0):
        return bytes(data)
    else:
        return bytearray(data)
  
        
if __name__ == "__main__":
    print("Running on {}".format(platform.system()))
    print("Available networks: ", "; ".join([cell.ssid for cell in Cell.all('wlan0')]))
