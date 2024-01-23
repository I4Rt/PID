
import time
import os.path
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np
from threading import Thread

import modules.PID as PID
from modules.PIDModels import *
from modules.sender import *
from modules.reciever import *

from modules.StopableThread import *




class Heater:
    
    def __init__(self, needPID=False, target = 100, p=50, i=50, d=100, serialName = 'COM5'):
        
        self.targetTemperature = target
        self.currentTemperature = None
        
        self.P = p
        self.I = i
        self.D = d
        
        self.pid = MyPID(self.P, self.I, self.D)
        self.pid.setTarget(self.targetTemperature)
        
        
        try:
            self.ser = serial.Serial(serialName, baudrate=38400, timeout=0.1)
        except Exception as e:
            self.ser = None
            print('connectError', e)
        
        self.needPID = needPID
        
        self.realTemperatureList = []
        self.targetTemperatureList = []
        
        self.controlThread = StopableThread(target=self.controlFunc, looped=True)
        
        
        
    def controlFunc(self):
        
        self.pid.k1 = self.P
        self.pid.k3 = self.I
        self.pid.k2 = self.D
        self.pid.setTarget(self.targetTemperature)
        
        
        #read temperature data
        t = None
        while not t:
            t = getTemperature(self.ser, b'\x02\x04\x00\x00\x00\x02')
        # print(t)
        self.currentTemperature = t
        self.targetTemperatureList.append(self.targetTemperature if self.needPID else None)
        self.targetTemperatureList = self.targetTemperatureList[-10000:]
        self.realTemperatureList.append(t)
        self.realTemperatureList = self.realTemperatureList[-10000:]
        
        if self.needPID:
            swith_on(self.ser)
            
            targetPwm = self.pid.update(t)
            print(targetPwm)
            if targetPwm > 300: 
                targetPwm = 0
            print(targetPwm)
            targetPwm = max(min( int(targetPwm), 100 ),0)
            
            # print ("Target: %.1f C | Current: %.1f C | PWM: %s %%"%(self.targetTemperature, self.currentTemperature, targetPwm))
            set_power(self.ser, int(10000 * targetPwm / 100))
        
            sleep(0.05)
        else:
            sleep(0.2)

    def startThread(self):
        while True:
            try:
                swith_off(self.ser)
                break
            except:
                print('e')
                    
        self.controlThread.start()
        
    def pauseThread(self):
        self.controlThread.pause()
        
    def playThread(self):
        self.controlThread.play()
        
    def stopThread(self):
        self.controlThread.stop()
        self.ser.close()
        
    def setNeedPID(self, val:bool):
        self.needPID = val
        
        if not self.needPID:
            print('\n\nswitching off\n\n')
            while True:
                try:
                    swith_off(self.ser)
                    return
                except:
                    print('e')
        
    






# TARGET_TEMPERATURE = 100
# temperature = None
# targetT = TARGET_TEMPERATURE
# P = 50
# I = 50
# D = 100

# pid = PID.PID(P, I, D)
# pid.SetPoint = TARGET_TEMPERATURE
# pid.setSampleTime(1)







# def readConfig ():
#         global targetT
#         global pid
#         global P, I, D, TARGET_TEMPERATURE
#         with open ('/tmp/pid.conf', 'r') as f:
#             config = f.readline().split(',')
#             pid.SetPoint = TARGET_TEMPERATURE
#             targetT = pid.SetPoint
#             pid.setKp (float(config[1]))
#             pid.setKi (float(config[2]))
#             pid.setKd (float(config[3]))
#             print()

# def createConfig ():
#     global P, I, D, TARGET_TEMPERATURE
#     if not os.path.isfile('/tmp/pid.conf'):
#         with open ('/tmp/pid.conf', 'w') as f:
#             f.write('%s,%s,%s,%s'%(TARGET_TEMPERATURE,P,I,D))



# def control(ser = None):
#     global temperature
#     global pid
#     global P, I, D, TARGET_TEMPERATURE
    
#     port = "COM5"  # Replace with the appropriate COM port name
#     baudrate = 38400  # Replace with the desired baud rate
#     if not ser:
#         ser = serial.Serial(port, baudrate=baudrate, timeout=0.1)
#     ser.flush()
#     createConfig()
#     def controlCommands():
#         global temperature
#         global pid, P, I, D, TARGET_TEMPERATURE
#         readConfig()
#         swith_on(ser)
#         #read temperature data
#         t = None
#         while not t:
#             t = getTemperature(ser, b'\x02\x04\x00\x00\x00\x02')
#         print(t)
#         pid.update(t)
#         temperature = t
#         targetPwm = pid.output
#         targetPwm = max(min( int(targetPwm), 100 ),0)
#         print ("Target: %.1f C | Current: %.1f C | PWM: %s %%"%(targetT, temperature, targetPwm))
#         # Set PWM expansion channel 0 to the target setting
#         set_power(ser, int(10000 * targetPwm / 100))
#         sleep(0.05)
    
#     resThread = StopableThread(target=controlCommands, args=(), looped=True)
#     return resThread









# def test():
#     h = Heater(target=50, needPID=True)
#     h.startThread()
#     sleep(10)
#     print('\n\nsetting stopPidding\n\n')
#     h.setNeedPID(False)
#     sleep(10)
#     print('\n\nsetting targetTemperature 50\n\n')
#     h.targetTemperature = 100
#     h.setNeedPID(True)
#     sleep(10)
#     h.stopThread()
    
#     from matplotlib import pyplot as plt

#     plt.plot(h.targetTemperatureList)
#     plt.plot(h.realTemperatureList)
#     plt.show()

# if __name__ == '__main__':
#     test()