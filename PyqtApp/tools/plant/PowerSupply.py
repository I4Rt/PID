from tools.ModbusTool import *

class PowerSupply:
    
    def __init__(self, address=b'\x01'):
        self.address = address
        self.status = 0
        self.amperageData = None
    
    def getStatus(self, ser):
        # 03 00 01 00 01
        msg = self.address + b'\x03\x00\x03\x00\x01'
        # convert status
        size, answer = sendMessage(ser, msg)
        print('status answer', answer)
        res, code, info = checkAnswer(size, answer)
        if res:
            self.status = int(binascii.b2a_hex(answer[3:5]), 16)
            print('status code', self.status)
            return True
        return False
    
    def switchON(self, ser):
        #01 10 00 06 00 01 02 01 00
        msg = self.address + b'\x10\x00\x06\x00\x01\x02\x01\x00'
        size, answer = sendMessage(ser, msg)
        print('switch on answer', answer)
        res, code, info = checkAnswer(size, answer)
        if res:
            return True
        return False
    
    def switchOFF(self, ser):
        #msg
        msg = self.address + b'\x10\x00\x06\x00\x01\x02\x00\x00'
        size, answer = sendMessage(ser, msg)
        print('switch off power supply answer', answer)
        res, code, info = checkAnswer(size, answer)
        if res:
            return True
        return False
    
    def setAmpere(self, ser, value=0):
        '''
        set amperage
        
        params:
         - ser: serial port [serial.Serial]
         - val: xxx.x amperage value 
        '''
        if value < 0:
            raise Exception('wrong amperage value')
        value *= 10
        value = "{0:x}".format(int(value))
        if len(value)%2:
            value = '0' + value
        value = bytes.fromhex(value)
        if len(value) < 2:
            value = b'\x00' + value
        #msg                    com address reg_n   b_n  
        msg = self.address + b'\x10\x00\x05\x00\x01\x02' + value
        size, answer = sendMessage(ser, msg)
        print('amperage set', answer)
        res, code, info = checkAnswer(size, answer)
        if res:
            return True
        return False
        
    def getAmperage(self, ser):
        ''' 
        Get current set amperage value
        
        params:
         - ser[serial.Serial] - Serial port connection
         
        returns:
         - value[float|int] - Float value of the amperage or -1 in case of error
        
        '''
        # 03 00 01 00 01
        msg = self.address + b'\x03\x00\x01\x00\x01'
        
        size, answer = sendMessage(ser, msg)
        print('amperage answer', answer)
        res, code, info = checkAnswer(size, answer)
        if res:
            return int(binascii.b2a_hex(answer[3:5]), 16) / 10
        return -1
    
    
    def getVoltage(self, ser):
        ''' 
        Get current voltage value
        
        params:
         - ser[serial.Serial] - Serial port connection
         
        returns:
         - value[float|int] - Float value of the amperage or -1 in case of error
        
        '''
        # 03 00 01 00 01 amperage
        # 03 00 00 00 01 voltage
        msg = self.address + b'\x03\x00\x00\x00\x01'
        
        size, answer = sendMessage(ser, msg)
        print('amperage answer', answer)
        res, code, info = checkAnswer(size, answer)
        if res:
            return int(binascii.b2a_hex(answer[3:5]), 16) / 100
        return -1
        