import serial.tools.list_ports

def getExistPorts():
    ports = serial.tools.list_ports.comports()

    info = []
    for portInfo in ports:
        info.append([portInfo[0], portInfo[1]])
        
    return info
        
    
    
if __name__ == '__main__':
    print(getExistPorts())