from time import time, sleep
from tools.PIDModels import *

from data.Experiment import *

class ViewState:
    instance = None
    
    def __init__(self):
        self.experiment:Experiment|None = None
        # controll assets
        self.plot1Pause = True
        self.plot2Pause = True
        
        self.plot1Stopped = True
        self.plot2Stopped = True
        
        self.firstPID1Run = True
        self.firstPID2Run = True
        
        self.playTime1 = None
        self.pauseTime1 = None
        self.pauseDuration1 = 0
        self.playTime2 = None
        self.pauseTime2 = None
        self.pauseDuration2 = 0
        
        # plot_2
        self.needAIM = True
        
        # plot assets
        self.plot1TargetData = [[],[]]
        self.plot1RealData = [[],[]]
        self.plot2TargetData = []
        self.plot2RealData = []
        self.plot2AmperageData = []
        self.plot2VoltageData = []
        
        
        # pid assets
        self.selectedPID = 'Степенная'
        self.tableData = []
        
        self.targetTemperature = None
        self.realTemperature = None

        # ! data in the view !
        self.K_1 = 0.
        self.K_2 = 0.
        self.K_3 = 0.
        self.K_4 = 0.
        self.K_5 = 0.
        
        self.K_1_industrial = 120
        self.K_2_industrial = 350

        self.spaceValue = 10.

        # pid models
        self.pidModule = PID(23)
        self.pidModuleIndustrial = IndustrialPID()
        
        
        
        # motors
        self.needShuffle = False
        self.needSearch0 = False
        self.needGoHome = False
        self.commandMotorVerticalIsRunning = False
        self.commandMotorRotateIsRunning = False
        self.needMoveDistance = False
        
        self.currentDeep = None
        self.targetDeep = 0
        self.needUpdateDeepth = False
        self.needStopVertical = False
        
        # powersupply
        self.targetAmperage = 0
        self.realAmperage = None
        
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
                   
    def setExperimentFSTarget(self, targetData:list[list[float]]|None=None):
        if not targetData:
            targetData = self.plot1TargetData
        print('targetData', targetData)
        expData = []
        size_ = len(targetData[0])
        print('size_', size_)
        for i in range(size_):
            x,y = targetData[1][i], targetData[0][i] # temperature, time
            expData.append([x,y])
        
            
        self.experiment.updateFSTargetProfile(expData)
        # self.experiment.save()
    
    # def setExperimentFSTarget(self, realData:list[list[float]]|None=None):
    #     if not realData:
    #         realData = self.plot1RealData
    #     print('realData', realData)
    #     expData = []
    #     size_ = len(realData[0])
    #     print('size_', size_)
    #     for i in range(size_):
    #         x,y = realData[1][i], realData[0][i] # temperature, time
    #         expData.append([x,y])
        
            
    #     self.experiment.updateFSRealProfile(expData)
    
    def getMotorTargetMove(self):
        return self.targetDeep - self.currentDeep
           
    #PLOT1
    def pausePlot1(self):
        print('paused')
        if not self.plot1Stopped:
            self.plot1Pause = True
            self.pauseTime1 = time()
        
    def playPlot1(self):
        print('played')
        if self.firstPID1Run:
            self.playTime1 = time()
            self.pauseTime1 = None
            self.pauseDuration1 = 0
            self.plot1Pause = False
            # self.plot1Stopped = False #commited now
            self.firstPID1Run = False
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
        if self.firstPID2Run:
            self.playTime2 = time()
            self.pauseTime2 = None
            self.pauseDuration2 = 0
            self.plot2Pause = False
            # self.plot2Stopped = False #commited now
            self.firstPID2Run = False
        else:
            if self.pauseTime2:
                self.pauseDuration2 += time() - self.pauseTime2
                self.pauseTime2 = None
            self.plot2Pause = False
        
    def stopPlot2(self):
        self.plot2Pause = True
        self.plot2Stopped = True 
        
    def getPlot2NowTime(self):
        # needCheck to continue from the time
        if self.playTime2:
            return time() - self.playTime2 - self.pauseDuration2
        return None
        
    #setters
    def togleAIM(self):
        self.needAIM = not self.needAIM
    
    def dropPlotTimes(self):
        self.plot1Pause = True
        self.plot2Pause = True
        
        self.plot1Stopped = False
        self.plot2Stopped = False
        
        self.firstPID1Run = True
        self.firstPID2Run = True
        
        self.playTime1 = None
        self.pauseTime1 = None
        self.pauseDuration1 = 0
        self.playTime2 = None
        self.pauseTime2 = None
        self.pauseDuration2 = 0
   
    
        
        
        
        