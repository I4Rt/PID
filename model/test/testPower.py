from time import time

from sender import *
from reciever import *

from matplotlib import pyplot as plt


if __name__ == '__main__':
    targets = [70 for i in range(200)] + [120 for i in range(200)] 
    prev_target = targets[0]
    plt.axis([0, len(targets) + 2, 20, 120])


    prev_temperatures = []
    prev_time = None
    T_ref_prev = 20

    prev_power = 0

    def add_temperature(t, time_):
        global prev_temperatures
        now = time() * 100 
        prev_temperatures.append((t, now))
        prev_temperatures = prev_temperatures[-200:]
        
    def get_power(t):
        global prev_time, prev_target, prev_temperatures, T_ref_prev, prev_power
        now=time() * 100
        T_cur = t
        T_prev, dt2 = prev_temperatures[-2] if len(prev_temperatures) > 2 else (t, now - 1)
        T_ref_prev = prev_temperatures[0][0] if len(prev_temperatures) > 50 else 20
        print(T_prev, dt2)
        dt1 = now - prev_time if prev_time else now - 1
        
        k1 = 550
        k2 = 2
        k3 = 1.6
        k4 = 0.5
        k5 = 0.4
        
        
        print('temperatures', T_cur, T_ref, T_ref_prev)
        print('dt1, dt2', dt1, dt2)
        
        
        try:
            POWER = k1 * T_cur * (k4 ** (k2 + (T_cur - T_prev)/dt2 ) - k5 ** (k3 + (T_ref - T_cur) / (T_cur - T_ref_prev) )) / dt1
        except ZeroDivisionError:
            POWER = prev_power
        except Exception:
            POWER = prev_power
        prev_power = POWER
        print('T_cur', T_cur, 'T_ref', T_ref, 'POWER', POWER)
        prev_time = now
        add_temperature(T_cur, now)
        
        return POWER


    port = "COM5"  # Replace with the appropriate COM port name
    baudrate = 38400  # Replace with the desired baud rate

    ser = serial.Serial(port, baudrate=baudrate, timeout=0.1)
    ser.flush()



    temperature_array = []



    switchedOn = swith_on(ser)
    counter = 0
    for target in targets:
        T_ref = target
        # T_ref_prev = 20
        
        counter += 1
        t = getTemperature(ser, b'\x02\x04\x00\x00\x00\x02')
        power = max(0, min(get_power(t), 100))
        print('______', int(1000 * power))
        tempSet = set_power(ser, int(10000 * power / 100))
        
        temperature_array.append(t)
        
        
        
        sleep(0.05)
        if prev_target != target:
            prev_target = target
            
    # counter = 0
    # for i in temperature_array:
    #     counter += 1

    plt.plot(temperature_array)
    plt.show()



class PID:
    def __init__(self,curT, k1 = 550, k2 = 2, k3 = 1.6, k4 = 0.5, k5 = 0.4):
        
        self.T_cur = curT
        self.k1 = k1
        self.k2 = k2
        self.k3 = k3
        self.k4 = k4
        self.k5 = k5
        self.prev_temperatures = []
        self.prev_time = None
        self.T_ref_prev = 20
        self.prev_power = 0
        
    def add_temperature(self, t, time_):
        now = time() * 100 
        self.prev_temperatures.append((t, now))
        self.prev_temperatures = self.prev_temperatures[-50:]
        
    def getPower(self, T_cur, T_ref):
        if T_cur == None:
            return self.prev_power
        
        now=time() * 100
        
        self.T_prev, dt2 = self.prev_temperatures[-2] if len(self.prev_temperatures) > 2 else (T_cur, now - 1)
        # self.T_prev = min(T_cur - 1, self.T_prev)
        self.T_ref_prev = 20
        
        print(self.T_prev, dt2)
        dt1 = now - self.prev_time if self.prev_time else now - 1
        
        k1 = 550
        k2 = 2
        k3 = 1.6
        k4 = 0.5
        k5 = 0.4
        
        
        print('temperatures', T_cur, T_ref, self.T_ref_prev)
        print('dt1, dt2', dt1, dt2)
        
        
        try:
            POWER = k1 * T_cur * (k4 ** (k2 + (T_cur - self.T_prev)/dt2 ) - k5 ** (k3 + (T_ref - T_cur) / (T_cur - self.T_ref_prev) )) / dt1
            self.T_cur = T_cur
        except ZeroDivisionError:
            POWER = self.prev_power
        except Exception:
            POWER = self.prev_power
        self.prev_power = POWER
        print('T_cur', T_cur, 'T_ref', T_ref, 'POWER', POWER)
        self.prev_time = now
        self.add_temperature(T_cur, now)
        
        return POWER
        
        
class IndustrialPID:

    def __init__(self, k1 = 120, k2 = 350):
    
        self.k1 = k1 #Kp
        self.k2 = k2 #Ki
        
        self.d_T_prev = None
        self.prev_time = None
        
        self.prev_power = None
        
    
    def getPower(self, T_cur, T_ref):
        if T_cur == None:
            return self.prev_power
        
        now=time()                      # in seconds
        if not self.prev_time:
            self.prev_time = now
            
        
        d_time = now - self.prev_time
        d_T = T_ref - T_cur
        if not self.d_T_prev:
            self.d_T_prev = d_T
        
        POWER = 100*(d_T + min(max(-10**4, (d_T + self.d_T_prev) * d_time / self.k2), 10**4) )/self.k1
        
        self.prev_power = min(max(POWER, 0), 80)
        self.prev_time = now
        return POWER