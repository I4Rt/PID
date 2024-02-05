import serial
import binascii

from tools.crc.crc16module import *
from tools.byteTools.ByteTools import *

def sendMessage(ser, message):
        message_crc = add_crc(message)
        # print('sending message:', message_crc)
        res = ser.write(message_crc)
        ser.flush()
        size, answer = byte_reader(ser, len(message_crc))
        return size, answer
    
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