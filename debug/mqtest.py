import zmq
import sys
import threading
import logging

def getServerConn(addr):
    logging.info("Opening server @ {0}".format(addr))
    context = zmq.Context()
    subscriber = context.socket(zmq.SUB)
    subscriber.bind(addr)
    subscriber.setsockopt(zmq.SUBSCRIBE, '')
    logging.info("Server open @ {0}".format(addr))
    return subscriber
    
def getClientConn(addr):
    logging.info("Connecting to {0}".format(addr))
    context = zmq.Context()
    publisher = context.socket(zmq.PUB)
    publisher.connect(addr)
    logging.info("Connection established")
    return publisher
    
def getAddress(proto, name):
    translateTable = { "ipc": "ipc:///", "tcp": "tcp://" }
    return translateTable.get(proto, "{0}://".format(proto))+name
    
def getTcpAddress(ip, port):
    return getAddress("tcp", "{0}:{1}".format(ip, port))
    
def getIcpAddress(path):
    return getAddress("ipc", path)
    
def runEchoClient(addr):
    publisher = getClientConn(addr)
    while True:
        msg = raw_input()
        if msg == "end":
            break
        publisher.send(msg)
    
def runEchoServer(addr):
    subscriber = getServerConn(addr)
    while True:
        print(subscriber.recv())
        
def printUsage():
    logging.error("Usage: python mqtest.py [server|client] [proto] [address]")

if __name__ == "__main__":
    if len(sys.argv) == 4:
        if sys.argv[1] == "server":
            runEchoServer(getAddress(sys.argv[2], sys.argv[3]))
        elif sys.argv[1] == "client":
            runEchoClient(getAddress(sys.argv[2], sys.argv[3]))
        else:
            logging.error("Invalid argument: {0}".format(sys.argv[1]))
            printUsage()
    else:
        logging.error("Invalid number of arguments")
        printUsage()