from time import time

class MyPID:
    def __init__(self,k1,k2,k3):
        self.k1 = 10
        self.k2 = 1
        self.k3 = 1
        
        self.Tref = 25 **3
        self.Tref_prev = 25 **3
        self.Tprev =  25 **3
        self.k4 = 10
        self.prevTime = time()
        
        
    
    def setTarget(self, target):
        if self.Tref != target ** 3:
            self.Tref_prev = self.Tref
            self.Tref = target ** 3
        
        
    def update(self, Tcur):
        now = time()
        deltaTime = int( (now - self.prevTime ) * 100 )# ms
        print('time ', deltaTime)
        self.prevTime = now
        
        
        Tcur = Tcur ** 3
        
        Idown =  ( Tcur - self.Tref_prev ) / 2 * deltaTime
        if Idown == 0:
            print( 'zero integral' )
            Idown = 0.01
        Iup = ( self.Tref - Tcur ) / 2 * deltaTime
        
        print('idown', Idown)
        print('iup', Iup)
        
        Tdelta = Tcur - self.Tprev
        print('delta temperature', Tdelta)
        
        divider = self.k2 * Tdelta + self.k3 * Iup / Idown
        print('divider', divider)
        
        if divider == 0:
            print( 'zeroDevider' )
            divider = 0.01 
            
        POWER = (self.k1 / deltaTime) * (Tcur + self.k4 * self.Tref / divider)
        
        self.Tprev = Tcur
        
        return POWER
        
          
        
        
        