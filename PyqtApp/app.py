from config import *

from view.TabsViewPlain import *
from view.MainWindow import *
from view.QTDBSelector import *
from time import time
import sys

from data.Experiment import Experiment
from data.SSRealDataMeasurement import *

from model.ApparatController import *
from threads.StopableThread import *
import data


from tools.plant.PowerSupply import *
from tools.plant.Motor import *
from tools.plant.VoltageGetter import *
from tools.plant.Heater import *

from model.PowerSupplyInterface import *
from model.Apparats import *

from tools.SerialConnector import *
        

Base.metadata.create_all(e)


import serial

try: 
    port = 'COM5'  # Replace with the appropriate COM port name
    baudrate = 19200  # Replace with the desired baud rate
    ser = serial.Serial(port, baudrate=baudrate, timeout=0.1, parity='E')
    ser.flush()
except Exception as e:
    print('ser exception', e)
    ser = None    
        
#auto com port getter
'''
portNameList = getExistPorts()
found = False
for portName, comment in portNameList:
    print('checking', portName, comment)
    if found:
        break
    ser = None
    try:
        if not comment.startswith('Стандартный последовательный порт по соединению Bluetooth'):
            port = portName  # Replace with the appropriate COM port name
            baudrate = 19200  # Replace with the desired baud rate
            ser = serial.Serial(port, baudrate=baudrate, timeout=0.1, parity='E')
            ser.flush()
            if powerSupply.getStatus(ser):
                found = True
    except Exception as e:
        print('ser exception', e)
        ser = None    
if not found:
    print('no com port connecion')
    sys.exit()
'''


def testVoltageSetter(ser:serial.Serial, looped = False):
    h = Heater(b'\x01')
    
    begin = time()
    i = 20
    while looped or time() - begin < 10:
        i += 20
        print('set voltage', h.setVoltage(ser, min(i / 100, 10)), min(i / 100, 10))
        print('switch on', h.swithON(ser))
        sleep(0.05)
        if min(i / 100, 10) == 10:
            break
    print('set voltage', h.setVoltage(ser, 0))
    h.swithOFF(ser)
    
    


def testVoltageGetter(ser:serial.Serial, looped = False):
    vg = VoltageGetter(b'\x01')
    
    begin = time()
    while looped or time() - begin < 100:
        print('cur voltage', vg.getVoltage(ser))
        sleep(0.5)


def testPowerSupply2():
    ps = PowerSupply()
    ps.getStatus(ser)
    print(ps.status)
    if ps.status == 0:
        print('amperage bofore set', ps.getAmperage(ser))
        print('set target res is', ps.setAmpere(ser, 1.2))
        print('switch on res is', ps.switchON(ser))
        print('amperage after set_1', ps.getAmperage(ser))
        sleep(2)
        print('amperage after set_2', ps.getAmperage(ser))
        sleep(8)
        print('amperage after sleep', ps.getAmperage(ser))
        print('switch off res is', ps.switchOFF(ser))
        print('amperage after swithc off', ps.getAmperage(ser))
        
def testPowerSupply():
    ps = PowerSupply()
    ps.getStatus(ser)
    ps.setAmpere(ser, 2.5)
    ps.switchON(ser)
    sleep(10)
    ps.getAmperage(ser)
    ps.switchOFF(ser)
    
def testMotors():
    # ver-1
    # m1 = Motor(b'\x04')
    # m1.updateStatus(ser)
    # m1.setPowerEnabled(ser)
    # m1.updateStatus(ser)
    # print(m1)
    # m1.setTurnSide(ser)
    # m1.setTurnSpeed(ser, 1)
    # m1.move(ser)
    # sleep(2)
    # m1.stop(ser)
    
    # ver-2
    m = Motor(b'\x03')
    m.stop()
    
    m1 = Motor(b'\x04')
    m1.stop(ser)
    
    res, msg, comment = m.updateStatus(ser)
    if not res:
        print(comment, msg)
    print(m)
    res, msg, comment = m.setTurnSpeed64000(ser, 0.2)
    if not res:
        print(comment, msg)
    res, msg, comment = m.setPowerEnabled(ser)
    if not res:
        print(comment, msg)
    res, msg, comment = m.setTurnSide(ser)
    if not res:
        print(comment, msg)
    res, msg, comment = m._setMoveDistance(ser, 100)
    if not res:
        print(comment, msg)
        
    
    m1.move(ser)
    sleep(0.5)
    
    res, msg, comment = m._runMoveDistance(ser)
    if not res:
        print(comment, msg)
        
    
    m.updateStatus(ser)
    while not m.movingCompleted:
        res, msg, comment = m.updateStatus(ser)
        if res:
            pass
        else:
            print(comment, msg)
        sleep(1)
        
    m1.stop(ser)
    sleep(1)
    
    res, msg, comment = m._goHome(ser)
    if not res:
        print(comment, msg)
    
    m.updateStatus(ser)
    while not m.baseSearchFinished:
        m.updateStatus(ser)
        sleep(0.1)
    print('finished')

# testVoltageSetter(ser, True)
# sys.exit()

apparatController = ApparatController(ser)
apparatThread = StopableThread(True, target=apparatController.controllApparature, args=())
apparatThread.start() 

app = QtWidgets.QApplication(sys.argv)
window = MainWindow()
def finish():
    app.exec_()
    apparatThread.stop()
    

# old code
# window.startUpdate()
# ui.startAutoSave()
# ui.controlThread.start()
# !old code

if __name__ == "__main__":  
    #run app
    window.show()
    sys.exit(finish())

    
