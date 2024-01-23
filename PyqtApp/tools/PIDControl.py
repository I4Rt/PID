from tools.plant.Reciever import *
from tools.plant.Sender import *
from tools.GraphTools import *
import serial
from model.ViewState import ViewState

def controllTemperature(getCurTempFunc, getRefTempFunc,configurePidFunc, calculateFunc, setPowerFunc, ser):
    try:
        sleep(0.05)
        state = ViewState.getState()
        if not state.plot1Pause and not state.plot1Stopped:
            curT = getCurTempFunc(ser)
            x = state.getPlot1NowTime()
            refT = getRefTempFunc(x, state.plot1TargetData[0], state.plot1TargetData[1])
            # print('refT', refT)
            configurePidFunc()
            powerLevel = max(0, min(calculateFunc(curT, refT), 80))
            
            setPowerFunc(ser, powerLevel)
            
            state.plot1RealData[0].append(x)
            state.plot1RealData[1].append(curT)
            
    except Exception as e:
        raise e
    

def getCurrentObjectTemperature(ser):
    return getTemperature(ser, b'\x02\x04\x00\x00\x00\x02')
    
def getCurrentTargetTempFunc(x, xData, yData):
    return getYinX(x, xData, yData)

def setObjectPower(ser, powerLevel):
    powerLevel = int(10000 * powerLevel / 100)
    swith_on(ser)
    set_power(ser, powerLevel)