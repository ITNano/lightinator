from pydub import AudioSegment
from tempfile import NamedTemporaryFile
import os
import subprocess
import util


############################# --------------------- Utils ------------------------ #################################
    
# Credit: Pydub utils        
def getPlayerName():
    if util.which("avplay"):
        return "avplay"
    elif util.which("ffplay"):
        return "ffplay"
    else:
        warn("Couldn't find ffplay or avplay - defaulting to ffplay, but may not work", RuntimeWarning)
        return "ffplay"
            
########################################################################################################################

DEBUG = False
sounds = {}
PLAYER = getPlayerName()
playProcess = None

def getType(filename):
    return filename[filename.rfind('.')+1:]
    
def getInMs(time):
    if time is None:
        return None
    else:
        return 1000*time

def loadSound(name, filename, start=0, end=0):
    if sounds.get(name) is None:
        sound = AudioSegment.from_file(filename, getType(filename))
        sound = sound[getInMs(start):getInMs(end)]
        with NamedTemporaryFile("w+b", suffix=".wav", delete=False) as f:
            sound.export(f.name, "wav")
            sounds[name] = f
    else:
        print "Warning: Duplicate sound ID - '"+name+"'"
    
def playSound(name, loop=None):
    file = sounds.get(name)
    if file is not None:
        global playProcess
        stopSounds()
        procArgs = [PLAYER, "-nodisp", "-autoexit"]
        if loop is not None:
            procArgs.extend(["-loop", str(loop)])
        procArgs.append(file.name)
        devnull = open(os.devnull, 'wb')
        if not DEBUG:
            playProcess = subprocess.Popen(procArgs, stdout=devnull, stderr=devnull)
        else:
            playProcess = subprocess.Popen(procArgs)
        
def stopSounds():
    if playProcess is not None:
        playProcess.terminate()
        
def cleanup():
    for file in sounds:
        file.close()
        os.remove(file.name)
    sounds = {}
            