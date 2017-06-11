import os
import sys
import psutil
import logging
import subprocess
import netifaces

def resetNICs(nicStart):
    # Reset interfaces that start with wlan
    print "Resetting interfaces...."
    for interface in netifaces.interfaces():
        if interface[:len(nicStart)] == nicStart:
            subprocess.call(['ifdown', interface])
            subprocess.call(['ifup', interface])
    print "Interfaces re-activated"
    

# Credit: s3ni0r
# https://stackoverflow.com/questions/11329917/restart-python-script-from-within-itself
def restartProgram():
    """Restarts the current program, with file objects and descriptors
       cleanup
    """
    try:
        p = psutil.Process(os.getpid())
        for handler in p.open_files() + p.connections():
            os.close(handler.fd)
    except Exception, e:
        logging.error(e)

    python = sys.executable
    os.execl(python, python, *sys.argv)
	
	
# Credit: Pydub utils        
def which(program):
    #Add .exe program extension for windows support
    if os.name == "nt" and not program.endswith(".exe"):
        program += ".exe"

    envdir_list = [os.curdir] + os.environ["PATH"].split(os.pathsep)

    for envdir in envdir_list:
        program_path = os.path.join(envdir, program)
        if os.path.isfile(program_path) and os.access(program_path, os.X_OK):
            return program_path
            
def writeFile(file, contents):
    with open(file, 'w') as f:
        return f.write(contents)
        
def readFile(file):
    with open(file, 'r') as f:
        return f.read()