from model.ViewState import ViewState

from tools.plant.Reciever import *
from tools.plant.Sender import *
from tools.PIDModels import *

from model.Apparats import *
from model.ConnectionHolder import ConnectionHolder

from tools.GraphTools import *
import tools.PidSideControllers as pidTools

from time import time, sleep

class ApparatController():
    def __init__(self, ser):
        # self.pidModulePower = PID(23)
        # self.pidModuleIndustrial = IndustrialPID()
        self.lastSaveTime = None
    
    
    #control all fucken
    #TODO: make controlObjectsClasses
    def controllApparature(self):
        
        try:
            state = ViewState.getState()
            self.updateStatuses()
            sleep(0.2)
            
            x1 = state.getPlot1NowTime()
            x2 = state.getPlot2NowTime()
            
            pidWorks = self.__pidControlUpdated(state, x1, x2)
            print('pidWorks', pidWorks)
            self.__motorsControl(state)
            # controll other booleans
            
            self.__powerSupplyControl(state)
            self.__voltageControl(state)
            
            
            
            #alram
            if not state.plot1Pause or not state.plot2Pause:
                if abs(state.realTemperature-state.targetTemperature) > state.spaceValue:
                    state.needAlram=True
                elif state.realAmperage:
                    if abs(state.realAmperage-state.targetAmperage) > state.amperageSpace:
                        state.needAlram=True
                    else:
                        state.needAlram=False
                else:
                    state.needAlram=False
            else:
                state.needAlram=False
            
            
            with open(f'bug-catch{str(datetime.now())[:10]}.txt', 'a') as file:
                
                file.write(f'state.plot1Stopped {state.plot1Stopped}\n')
                file.write(f'state.plot2Stopped {state.plot2Stopped}\n')
                file.write(f'lastSaveTime {self.lastSaveTime}\n')
                file.write(f'now {datetime.now()}\n')
                file.write(f'pidWorks {pidWorks}\n\n\n')
    
            # add params
            if pidWorks: #TODO: add time intervales
                now = time()
                needSave=False
                if not self.lastSaveTime:
                    
                    self.lastSaveTime = now
                    needSave = True
                elif now - self.lastSaveTime >= 30: #last save time bug
                    self.lastSaveTime = now
                    needSave = True
                
                
                
                
                

                if not state.plot1Stopped:
                    if needSave:
                        state.experiment.addFSRealData(state.realTemperature, x1)
                elif not state.plot2Stopped:
                    self.__thermocoupleControl(state, x2)
                    if needSave:                                   # need save bug
                        state.lastSSTime = x2
                        state.experiment.addSSRealData(state.realTemperature, x2)
                        state.experiment.addAmperageData(state.realAmperage, state.targetAmperage if state.powerIsOn else 0, x2)
                        state.experiment.addVoltageData(state.realVolrage, x2)
                        
                        if state.needSaveThermocouple:
                            # print('\n\n\nneed thermocoupe.save\n\n\n', not (state.realThermocouple is None))
                            if not (state.realThermocouple is None):
                                state.experiment.addThermocoupleData(state.realThermocouple, x2)
                                # print('\n\n\nthermocoupe.save\n\n\n')
                            state.needSaveThermocouple = False
            else:
                
                heater.swithOFF(ConnectionHolder.getConnection())
                state.curPower = 0.
                state.needAlram = False
                state.mute = False # нужно ли
                
        except Exception as e:
            with open(f'bug-catch{str(datetime.now())[:10]}.txt', 'a') as file:
                file.write(f'{datetime.now()}\nexception {e}\n\n\n')
            # raise e
            print('apparature error', e)
            pass
         
    def updateStatuses(self,):
        state = ViewState.getState()
        # print('connection', ConnectionHolder.getConnection())
        if ConnectionHolder.getConnection() != None:
            try:
                t1 = thermoCoupleMainGetter.getTemperature(ConnectionHolder.getConnection())
                t2 = thermoCoupleOuterGetter.getTemperature(ConnectionHolder.getConnection())
                
                m1_status, msg, comment = motorRotate.updateStatus(ConnectionHolder.getConnection())
                m2_status, msg, comment = motorVertical.updateStatus(ConnectionHolder.getConnection())
                
                h_status = voltageGetter.getVoltage(ConnectionHolder.getConnection())
                ps_status = powerSupply.getStatus(ConnectionHolder.getConnection())
                
                # print('statuses', t1,t2,m1_status,m2_status,h_status,ps_status)
                state.thermocouple1Error = True if t1 is None else False
                state.thermocouple2Error = True if t2 is None else False
                state.indipendTemperature = t1
                state.motor1Error        = not m1_status
                state.motor2Error        = not m2_status
                state.heaterError        = not h_status
                state.powerError         = not ps_status
                return
            except Exception as e:
                print('status error update', e)
        state.thermocouple1Error = True
        state.thermocouple2Error = True  
        state.motor1Error        = True 
        state.motor2Error        = True 
        state.heaterError        = True             
        state.powerError         = True 

        
    # old version
    def __pidControl(self, state:ViewState, x1:float, x2:float):
        needPID = False
        if not state.plot1Stopped:
            if not state.plot1Pause:
                x = x1
                print('time from the beginning:', x)
                state.targetTemperature = refT = getYinX(x, state.experiment.getData(FSTargetDataMeasurement)) # need always save experiment model
                needPID = True
        elif not state.plot2Stopped:
            if not state.plot2Pause:
                x = x2
                state.targetTemperature = refT = state.experiment.ssTarget # need always save experiment model
                needPID = True
        if needPID:
            # print('refT', refT)
            state.realTemperature = curT = getTemperature(ConnectionHolder.getConnection(), b'\x02\x04\x00\x00\x00\x02')
            state.configPidParams()
            state.curPower = max(0, min(state.getPower(curT, pidTools.temperatureCorrector(refT, 3.5))), pidTools.maxPowerCorrector(curT))   #update of 03.05.24     #pidTools.temperatureCorrector(refT)), pidTools.maxPowerCorrector(curT)))
            powerLevel = int(10000 * state.curPower / 100)
            swith_on(ConnectionHolder.getConnection())
            set_power(ConnectionHolder.getConnection(), powerLevel)
            
            if state.plot2Pause:
                state.realTemperature_1 = curT
            else:
                state.realTemperature_2 = curT
        return needPID
    
    def __pidControlUpdated(self, state:ViewState, x1:float, x2:float):
        
        
        needPID = False
        x = None
        if not state.plot1Stopped:
            if not state.plot1Pause:
                x = x1
                # print('time from the beginning:', x)
                track = state.experiment.getData(FSTargetDataMeasurement)
                state.targetTemperature = getYinX(x/60, track)
                refT = getYinX((x+state.timeKoefValue)/60, track) # need always save experiment model
                # print('time koef collibration', x/60, state.timeKoefValue, (x+state.timeKoefValue)/60, refT)
                needPID = True
        elif not state.plot2Stopped:
            if not state.plot2Pause:
                x = x2
                
                state.targetTemperature = refT = state.experiment.ssTarget # need always save experiment model
                needPID = True
                
        # print('inside pid state.plot1Stopped', state.plot1Stopped)
        # print('inside pid state.plot1Pause', state.plot1Pause)
        # print('inside pid state.plot1Stopped', state.plot1Stopped)
        # print('inside pid state.plot1Pause', state.plot1Pause)
        # print('inside pid needPID', needPID, '\n\n\n')
        
        state.currentTime = x
        if needPID:
            # print('refT', refT)
            state.realTemperature = curT = thermoCoupleMainGetter.getTemperature(ConnectionHolder.getConnection())
            # print('realTemperature', state.realTemperature)
            state.configPidParams()
            # print('PID',
            #       state.pidModule.k1,
            #       state.pidModule.k2,
            #       state.pidModule.k3,
            #       state.pidModule.k4,
            #       state.pidModule.k5,
            #       state.selectedPID, sep='\n')
            
            temperatureDelta = pidTools.getTemperatureUpscale(refT)
            # temperatureDelta = 0.
            state.tempDelta = temperatureDelta
            state.curPower = max(0, min(state.getPower(curT, refT + temperatureDelta), pidTools.maxPowerCorrector(curT)))
                # state.curPower = max(0, min(state.getPower(curT, refT), 90))
            # else:
            #     state.curPower = 25.0
            powerLevel = round(state.curPower/10, 2)
    
            # print('power (voltage)', powerLevel)
            heater.swithON(ConnectionHolder.getConnection())
            heater.setVoltage(ConnectionHolder.getConnection(), powerLevel)
            
            if state.plot2Pause:
                state.realTemperature_1 = curT
            else:
                state.realTemperature_2 = curT
        
        return needPID

                
    def __motorsControl(self, state:ViewState):
        
        #vartical
        if state.needSearchZero:
            # print('needSearchZero')
            res, exc, msg = motorVertical.updateStatus(ConnectionHolder.getConnection())
            if not res:
                print('vertical motor exception(status):', msg, (exc))
                return
            else:
                # print('bools', motorVertical.movingCompleted, '\n')
                if motorVertical.movingCompleted:
                    found = False
                    if state.realAmperage:
                        if state.realAmperage > 0.5:
                            found = True
                    if found:
                        state.zeroDeep = 0 #state.currentDeep
                        state.needSearchZero = False
                        state.commandMotorVerticalIsRunning = False
                        state.targetAmperage = 0
                        state.powerIsOn = False
                    else:
                        res, exc, msg = motorVertical.setPowerEnabled(ConnectionHolder.getConnection())
                        if not res:
                            print('vertical motor exception(enabled):', msg, (exc))
                            # error counter !
                        else:
                            res, exc, msg =motorVertical.setTurnSide(ConnectionHolder.getConnection())
                            if not res:
                                print('vertical motor exception(setTurnSide):', msg, (exc))
                                # error counter !
                            else:
                                res, exc, msg = motorVertical._setMoveDistance(ConnectionHolder.getConnection(), abs(1.0))
                                if not res:
                                    print('vertical motor exception(setMoveDistance):', msg, (exc))
                                    # error counter !
                                else:
                                    res, msg, msg = motorVertical.setTurnSpeed64000(ConnectionHolder.getConnection(), 0.1)
                                    if not res:
                                        print('vertical motor exception(set speed):', msg, (exc))
                                        # error counter !
                                    else:
                                        res, exc, msg = motorVertical._runMoveDistance(ConnectionHolder.getConnection())
                                        print('running MoveDistance')
                                        if res:
                                            state.currentDeep += 1
        else:
            if state.commandMotorVerticalIsRunning:
                # if state.needStopVertical:
                #     print('\n\n\n\nstop vertical\n\n\n\n')
                #     res, exc, msg = motorVertical.stop(ConnectionHolder.getConnection())
                #     if not res:
                #         print('vertical motor exception(stop):', msg, (exc))
                #         # error counter !
                #     else:
                #         state.currentDeep = None
                
                res, exc, msg = motorVertical.updateStatus(ConnectionHolder.getConnection())
                if not res:
                    print('vertical motor exception(status):', msg, (exc))
                    # error counter !
                else:
                    state.commandMotorVerticalIsRunning = not (motorVertical.movingCompleted and motorVertical.baseSearchFinished)
                    print('commandMotorVerticalIsRunning', state.commandMotorVerticalIsRunning)
                    if motorVertical.baseSearchFinished or motorVertical.movingCompleted:
                        state.needUpdateDeepth = True
                    

            else:
                res, exc, msg = motorVertical.setPowerEnabled(ConnectionHolder.getConnection())
                if not res:
                    print('vertical motor exception(enabled):', msg, (exc))
                    # error counter !
                else:
                    if state.needGoHome:
                        
                        print('going home')
                        res, exc, msg = motorVertical._goHome(ConnectionHolder.getConnection())
                        if not res:
                            print('vertical motor exception(go home):', msg, (exc))
                            state.currentDeep = None
                            # error counter !
                        else:
                            state.zeroDeep = None
                            state.needGoHome = False
                            state.commandMotorVerticalIsRunning = True
                    elif state.needMoveDistance:
                        
                        movement = state.getMotorTargetMove()
                        if movement > 0:
                            res, exc, msg =motorVertical.setTurnSide(ConnectionHolder.getConnection())
                            print('setting turn side')
                        else:
                            res, exc, msg =motorVertical.setTurnSide(ConnectionHolder.getConnection(), False)
                            print('setting turn side')
                        if not res:
                            print('vertical motor exception(set move side):', msg, (exc))
                            # error counter !
                        else:
                            res, exc, msg = motorVertical._setMoveDistance(ConnectionHolder.getConnection(), abs(movement))
                            print('setting _setMoveDistance')
                            if not res:
                                print('vertical motor exception(setMoveDistance):', msg, (exc))
                                # error counter !
                            else:
                                res, msg, msg = motorVertical.setTurnSpeed64000(ConnectionHolder.getConnection(), 0.3125)
                                print('setting set turn speed 64000')
                                
                                if not res:
                                    print('vertical motor exception(set speed):', msg, (exc))
                                    # error counter !
                                else:
                                    res, exc, msg = motorVertical._runMoveDistance(ConnectionHolder.getConnection())
                                    print('running MoveDistance')
                                    if not res:
                                        print('vertical motor exception(go run moveDistance):', msg, (exc))
                                        # error counter !
                                        state.currentDeep = None
                                    else:
                                        state.needMoveDistance = False
                                        state.commandMotorVerticalIsRunning = True
                                        print('command is running')
                      
        #rotate      
        if state.commandMotorRotateIsRunning:
            
            if not state.needShuffle:
                print('\n\n\n\nstop\n\n\n\n')
                res, exc, msg = motorRotate.stop(ConnectionHolder.getConnection())
                if not res:
                    print('rotate motor exception(stop):', msg, (exc))
                    # error counter !
                else:
                    state.commandMotorRotateIsRunning = False
            print('update status')
            res, exc, msg = motorRotate.updateStatus(ConnectionHolder.getConnection())
            if not res:
                print('rotate motor exception(status):', msg, (exc))
                # error counter !
            else:
                #state.commandMotorRotateIsRunning = not (motorRotate.commandCompleted and motorRotate.movingCompleted and motorRotate.baseSearchFinished)
                pass
        else:
            if state.needShuffle:
                if state.smashSpeed != 0:
                    print('set enabled')
                    res, exc, msg = motorRotate.setPowerEnabled(ConnectionHolder.getConnection())
                    if not res:
                        print('rotate motor exception(set enabled):', msg, (exc))
                        if exc == 6:
                            state.commandMotorRotateIsRunning = True
                        # error counter !   
                    else:
                        if state.smashSpeed > 0:
                            res, exc, msg = motorRotate.setTurnSide(ConnectionHolder.getConnection())
                        else:
                            res, exc, msg = motorRotate.setTurnSide(ConnectionHolder.getConnection(), False)
                        if not res:
                            print('rotate motor exception(setTurnSide):', msg, (exc))
                            # error counter !   
                        else:  
                            res, exc, msg = motorRotate.setTurnSpeed(ConnectionHolder.getConnection(), abs(state.smashSpeed / 60) )
                            if not res:
                                print('rotate motor exception(setTurnSpeed):', msg, (exc))
                                # error counter !   
                            else:
                                print('move')
                                res, exc, msg = motorRotate.move(ConnectionHolder.getConnection())
                                if not res:
                                    print('rotate motor exception(move):', msg, (exc))
                                    if exc == 6:
                                        state.commandMotorRotateIsRunning = True
                                    # error counter !
                                else:
                                    state.commandMotorRotateIsRunning = True

                
    def __powerSupplyControl(self, state:ViewState):

        # needSetAmperage = False
        # if not state.plot2Stopped:
        #     if not state.plot2Pause:
        #         needSetAmperage = True
        # if needSetAmperage:
        if state.powerIsOn:
            res = powerSupply.getStatus(ConnectionHolder.getConnection())
            if res:
                if powerSupply.status == 0:
                    res = powerSupply.setAmpere(ConnectionHolder.getConnection(), max(0, state.targetAmperage)) # TODO: maximum set 10 for now
                    if res:
                        res = powerSupply.switchON(ConnectionHolder.getConnection())
                        if not res:
                            print('error switch on power supply')
                    else:
                        print('error set amperage power supply')
                else:
                    print('\n\nswitch off 1')
                    powerSupply.switchOFF(ConnectionHolder.getConnection())
                    print('error status power supply', powerSupply.status)
            else:
                print('\n\nswitch off 2')
                powerSupply.switchOFF(ConnectionHolder.getConnection())
                print('error status power supply', 'command did not proceed')
        else:
            print('\n\nswitch off 3')
            res = powerSupply.switchOFF(ConnectionHolder.getConnection())
            if not res:
                print('power supply switch off error')
                    
        amperageRes = powerSupply.getAmperage(ConnectionHolder.getConnection())
        if amperageRes >= 0:
            state.realAmperage = amperageRes
        else:
            print('power supply switch off error')


    def __thermocoupleControl(self, state:ViewState, x2:float):
        temperature = thermoCoupleOuterGetter.getTemperature(ConnectionHolder.getConnection())
        state.realThermocouple = None if temperature is None and state.realThermocouple is None else temperature
        pass
                    
    def __voltageControl(self, state:ViewState):
        # voltage = powerSupply.getVoltage(ConnectionHolder.getConnection()) #TODO: temp
        voltage = voltageGetter.getVoltage(ConnectionHolder.getConnection())
        if voltage != -1:
            state.realVolrage = round(voltage, 2)
            # print('voltage,', voltage)