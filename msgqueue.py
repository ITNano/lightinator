import zmq
import sys
from util import runDaemon

runningServers = {}
    
def runServer(addr, callback, preprocessor=None, useMainThread=False):
    def run(addr, callback):
        global shouldRunServer
        runningServers[addr] = True
        conn = getServerConn(addr)
        while runningServers.get(addr) is True:
            try:
                msg = conn.recv()
                if preprocessor is not None:
                    msg = preprocessor(msg)
                runDaemon(target=callback, args=(addr, msg,))
            except:
                print("WARNING: Got an exception while reading server messages!")
        conn.close()
        
    if useMainThread:
        run(addr, callback)
    else:
        runDaemon(target=run, args=(addr, callback))
    
def stopServer(addr):
    runningServers[addr] = False
    
def getServerConn(addr):
    print("Opening server @ {0}".format(addr))
    context = zmq.Context()
    subscriber = context.socket(zmq.SUB)
    subscriber.bind(addr)
    subscriber.setsockopt(zmq.SUBSCRIBE, '')
    print("Server open @ {0}".format(addr))
    return subscriber
    
def getClientConn(addr):
    print("Connecting to {0}".format(addr))
    context = zmq.Context()
    publisher = context.socket(zmq.PUB)
    publisher.connect(addr)
    return publisher
    
def getAddress(proto, name):
    translateTable = { "ipc": "ipc:///", "tcp": "tcp://" }
    return translateTable.get(proto, "{0}://".format(proto))+name
    
def getTcpAddress(ip, port):
    return getAddress("tcp", "{0}:{1}".format(ip, port))
    
def getIcpAddress(path):
    return getAddress("ipc", path)
  
  