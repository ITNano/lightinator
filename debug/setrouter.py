from socket import *

data = [0xFB, 0xE1]
for i in range(2, 66):
	data.append(0x00)
for c in "TARDIS":
	data.append("{:02x}".format(ord(c)))
while(len(data) < 98):	
	data.append(0x00)
for c in "C17E850FA6CF0":
	data.append("{:02x}".format(ord(c)))
while(len(data) < 130):	
	data.append(0x00)
data.append(0x00)
data.append(0xCF)
data.append(0xD4)
data.append(0xFA)

sock = socket(AF_INET, SOCK_DGRAM) # UDP, internet
sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
sock.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
sock.sendto(bytes(data), ("192.168.4.255", 30977))
