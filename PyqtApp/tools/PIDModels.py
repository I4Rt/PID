from time import time



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