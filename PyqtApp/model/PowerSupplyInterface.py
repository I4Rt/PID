from tools.plant.PowerSupply import *

from threads.StopableThread import *


class PowerSupplyInterface:
    
    def __init__(self, powerSupply:PowerSupply, ser:serial.Serial):
        
        self.readyToWork = False
        self.__powerSupply = powerSupply
        self.ser = self.ser
        
        
        self.setAmperageValue = 0
        self.targetAmperageValue = 0
        self.needSetPower = False
        
        # self.needCriticalStop = False
        
        self.controlThread = StopableThread(True, target=self.__powerSupplyControllLoopStrp, args=[])
        
        
        
    def __powerSupplyControllLoopStrp(self):
        
        if self.ser:
            self.__powerSupply.setAmpere(self.ser, self.targetAmperageValue)
            if self.needSetPower:
                res = self.__powerSupply.switchON(self.ser)
                
            self.setAmperageValue = self.__powerSupply.getAmperage(self.ser)
            
            
    def startWork(self):
        return self.controlThread.start()
    
    def pauseWork(self):
        return self.controlThread.pause()
                
    def stopWork(self):
        return self.controlThread.stop()
        
        