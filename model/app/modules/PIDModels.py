from time import time

class MyPID:
    def __init__(self, target):
        self.k1 = 10
        self.k2 = 1
        self.k3 = 1
        
        self.Tref = target
        self.Tref_prev = 25
        self.Tprev =  25
        
        self.prevTime = time()
        
        
    
    def setTarget(self, target):
        self.Tref_prev = self.Tref
        self.Tref = target
        
        
    def update(self, Tcur):
        now = time()
        deltaTime = now - self.prevTime 
        self.prevTime = now
        
        Idown =  ( Tcur - self.Tref_prev ) / 2 * deltaTime
        if Idown == 0:
            Idown = 0.001
        Iup = ( self.Tref - Tcur ) / 2 * deltaTime
        
        Tdelta = Tcur - self.Tprev
        divider = self.k2 * Tdelta + self.k3 * Iup / Idown
        if divider == 0:
            divider = 0.000001 
            
        POWER = (self.k1 / deltaTime) * (Tcur - self.Tref / divider)
        
        self.Tprev = Tcur
        
        return POWER
        
          
        
        
        