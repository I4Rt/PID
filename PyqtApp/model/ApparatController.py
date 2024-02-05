from model.ViewState import ViewState

from tools.plant.Reciever import *
from tools.plant.Sender import *
from tools.PIDModels import *

from model.Apparats import *

from tools.GraphTools import *

from time import time, sleep

class ApparatController():
    def __init__(self, ser):
        self.ser = ser
        self.pidModulePower = PID(23)
        self.pidModuleIndustrial = IndustrialPID()
        
        
        
    #control all fucken
    #TODO: make controlObjectsClasses
    def controllApparature(self):
        try:
            sleep(0.05)
            state = ViewState.getState()
            self.__pidControl(state)
            self.__motorsControl(state)
            # controll other booleans
        except Exception as e:
            # raise e
            # print('apparature error', e)
            pass
              
    def __pidControl(self, state:ViewState):
        needPID = False
        if not state.plot1Stopped:
            if not state.plot1Pause:
                x = state.getPlot1NowTime()
                print('time from the beginning:', x)
                refT = getYinX(x, state.experiment.getData(FSTargetDataMeasurement)) # need always save experiment model
                needPID = True
        elif not state.plot2Stopped:
            if not state.plot2Pause:
                x = state.getPlot2NowTime()
                refT = state.experiment.ssTarget # need always save experiment model
                needPID = True
        if needPID:
            # print('refT', refT)
            curT = getTemperature(self.ser, b'\x02\x04\x00\x00\x00\x02')
            state.configPidParams()
            powerLevel = max(0, min(state.getPower(curT, refT), 80))
            powerLevel = int(10000 * powerLevel / 100)
            swith_on(self.ser)
            set_power(self.ser, powerLevel)
            if not state.plot1Stopped:
                state.experiment.addFSRealData(curT, x)
            else:
                state.experiment.addSSRealData(curT, x)
                
    def __motorsControl(self, state:ViewState):
        #vartical
        if state.commandMotorVerticalIsRunning:
            if state.needStopVertical:
                print('\n\n\n\nstop vertical\n\n\n\n')
                res, exc, msg = motorVertical.stop(self.ser)
                if not res:
                    print('vertical motor exception(stop):', msg, (exc))
                    # error counter !
                else:
                    state.currentDeep = None
            
            res, exc, msg = motorVertical.updateStatus(self.ser)
            if not res:
                print('vertical motor exception(status):', msg, (exc))
                # error counter !
            else:
                print(motorVertical)
                state.commandMotorVerticalIsRunning = not (motorVertical.movingCompleted and motorVertical.baseSearchFinished)
                print('commandMotorVerticalIsRunning', state.commandMotorVerticalIsRunning)
                if motorVertical.baseSearchFinished or motorVertical.movingCompleted:
                    state.needUpdateDeepth = True

        else:
            res, exc, msg = motorVertical.setPowerEnabled(self.ser)
            if not res:
                print('vertical motor exception(enabled):', msg, (exc))
                # error counter !
            else:
                if state.needGoHome:
                    print('going home')
                    res, exc, msg = motorVertical._goHome(self.ser)
                    if not res:
                        print('vertical motor exception(go home):', msg, (exc))
                        # error counter !
                    else:
                        state.needGoHome = False
                        state.commandMotorVerticalIsRunning = True
                elif state.needMoveDistance:
                    
                    movement = state.getMotorTargetMove()
                    if movement > 0:
                        res, exc, msg =motorVertical.setTurnSide(self.ser)
                        print('setting turn side')
                    else:
                        res, exc, msg =motorVertical.setTurnSide(self.ser, False)
                        print('setting turn side')
                    if not res:
                        print('vertical motor exception(set move side):', msg, (exc))
                        # error counter !
                    else:
                        res, exc, msg = motorVertical._setMoveDistance(self.ser, abs(movement))
                        print('setting _setMoveDistance')
                        if not res:
                            print('vertical motor exception(setMoveDistance):', msg, (exc))
                            # error counter !
                        else:
                            res, msg, msg = motorVertical.setTurnSpeed64000(self.ser, 0.25)
                            print('setting set turn speed 64000')
                            
                            if not res:
                                print('vertical motor exception(set speed):', msg, (exc))
                                # error counter !
                            else:
                                res, exc, msg = motorVertical._runMoveDistance(self.ser)
                                print('running MoveDistance')
                                if not res:
                                    print('vertical motor exception(go run moveDistance):', msg, (exc))
                                    # error counter !
                                else:
                                    state.needMoveDistance = False
                                    state.commandMotorVerticalIsRunning = True
                                    print('command is running')
                      
        #rotate      
        if state.commandMotorRotateIsRunning:
            
            if not state.needShuffle:
                print('\n\n\n\nstop\n\n\n\n')
                res, exc, msg = motorRotate.stop(self.ser)
                if not res:
                    print('rotate motor exception(stop):', msg, (exc))
                    # error counter !
                else:
                    state.commandMotorRotateIsRunning = False
            print('update status')
            res, exc, msg = motorRotate.updateStatus(self.ser)
            if not res:
                print('rotate motor exception(status):', msg, (exc))
                # error counter !
            else:
                #state.commandMotorRotateIsRunning = not (motorRotate.commandCompleted and motorRotate.movingCompleted and motorRotate.baseSearchFinished)
                pass
        else:
            if state.needShuffle:
                print('set enabled')
                res, exc, msg = motorRotate.setPowerEnabled(self.ser)
                if not res:
                    print('rotate motor exception(set enabled):', msg, (exc))
                    if exc == 6:
                        state.commandMotorRotateIsRunning = True
                    # error counter !   
                else:
                    res, exc, msg = motorRotate.setTurnSpeed(self.ser, 0.5)
                    if not res:
                        print('rotate motor exception(setTurnSpeed):', msg, (exc))
                        # error counter !   
                    else:
                        print('move')
                        res, exc, msg = motorRotate.move(self.ser)
                        if not res:
                            print('rotate motor exception(move):', msg, (exc))
                            if exc == 6:
                                state.commandMotorRotateIsRunning = True
                            # error counter !
                        else:
                            state.commandMotorRotateIsRunning = True
                