from time import time, sleep
from tools.PIDModels import *

class ViewState:
    instance = None
    
    def __init__(self):
        self.plot1Pause = True
        self.plot2Pause = True
        
        self.plot1Stopped = True
        self.plot2Stopped = True
        
        self.playTime1 = None
        self.pauseTime1 = None
        self.pauseDuration1 = 0
        self.playTime2 = None
        self.pauseTime2 = None
        self.pauseDuration2 = 0
        
        self.plot1TargetData = [[],[]]
        self.plot1RealData = [[],[]]
        self.plot2TargetData = []
        self.plot2RealData = []
        
        
        self.selectedPID = 'Степенная'
        self.tableData = []
        
        self.experiment = None
        
        self.K_1 = 0.
        self.K_2 = 0.
        self.K_3 = 0.
        self.K_4 = 0.
        self.K_5 = 0.
        
        self.K_1_industrial = 120
        self.K_2_industrial = 350

        self.spaceValue = 10.

        self.pidModule = PID(23)
        self.pidModuleIndustrial = IndustrialPID()
 
    def configPidParams(self):
        self.pidModule.k1 = self.K_1
        self.pidModule.k2 = self.K_2
        self.pidModule.k3 = self.K_3
        self.pidModule.k4 = self.K_4
        self.pidModule.k5 = self.K_5
        
        self.pidModuleIndustrial.k1 = self.K_1_industrial
        self.pidModuleIndustrial.k2 = self.K_2_industrial
    
    def getPower(self, curT, refT):
        if self.selectedPID == 'Промышленная':
            return self.pidModuleIndustrial.getPower(curT, refT)
        return self.pidModule.getPower(curT, refT)
    
    @classmethod
    def getState(cls):
        if not cls.instance:
            cls.instance = ViewState()
        return cls.instance
                   
    #PLOT1
    def pausePlot1(self):
        print('paused')
        if not self.plot1Stopped:
            self.plot1Pause = True
            self.pauseTime1 = time()
        
    def playPlot1(self):
        print('played')
        if self.plot1Stopped:
            self.playTime1 = time()
            self.pauseTime1 = None
            self.pauseDuration1 = 0
            self.plot1Pause = False
            self.plot1Stopped = False
        else:
            if self.pauseTime1:
                self.pauseDuration1 += time() - self.pauseTime1
                self.pauseTime1 = None
            self.plot1Pause = False
        
    def stopPlot1(self):
        print('stopped')
        self.plot1Pause = True
        self.plot1Stopped = True 
        
    def getPlot1NowTime(self):
        if self.playTime1:
            return time() - self.playTime1 - self.pauseDuration1
        return None
       
    #PLOT2
    def pausePlot2(self):
        if not self.plot2Stopped:
            self.plot2Pause = True
            self.pauseTime2 = time()
        
    def playPlot2(self):
        if self.plot2Stopped:
            self.playTime2 = time()
            self.pauseTime2 = None
            self.pauseDuration2 = 0
            self.plot2Pause = False
            self.plot2Stopped = False
        else:
            if self.pauseTime2:
                self.pauseDuration2 += time() - self.pauseTime2
                self.pauseTime2 = None
            self.plot2Pause = False
        
    def stopPlot2(self):
        self.plot2Pause = True
        self.plot2Stopped = True 
        
    def getPlot2NowTime(self):
        if self.playTime2:
            return time() - self.playTime2 - self.pauseDuration2
        return None
        
    
    
   
    
        
        
        
        