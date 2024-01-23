import serial
from time import time
def byte_reader(ser: serial.Serial, size = 9):
    buf = b''
    begin = time()
    while True:
        res = ser.read()
        if res:
            now = time()
            buf += res
            if len(buf) > 72:
                ser.close()
                ser.open()
                return len(buf), buf
                
                raise Exception(str(buf))
            continue
        break 
    end = time()
    if end - begin > 1:
        print(end - begin)
    
    return len(buf), buf