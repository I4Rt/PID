from tools.ModbusTool import *
from tools.byteTools.ByteTools import *
from tools.IEEE754 import *

class ThermoGetter:
    def __init__(self, address=b'\x01', register:bytes=b'\x00\x00'):
        self.address:bytes = address
        self.register:bytes=register
        print(self.address, self.register)
        
    def getTemperature(self, ser:serial.Serial):
        msg = self.address + b'\x04' + self.register + b'\x00\x02'
        message_crc = add_crc(msg)
        res = ser.write(message_crc)
        # print('temp command')
        ser.flush()
        size, answer = byte_reader(ser, len(message_crc))
        res = checkAnswer(size,answer)
        if res:
            temp = int.from_bytes(answer[5:7], byteorder='big')
            order = int.from_bytes(answer[3:5], byteorder='big')
            print('\n\n\n\n\n\n\n\n\n\n\n\n\ngot temperature', temp)
            return temp / 10 **order
        return None
        