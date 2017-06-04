from hardware import Hardware
import pylirc, time
import threading

DEBUG = False
UPDATE_FREQ = 100

class InfraRedSensor(Hardware):

    def __init__(self, id):
        Hardware.__init__(self, id, "IR")
        self.value = None
        self.listening = False
        self.listeners = []
        self.closed = False
        if not pylirc.init("pylirc", "./lirc_conf", False):
            print("Warning: Could not load IR dependencies")
        else:
            t = threading.Thread(target=self.listenLoop, name="IR Thread")
            t.daemon = True
            t.start()
            
    def getValue(self):
        return self.value

    def startListen(self):
        self.listening = True

    def stopListen(self):
        self.listening = False

    def listenLoop(self):
        while(not self.closed):
            s = pylirc.nextcode(1)
            if s is not None:
                for signal in s:                
                    if self.listening and signal is not None:
                        self.value = signal["config"]
                        for callback in self.listeners:
                            callback(signal["config"])
            time.sleep(0.040)

    def addListener(self, listener):
        self.listeners.append(listener)

    def removeListener(self, listener):
        self.listeners.remove(listener)

    def terminate(self):
        self.stopListen()
        self.closed = True
        pylirc.exit()



if DEBUG:
    def gotIREvent(event):
        print(event)

    irSensor = InfraRedSensor()
    irSensor.addListener(gotIREvent)
    irSensor.startListen()

    print("All started, listening for commands")
    while True:
        cmd = raw_input("Enter command: ")
        if cmd == "exit":
            print("Quitting....")
            irSensor.removeListener(gotIREvent)
            irSensor.destroy()
            break
        else:
            print("Unknown command: "+cmd)
