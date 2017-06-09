from pydub import AudioSegment
from tempfile import NamedTemporaryFile
import os
import subprocess


############################# --------------------- Utils ------------------------ #################################
    
# Credit: Pydub utils        
def getPlayerName():
    if which("avplay"):
        return "avplay"
    elif which("ffplay"):
        return "ffplay"
    else:
        warn("Couldn't find ffplay or avplay - defaulting to ffplay, but may not work", RuntimeWarning)
        return "ffplay"
        
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
            
########################################################################################################################

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
    
def playSound(name):
    file = sounds.get(name)
    if file is not None:
        global playProcess
        stopSounds()
        playProcess = subprocess.Popen([PLAYER, "-nodisp", "-autoexit", file.name])
        
def stopSounds():
    if playProcess is not None:
        playProcess.terminate()
        
def cleanup():
    for file in sounds:
        file.close()
        os.remove(file.name)
    sounds = {}
            