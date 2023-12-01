import serial
from modules.crc16module import add_crc, check_crc

from time import sleep, time
from modules.reciever import getTemperature
from modules.tools import *


def swith_on(ser):
    message = b'\x01\x05\x00\x04\xFF\x00'
    message_crc = add_crc(message)
    res = ser.write(message_crc)
    size, answer = byte_reader(ser, len(message_crc)) 
    if size > 2:
        if answer[1] == 5:
            return True
    return False
    
def swith_off(ser):
    message = b'\x01\x05\x00\x04\x00\x00'
    message_crc = add_crc(message)
    res = ser.write(message_crc)
    size, answer = byte_reader(ser, len(message_crc)) 
    if size > 2:
        if answer[1] == 5:
            return True
    return False

def set_power(ser:serial.Serial, power):
    byte_power = power.to_bytes(2, byteorder='big')
    message = b'\x01\x06\x00\x00' + byte_power
    message_crc = add_crc(message)
    ser.flush()
    res = ser.write(message_crc)
    
    size, answer = byte_reader(ser, len(message_crc)) 
    if size > 2:
        if answer[1] == 6:
            return True
    print('setv power error', answer)
    return False

# if __name__ == '__main__':
#     from matplotlib import pyplot as plt
    
#     part1 = [5000 for i in range(1000)]
#     part2 = [0 for i in range(200)]
#     part3 = [10000 for i in range(500)]
#     part4 = [2500 for i in range(200)]
#     part5 = [0 for i in range(200)]
#     part6 = [5000 for i in range(500)]
#     part7 = [3000 for i in range(250)]
#     part8 = [1000 for i in range(250)]
#     part9 = [0 for i in range(250)]


#     modes = part1 + part2 + part3 + part4 + part5 + part6 + part7 + part8 + part9

#     port = "COM5"  # Replace with the appropriate COM port name
#     baudrate = 38400  # Replace with the desired baud rate

#     ser = serial.Serial(port, baudrate=baudrate, timeout=0.1)
#     ser.flush()

#     plt.axis([0, len(modes) + 2, 0, 200])
#     counter = 0

#     switchedOn = swith_on(ser)
#     print(switchedOn)
#     prev_temp = 0
#     count = 0
#     temp_list = []

#     for i in modes:
#         counter += 1
#         tempSet = set_power(ser, i)
#         sleep(0.05)
#         # if not(tempSet):
#         # print(tempSet)
#         got_temp = getTemperature(ser, b'\x02\x04\x00\x00\x00\x02')
#         temp_list.append(got_temp)
#         print(got_temp)
#         # plt.scatter(counter, got_temp, marker='.', color='red')
#         # plt.scatter(counter, i / 100, marker='.', color='blue')
#         # plt.pause(0.05)
#         # if got_temp:
#         #     if got_temp > prev_temp:
#         #         count += 1
#         #         prev_temp = got_temp
#         #         print(count, prev_temp)
        
#         sleep(0.05)
        
#     ser.close()  # Remember to close the connection when done


#     import json
#     with open('counter.txt', 'r') as file:
#         counter = int(file.read())
#     with open('counter.txt', 'w') as file:
#         counter = str(counter + 1)
#     with open(f'test{counter}.txt', 'w') as file:
#         file.write(json.dumps({'input': modes, 'output':temp_list}))


#     x = [i for i in range(len(modes))]
#     plt.plot(x, [mode / 100 for mode in modes] , 'r', x, temp_list, 'b')
#     plt.show()

