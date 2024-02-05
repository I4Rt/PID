from tools.plant.PowerSupply import *
from tools.SerialConnection import *

from threads.StopableThread import *


class PowerSupplyInterface:
    
    def __init__(self, powerSupply:PowerSupply):
        
        self.readyToWork = False
        self.__powerSupply = powerSupply
        
        
        self.setAmperageValue = 0
        self.targetAmperageValue = 0
        self.needSetPower = False
        
        # self.needCriticalStop = False
        
        self.controlThread = StopableThread(True, target=self.__powerSupplyControllLoopStrp, args=[])
        
        
        
    def __powerSupplyControllLoopStrp(self):
        ser = SerialConnection.getInstance()
        if ser:
            self.__powerSupply.setAmpere(ser, self.targetAmperageValue)
            if self.needSetPower:
                res = self.__powerSupply.switchON(ser)
                
            self.setAmperageValue = self.__powerSupply.getAmperage(ser)
            
            
    def startWork(self):
        return self.controlThread.start()
    
    def pauseWork(self):
        return self.controlThread.pause()
                
    def stopWork(self):
        return self.controlThread.stop()
        
        