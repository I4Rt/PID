import serial
import binascii

from tools.crc.crc16module import *
from tools.byteTools.ByteTools import *


class Motor:
    
    def __init__(self, address = b'\x04'):
        self.address = address # b'\x04'
        
        self.enabled = False
        self.movingCompleted = True
        self.commandCompleted = True
        self.baseSearchFinished = True
        self.inWork = False
        self.fault = False
        
    def __sendMessage(self, ser, message):
        message_crc = add_crc(message)
        # print('sending message:', message_crc)
        res = ser.write(message_crc)
        ser.flush()
        size, answer = byte_reader(ser, len(message_crc))
        return size, answer
    
    @staticmethod
    def checkAnswer(size, answer):
        if size < 3:
            return False, -1, 'Слишкий малый размер ответа'
        if size > 10:
            return False, -1, 'Слишкий большой размер ответа'
        if answer[1:2] > b'\x80':
            if answer[2:3] == b'\x01':
                return False, 1,  'Принятый код функции не может быть обработан'
            if answer[2:3] == b'\x02':
                return False, 2,  'Адрес данных, указанный в запросе, недоступен'
            if answer[2:3] == b'\x03':
                return False, 3,  'Значение, содержащееся в поле данных запроса, является недопустимой величиной'
            if answer[2:3] == b'\x04':
                return False, 4,  'Невосстанавливаемая ошибка имела место, пока ведомое устройство пыталось выполнить затребованное действие'
            if answer[2:3] == b'\x05':
                return False, 5,  'Ведомое устройство приняло запрос и обрабатывает его, но это требует много времени. Этот ответ предохраняет ведущее устройство от генерации ошибки тайм-аута'
            if answer[2:3] == b'\x06':
                return False, 6,  'Ведомое устройство занято обработкой команды. Ведущее устройство должно повторить сообщение позже, когда ведомое освободится'
            if answer[2:3] == b'\x07':
                return False, 7,  'Ведомое устройство не может выполнить программную функцию, заданную в запросе. Этот код возвращается для неуспешного программного запроса, использующего функции с номерами 13 или 14. Ведущее устройство должно запросить диагностическую информацию или информацию об ошибках от ведомого'
            if answer[2:3] == b'\x08':
                return False, 8,  '	Ведомое устройство при чтении расширенной памяти обнаружило ошибку паритета. Ведущее устройство может повторить запрос, но обычно в таких случаях требуется ремонт'
            if answer[2:3] == b'\x0A':
                return False, 10, 'Шлюз неправильно настроен или перегружен запросами'
            if answer[2:3] == b'\x0B':
                return False, 11, 'Slave устройства нет в сети или от него нет ответа'
            return False, int(binascii.b2a_hex(answer[2]), 16), 'Неопозная ошибка'
        return True, 0, 'Нормальный ответ'
    
    @staticmethod
    def StatusChecker(func):
        def inner(*args, **kwargs) -> tuple[bool, int, str]:
            size, answer = func(*args, **kwargs)
            return Motor.checkAnswer(size, answer)
        return inner
    
    def updateStatus(self, ser:serial.Serial):
        message = self.address + b'\x03' + b'\x40\x0A\x00\x01'
        size, answer = self.__sendMessage(ser, message)
        res, msg, comment =  Motor.checkAnswer(size, answer)
        if not res:
            return res, msg, comment
            
        # print('status recieved', answer, 'size', size)
        binRes = bin(int(binascii.b2a_hex(answer[3:5]), 16))
        binRes=binRes[2:]
        # print('bin status', binRes)
        binRes = '0'* (8 - len(binRes)) + binRes
        
        self.fault = bool(int(binRes[-1]))
        self.enabled = bool(int(binRes[-2]))
        self.inWork = bool(int(binRes[-3]))
        self.commandCompleted = bool(int(binRes[-5]))
        self.movingCompleted = bool(int(binRes[-6]))
        self.baseSearchFinished = bool(int(binRes[-7]))
        return res, msg, comment
        # print('error message', answer)
    
    @StatusChecker
    def setPowerEnabled(self, ser):
        #            device    command   register      value
        message=self.address + b'\x06' + b'\x00\x05' + b'\x00\xFF'
        return self.__sendMessage(ser, message)
        # print('set power enable:', answer)
    
    @StatusChecker
    def setTurnSide(self, ser, rightOrDown=True):
        value = b'\x00\x00'
        if rightOrDown:
            value = b'\x00\xFF'
        #            device    command   register      value
        message=self.address + b'\x06' + b'\x00\x06' + value
        return  self.__sendMessage(ser, message)
        # print('set turn size answer: '+str(answer))
        
    @StatusChecker
    def setTurnSpeed(self, ser, speed=0.5):
        '''
        set speed value tp motor
          ser:serial.Serial com port connection
          speed:double in Hz
        '''
        speed = "{0:x}".format(int(speed*1000))
        if len(speed)%2:
            speed = '0' + speed
        
        speed = bytes.fromhex(speed)
        if len(speed) < 2:
            speed = b'\x00'+speed
        # print('speed hex value', speed)
        
        #            device    command   register      value
        message=self.address + b'\x06' + b'\x40\x00' + speed
        return self.__sendMessage(ser, message)
        # print('set speed answer: '+str(answer))
    
    @StatusChecker
    def setTurnSpeed64000(self, ser, speed=0.5):
        '''
        set speed value tp motor
        ser:serial.Serial com port connection
        speed:double in mm per second
        '''
        speed = "{0:x}".format(int(speed*64000))
        if len(speed)%2:
            speed = '0' + speed
        speed = bytes.fromhex(speed)
        # print('freq hex value', speed)
        
        #            device    command   register      value
        message=self.address + b'\x06' + b'\x40\x00' + speed
        return  self.__sendMessage(ser, message)
        # print('set speed64000 answer: '+str(answer))
        
    @StatusChecker
    def move(self, ser):
        #       device         command   register      value
        message=self.address + b'\x06' + b'\x00\x07' + b'\x00\x02'
        return  self.__sendMessage(ser, message)
        # print('move answer: '+str(answer))
    
    @StatusChecker
    def stop(self, ser):
        #            device    command   register      value
        message=self.address + b'\x06' + b'\x00\x07' + b'\x00\x01'
        return  self.__sendMessage(ser, message)
        # print('stop answer: '+str(answer))
    
    @StatusChecker
    def _goHome(self, ser:serial.Serial):
        #            device    command   register      value
        message=self.address + b'\x06' + b'\x00\x07' + b'\x00\x09'
        return  self.__sendMessage(ser, message)
        # print('go home answer: '+str(answer))
        
    @StatusChecker
    def _setMoveDistance(self, ser:serial.Serial, distance:int):
        '''
        set move value to motor move_n command
          ser:serial.Serial com port connection
          distance:int in mm
        '''
        steps = "{0:x}".format(int(distance*4000)) # check formula
        if len(steps)%2:
            steps = '0' + steps
        steps = bytes.fromhex(steps)
        steps = b'\x00'*(4-len(steps)) + steps
        # print('distance hex value', steps, len(steps))
        
        #             device    command   register      reg count     bytes count value
        message= self.address + b'\x10' + b'\x80\x00' + b'\x00\x02' + b'\x04'   + steps
        return  self.__sendMessage(ser,message)
        # print('set distance answer', answer)
    
    @StatusChecker
    def _runMoveDistance(self, ser:serial.Serial):
        #            device    command   register      value
        message=self.address + b'\x06' + b'\x00\x07' + b'\x00\x03'
        return  self.__sendMessage(ser, message)
        # print('run distance answer', answer)
            
    def __str__(self):
        return f'''{self.__class__.__name__} ["fault": {self.fault}, "enabled": {self.enabled}, "inWork": {self.inWork}, "commandCompleted": {self.commandCompleted}, "movingCompleted": {self.movingCompleted}, "baseSearchFinished": {self.baseSearchFinished}]'''