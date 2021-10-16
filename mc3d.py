#   _____ _                     ___ _      ___   _    _____     _     _           
#  |     |_|___ ___ ___ ___ ___|  _| |_   |_  |_| |  |  _  |___|_|___| |_ ___ ___ 
#  | | | | |   | -_|  _|  _| .'|  _|  _|  |_  | . |  |   __|  _| |   |  _| -_|  _|
#  |_|_|_|_|_|_|___|___|_| |__,|_| |_|    |___|___|  |__|  |_| |_|_|_|_| |___|_|  
#


import time
import sys
from pywinauto import keyboard
from gcode import * #Point, GCommand, G28


gcodefile = sys.argv[1]

extruder = Point(0,0,0)
offset = Point(3,3,0)
nextEndPoint = GCommand("")
block = "minecraft:diamond_block"

def main():
    global gcodefile
    print (f"Opening {gcodefile}.. switch to Minecraft.")
    #A short wait to allow me to switch to minecraft
    time.sleep(3) 
    # open file
    n=800 # batch lines at a time
    with open(gcodefile) as f:
        batch=[]
        for line in f:
            batch.append(line)
            if len(batch)==n:
                process(batch)
                batch=[]
    process(batch)

def process(data): 
    if (data and len(data) > 0):
        #process lines
        global extruder, offset, block
        for command in data:
            if(command.startswith("G")):
                commandParts = CommandData(command)
                if (len(commandParts) > 0):
                    #Take the command and parameters and converts them into coordinates
                    nextEndPoint = CommandDecoder(commandParts, extruder, offset, block)
                    extruder = CmdExec(nextEndPoint, extruder, offset)

if __name__ == "__main__":
    main()
