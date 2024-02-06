from tools.ModbusTool import *
from tools.byteTools.ByteTools import *
from tools.IEEE754 import *

class Heater:
    
    def __init__(self, address=b'\x01'):
        self.address:bytes = address
        
    def swithON(self, ser:serial.Serial):
        msg = self.address + b'\x06\x02\x04\x00\x01'
        size, answer = sendMessage(ser, msg)
        res, code, msg = checkAnswer(size, answer)
        if res:
            return True
        print('heater error', code, msg)
        return False
    
    def swithOFF(self, ser:serial.Serial):
        msg = self.address + b'\x06\x02\x04\x00\x00'
        size, answer = sendMessage(ser, msg)
        res, code, msg = checkAnswer(size, answer)
        if res:
            return True
        print('heater error', code, msg)
        return False
    
    def setVoltage(self, ser:serial.Serial, voltage:float):
        if voltage > 10 or voltage < 0:
            print('unavaliable voltage size (10 >= voltage >= 0)')
            return False
        voltage/=10
        voltage = round(voltage, 2)
        hexVoltage = float_to_hex16(voltage)
        if len(hexVoltage) > 4:
            print('got too big hex', hexVoltage)
            return False
        hexVoltage = b'\x00'* (4 - len(hexVoltage)) + hexVoltage
        print('sending hex voltage', hexVoltage)
        
        msg = self.address + b'\x10\x02\x01\x00\x02\x04' + hexVoltage
        
        size, answer = sendMessage(ser, msg)
        res, code, msg = checkAnswer(size, answer)
        if res:
            return True
        
        print('heater error (set voltage)', code, msg)
        return False
