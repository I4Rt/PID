import serial
from time import sleep

from tools.crc.crc16module import *
from tools.byteTools.ByteTools import *

def getTemperature(ser:serial.Serial, message = b'\x02\x04\x00\x00\x00\x02'):
    message_crc = add_crc(message)
    res = ser.write(message_crc)
    # print('temp command')
    ser.flush()
    size, answer = byte_reader(ser, len(message_crc))
    
    if size > 2:
        if answer[1] == 4:
            temp = int.from_bytes(answer[5:7], byteorder='big')
            order = int.from_bytes(answer[3:5], byteorder='big')
            return temp / 10 **order
    print('error message', answer)
    return None

# if __name__ == '__main__':
    
#     port = "COM5"  # Replace with the appropriate COM port name
#     baudrate = 38400  # Replace with the desired baud rate
#     data = b'\x02\x04\x00\x00\x00\x02'
#     ser = serial.Serial(port, baudrate=baudrate)
#     print(getTemperature(ser, data))
#     ser.close()


