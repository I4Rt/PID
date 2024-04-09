from tools.ModbusTool import *
from tools.IEEE754 import *

class VoltageGetter:
    
    def __init__(self, address=b'\x01'):
        self.address:bytes = address
        

    def getVoltage(self, ser:serial.Serial):
        msg = self.address + b'\x03\x02\x02\x00\x02'
        size, answer = sendMessage(ser, msg)
        
        res, code, msg = checkAnswer(size, answer)
        if res:
            if size >=7:
                dataPice1 = answer[3:5]
                dataPice2 = answer[5:7]
                data = dataPice2 + dataPice1
                print(data)
                flaotData = hex16_to_float(data)
                return flaotData * 2
        else:
            print('modbus error', code, msg)
        return -1
        
        
        