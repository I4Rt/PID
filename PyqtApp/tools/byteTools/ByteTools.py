import serial
from time import time
def byte_reader(ser: serial.Serial, size = 9):
    buf = b''
    while True:
        res = ser.read()
        if res:
            buf += res
            if len(buf) > 72:
                ser.close()
                ser.open()
                return len(buf), buf
                # raise Exception(str(buf))
            continue
        break 

    
    return len(buf), buf