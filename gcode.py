import time
from pywinauto import keyboard
history = []
validcmds = ["G0","G1","G28"]
maxComParam = 5
delayT = 0.02
delayK = 0.0001

def SendKeys(cmd:str):
    global delayT
    cmd = cmd.replace("~","{~}") # ~ is Enter, so escaping the tilda ~
    keyboard.send_keys(cmd+"{ENTER}", delayK, True)
    time.sleep(delayT)
    keyboard.send_keys("{/ down}{/ up}{BS}", delayT) # this keeps the console open
    time.sleep(delayT)
    #debug:
    #print (cmd)

class Point(object):
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

class GCommand():
    def __init__(self, code:str, x=0, y=0, z=0, newx=False, newy=False, newz=False, extrude=False, ignore=True, block=""):
        self.code = code
        self.x = x
        self.y = y
        self.z = z
        self.newx = newx
        self.newy = newy
        self.newz = newz
        self.extrude = extrude
        self.ignore = ignore
        self.block = block

def CmdExec(target: GCommand, extruder: Point, offset: Point):
    if (target.code == "G1"):
        return G1(target, extruder, offset)
    if (target.code == "G28"):
        return G28(extruder, offset)
    return extruder


def G28(extruder:Point, offset: Point):
    print ("G28\n")
    extruder.x = offset.x
    extruder.y = offset.y
    extruder.z = offset.z
    return extruder

def CommandData(com:str):
    global maxComParam
    command = com.strip();
    if ';' in com:
        cmdEnd = command.index(';')
        command = command[:cmdEnd]
    commandParts = command.split(' ')
    # if ';' in commandParts:
    #     commandParts = commandParts[:commandParts.index(';')]

    return commandParts


def CommandDecoder(commandParts, extruder:Point, offset: Point, block):
    
    global validcmds, maxComParam
    endpoint = GCommand(commandParts[0])
    endpoint.block = block

    if (endpoint.code in validcmds):
        endpoint.ignore = False
        for h in range(len(commandParts)):
            if(commandParts[h] == ""):
                continue
            else:
                #and if it has, then converts it to variables
                if (commandParts[h].startswith("X")):
                    endpoint.x = int(float(commandParts[h][1:])) + offset.x
                    if (abs(endpoint.x - extruder.x) >= 1):
                        endpoint.newx = True
                        continue
                elif commandParts[h].startswith("Y"):
                    endpoint.y = int(float(commandParts[h][1:])) + offset.y

                    if (abs(endpoint.y - extruder.y) >= 1):
                        endpoint.newy = True                        
                        continue   
                    
                elif(commandParts[h].startswith("Z")):
                    endpoint.z = int(float(commandParts[h][1:])) + offset.z
                    if(abs(endpoint.z - extruder.z) > 0):
                        endpoint.newz = True
                        continue

                if(commandParts[h].startswith("E") and float(commandParts[h][1:]) > 0):
                    endpoint.extrude = True
                    continue
        # end for
        if(endpoint.newx == False and endpoint.newy == False and endpoint.newz == False and endpoint.extrude == False):
            endpoint.ignore = True
    
    #print (commandParts)
    #print(vars(endpoint))
    return endpoint

def SendSetBlock(ext: Point, block):
    if (not block):
        block = "minecraft:gold_block"
    if (f"X{ext.x}Y{ext.y}Z{ext.z}" not in history):
        history.append(f"X{ext.x}Y{ext.y}Z{ext.z}")
        SendKeys(f"/setblock ~{ext.x} ~{ext.z} ~{(-1*ext.y)} {block} replace")

def G1(target: GCommand, extruder: Point, offset: Point):
    
    ext = Point(extruder.x, extruder.y, extruder.z)

    if (target.ignore == False):
        if (target.extrude == True):

            if (target.newx == True and target.newy == False and target.newz == False and abs(extruder.x - target.x) >= 1):
                # X-only ext
                if (extruder.x < target.x):
                    for x in range(extruder.x, target.x):
                        ext.x = x
                        SendSetBlock(ext, target.block)
                else: # extruder.x >= target.x
                    for x in range(extruder.x, target.x, -1):
                        ext.x = x
                        SendSetBlock(ext, target.block)
            elif (target.newx == False and target.newy == True and target.newz == False and abs(extruder.y - target.y) >= 1):
                # Y-only ext
                if (extruder.y < target.y):
                    for y in range(extruder.y, target.y):
                        ext.y = y
                        SendSetBlock(ext, target.block)
                else: #extruder.y >= target.y
                    for y in range(extruder.y, target.y, -1):
                        ext.y = y
                        SendSetBlock(ext, target.block)
            elif (target.newx == True and target.newy == True and target.newz == False):
                # XY ext
                deltaY = target.y - extruder.y
                deltaX = target.x - extruder.x
                m = (deltaY)/(deltaX)
                if(abs(m) <= 1):
                    if (extruder.x < target.x):
                        for i in range(0, deltaX):
                            ext.x = i + extruder.x
                            ext.y = int(round(m * i)) + extruder.y
                            if (abs(extruder.x - ext.x) >= 1 or abs(extruder.y - ext.y) >= 1):
                                SendSetBlock(ext, target.block)
                    else: # extruder.x >= target.x
                         for i in range(0, deltaX, -1):
                            ext.x = i + extruder.x
                            ext.y = int(round(m * i)) + extruder.y
                            if (abs(extruder.x - ext.x) >= 1 or abs(extruder.y - ext.y) >= 1):
                                SendSetBlock(ext, target.block)
                else: 
                    if (extruder.y < target.y):
                        for w in range(0, deltaY):
                            ext.y = w + extruder.y
                            ext.x = int(round(w / m)) + extruder.x
                            if (abs(extruder.x - ext.x) >= 1 or abs(extruder.y - ext.y) >= 1):
                                SendSetBlock(ext, target.block)
                    else: # extruder.y >= target.y
                        for w in range(0, deltaY, -1):
                            ext.y = w + extruder.y
                            ext.x = int(round(w / m)) + extruder.x
                            if (abs(extruder.x - ext.x) >= 1 or abs(extruder.y - ext.y) >= 1):
                                SendSetBlock(ext, target.block)

            extruder.x = ext.x
            extruder.y = ext.y    
        else:
            # Movement
            if (target.newx):
                extruder.x = target.x
            if (target.newy):
                extruder.y = target.y
            if (target.newz):
                extruder.z = target.z
    
    # Done
    return extruder
