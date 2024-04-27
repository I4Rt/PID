from time import time, sleep



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
        now=time() * 100
        if self.prev_time != None:
            if now - self.prev_time < 500: # 5 sec
                return self.prev_power
        if T_cur == None:
            return self.prev_power
        
        
        
        self.T_prev, dt2 = self.prev_temperatures[-2] if len(self.prev_temperatures) > 2 else (T_cur, now - 1)
        # self.T_prev = min(T_cur - 1, self.T_prev)
        self.T_ref_prev = 20
        dt2 = now - dt2
        print(self.T_prev, dt2)
        dt1 = now - self.prev_time if self.prev_time else now - 1
        
        
        
        
        print('temperatures', T_cur, T_ref, self.T_ref_prev)
        print('dt1, dt2', dt1, dt2)
        #TODO:wrong formula? why dt2 is just time
        
        try:
            POWER = self.k1 * T_cur * (self.k4 ** (self.k2 + (T_cur - self.T_prev)/dt2 ) - self.k5 ** (self.k3 + (T_ref - T_cur) / (T_cur - self.T_ref_prev) )) / dt1
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

    def __init__(self, k1 = 120, k2 = 350, k3 = 1):
    
        self.k1 = k1 #Kp
        self.k2 = k2 #Ki
        self.k3 = k3 #Ki
        
        self.d_T_prev = None
        self.prev_time = None
        
        self.prev_power = 0
        self.prev_temperature = None
        
        self._pass_counter = 0
        
    
    def getPower(self, T_cur, T_ref):
        if T_cur == None:
            return self.prev_power
        
        now=round(time(),2)                      # in seconds
        if self.prev_time != None:
            if now - self.prev_time < 4:
                sleep(2 - (now - self.prev_time))
                now=round(time(),2)
                
        # if self.prev_temperature != None: # проверка погрешностей
            
        #     if abs(self.prev_temperature - T_cur) < 0.2:
        #         self._pass_counter += 1
        #         if self._pass_counter < 6:
        #             self.prev_time = now
        #             # self.d_T_prev = T_ref - T_cur # ??
        #             return self.prev_power
        #         else:
        #             self._pass_counter = 0
            
        if not self.prev_time:
            self.prev_time = now
            
        
        d_time = now - self.prev_time
        d_T = T_ref - T_cur
        if self.d_T_prev == None:
            self.d_T_prev = d_T
        #                                                   -?               /?
        POWER = self.k1*(d_T*self.k3 + min(max(-10**4, (d_T + self.d_T_prev) * d_time * self.k2), 10**4) )
        
        self.prev_power = POWER
        self.prev_time = now
        self.d_T_prev = d_T
        self.prev_temperature = T_cur
        
        print(f'\n\n\nPIDKOEFS\n{self.k1}, {self.k2}, {self.k3}\n\n\n')
        return POWER
    
    
    
    
    
class IndustrialPIDV2:

    def __init__(self, k1 = 120, k2 = 350, k3 = 1):
    
        self.k1 = k1 #Kp
        self.k2 = k2 #Ki
        self.k3 = k3 #Kd
        
        
        self.prev_time = None
        
        self.prev_power = 0
        self.prev_temperature = None
        
        self.__last_differences = []
        
    
    def getPower(self, T_cur, T_ref):
        if T_cur == None:
            return self.prev_power
        
        check_time = 10
        now=round(time(),2)                      # in seconds
        if self.prev_time != None:
            if now - self.prev_time < check_time - 1.:       # not ealier than 10 secs
                return self.prev_power
            elif now - self.prev_time < check_time:
                sleep(check_time - (time() - self.prev_time))
                now=round(time(), 2)
        
        time_delta = now - self.prev_time if self.prev_time != None else check_time # seconds
        E_cur = T_ref - T_cur
        E_prev = self.__last_differences[-1][0] if len(self.__last_differences) > 0 else E_cur
        
        
        
        I = min( 10000, max(-10000, sum(pair[0]*pair[1] for pair in self.__last_differences) + E_cur*time_delta)) # in -10^4 ... 10^4
        D = (E_cur - E_prev) / time_delta
        
        last_index = max(-6, -1*len(self.__last_differences)) # need index not greater than 4 rfom the end
        E_dif = 0 if len(self.__last_differences) == 0 else E_cur - self.__last_differences[last_index][0]
        time_sum = sum([self.__last_differences[i][1]  for i in range(-1, last_index, -1)]) + time_delta
        
        D_TEST = E_dif / time_sum
        
        POWER = self.k1*(E_cur + I/self.k2 + self.k3*D)
        
        print('\n\n\n\n\nDELTAS\n', 'time', time_delta, '\nt_real', T_cur, '\nt_target', T_ref )
        print('prev_power', self.prev_power, 'power', POWER, '\nI', I/self.k2, '\nD', self.k3*D, 'D_TEST', self.k3 * D_TEST, '\nP', E_cur, '\n\n\n\n\n',)
        
        self.__last_differences.append([E_cur, time_delta])
        self.__last_differences = self.__last_differences[-10:]
        
        self.prev_time = now
        self.prev_power = POWER
        
        return POWER