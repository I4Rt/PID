
import time
import os.path
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np
from threading import Thread

import modules.PID as PID
from modules.sender import *
from modules.reciever import *



TARGET_TEMPERATURE = 100
temperature = None
targetT = TARGET_TEMPERATURE
P = 50
I = 50
D = 100

pid = PID.PID(P, I, D)
pid.SetPoint = TARGET_TEMPERATURE
pid.setSampleTime(1)

def readConfig ():
        global targetT
        with open ('/tmp/pid.conf', 'r') as f:
            config = f.readline().split(',')
            pid.SetPoint = TARGET_TEMPERATURE
            targetT = pid.SetPoint
            pid.setKp (float(config[1]))
            pid.setKi (float(config[2]))
            pid.setKd (float(config[3]))

def createConfig ():
    if not os.path.isfile('/tmp/pid.conf'):
        with open ('/tmp/pid.conf', 'w') as f:
            f.write('%s,%s,%s,%s'%(TARGET_TEMPERATURE,P,I,D))
def control(ser = None):
    global temperature
    global PID

    port = "COM5"  # Replace with the appropriate COM port name
    baudrate = 38400  # Replace with the desired baud rate
    if not ser:
        ser = serial.Serial(port, baudrate=baudrate, timeout=0.1)
    ser.flush()
    createConfig()
    
    while True:
        readConfig()
        #read temperature data
        t = None
        while not t:
            t = getTemperature(ser, b'\x02\x04\x00\x00\x00\x02')
        print(t)
        pid.update(t)
        temperature = t
        targetPwm = pid.output
        targetPwm = max(min( int(targetPwm), 100 ),0)
        print ("Target: %.1f C | Current: %.1f C | PWM: %s %%"%(targetT, temperature, targetPwm))
        # Set PWM expansion channel 0 to the target setting
        set_power(ser, int(10000 * targetPwm / 100))
        sleep(0.05)
    ser.close()


if __name__ == '__main__':
    t = Thread(target=control)
    t.start()


