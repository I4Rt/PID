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
from tools.plant.ThermoGetter import *

from model.PowerSupplyInterface import *
from model.Apparats import *

from tools.SerialConnector import *
from model.ConnectionHolder import ConnectionHolder
    
import random
import serial
import os

try:
    os.environ["QT_DEBUG_PLUGINS"] = "1"
    Base.metadata.create_all(e)


    

    ConnectionHolder.changePort('COM3') 
            
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
                if powerSupply.getStatus(ConnectionHolder.getConnection()):
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
            print('switch on', h.swithON(ConnectionHolder.getConnection()))
            sleep(0.05)
            if min(i / 100, 10) == 10:
                break
        print('set voltage', h.setVoltage(ser, 0))
        h.swithOFF(ConnectionHolder.getConnection())
        

    def testVoltageGetter(ser:serial.Serial, looped = False):
        vg = VoltageGetter(b'\x01')
        
        begin = time()
        while looped or time() - begin < 100:
            print('cur voltage', vg.getVoltage(ConnectionHolder.getConnection()))
            sleep(0.5)



    def testPowerSupply2():
        ps = PowerSupply(b'\x05')
        ps.getStatus(ConnectionHolder.getConnection())
        print(ps.status)
        if ps.status == 0:
            print('amperage bofore set', ps.getAmperage(ConnectionHolder.getConnection()))
            print('set target res is', ps.setAmpere(ConnectionHolder.getConnection(), 1.2))
            print('switch on res is', ps.switchON(ConnectionHolder.getConnection()))
            print('amperage after set_1', ps.getAmperage(ConnectionHolder.getConnection()))
            sleep(2)
            print('amperage after set_2', ps.getAmperage(ConnectionHolder.getConnection()))
            sleep(8)
            print('amperage after sleep', ps.getAmperage(ConnectionHolder.getConnection()))
            print('switch off res is', ps.switchOFF(ConnectionHolder.getConnection()))
            print('amperage after swithc off', ps.getAmperage(ConnectionHolder.getConnection()))


            
    def testPowerSupply():
        ps = PowerSupply()
        ps.getStatus(ConnectionHolder.getConnection())
        ps.setAmpere(ConnectionHolder.getConnection(), 2.5)
        ps.switchON(ConnectionHolder.getConnection())
        sleep(10)
        ps.getAmperage(ConnectionHolder.getConnection())
        ps.switchOFF(ConnectionHolder.getConnection())
        
    def testMotorsRotate():
        m1 = Motor(b'\x04')
        res, msg, comment = m1.setPowerEnabled(ConnectionHolder.getConnection())
        if not res:
            return comment
        
        m1.stop(ConnectionHolder.getConnection())
        res, msg, comment = m1.setTurnSide(ConnectionHolder.getConnection())
        if not res:
            return comment
        res, msg, comment = m1.setTurnSpeed(ConnectionHolder.getConnection(), 0.001)
        if not res:
            return comment
        
        res, msg, comment = m1.move(ConnectionHolder.getConnection())
        if not res:
            return comment
        sleep(10)
        res = False
        while not res:
            res, msg, comment =  m1.stop(ConnectionHolder.getConnection())
        
    def testTemperatureGetter():
        tg = ThermoGetter(b'\x02', b'\x00\x06')
        while True:
            print(tg.getTemperature(ConnectionHolder.getConnection()))
            sleep(0.5)
        
    def testMotors():
        # ver-1
        # m1 = Motor(b'\x04')
        # m1.updateStatus(ConnectionHolder.getConnection())
        # m1.setPowerEnabled(ConnectionHolder.getConnection())
        # m1.updateStatus(ConnectionHolder.getConnection())
        # print(m1)
        # m1.setTurnSide(ConnectionHolder.getConnection())
        # m1.setTurnSpeed(ser, 1)
        # m1.move(ConnectionHolder.getConnection())
        # sleep(2)
        # m1.stop(ConnectionHolder.getConnection())
        
        # ver-2
        #
        m = Motor(b'\x03')
        m.stop()
        
        m1 = Motor(b'\x04')
        m1.stop(ConnectionHolder.getConnection())
        
        res, msg, comment = m.updateStatus(ConnectionHolder.getConnection())
        if not res:
            print(comment, msg)
        print(m)
        res, msg, comment = m.setTurnSpeed64000(ConnectionHolder.getConnection(), 0.2)
        if not res:
            print(comment, msg)
        res, msg, comment = m.setPowerEnabled(ConnectionHolder.getConnection())
        if not res:
            print(comment, msg)
        res, msg, comment = m.setTurnSide(ConnectionHolder.getConnection())
        if not res:
            print(comment, msg)
        res, msg, comment = m._setMoveDistance(ConnectionHolder.getConnection(), 100)
        if not res:
            print(comment, msg)
            
        
        m1.move(ConnectionHolder.getConnection())
        sleep(0.5)
        
        res, msg, comment = m._runMoveDistance(ConnectionHolder.getConnection())
        if not res:
            print(comment, msg)
            
        
        m.updateStatus(ConnectionHolder.getConnection())
        while not m.movingCompleted:
            res, msg, comment = m.updateStatus(ConnectionHolder.getConnection())
            if res:
                pass
            else:
                print(comment, msg)
            sleep(1)
            
        m1.stop(ConnectionHolder.getConnection())
        sleep(1)
        
        res, msg, comment = m._goHome(ConnectionHolder.getConnection())
        if not res:
            print(comment, msg)
        
        m.updateStatus(ConnectionHolder.getConnection())
        while not m.baseSearchFinished:
            m.updateStatus(ConnectionHolder.getConnection())
            sleep(0.1)
        print('finished')





    def addData():
        amperage = 40
        exp = Experiment.getByID(42)
        exp.dropAmperageData()
        exp.dropVoltageData()
        exp.dropThermocoupleData()
        for i in range(850):
            
            if i %100 ==0:
                amperage+=2
            realAmperage = max(amperage + random.randint(-100,100)/40, 0)
            exp.addAmperageData(realAmperage, amperage, i/10, False)
            realVoltage = max(40 - i/100 + random.randint(-10,10)/10, 0)
            exp.addVoltageData(realVoltage, i/10, False)
            if i % 50 == 0:
                exp.addThermocoupleData(min(63, 25 + i/50*15), i/10, False)

    # addData()   

    apparatController = ApparatController(ConnectionHolder.getConnection())
    apparatThread = StopableThread(True, target=apparatController.controllApparature, args=())
    apparatThread.start() 

    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow(ConnectionHolder.getConnection())
    def finish():
        app.exec_()
        apparatThread.stop()
        #принудительное выключение устройств
        try:
            powerSupply.switchOFF(ConnectionHolder.getConnection())
        except Exception as e:
            print('final power supply switch off error', e)
        try:
            heater.swithOFF(ConnectionHolder.getConnection())
        except Exception as e:
            print('final heater switch off error',e)
        

    # old code
    # window.startUpdate()
    # ui.startAutoSave()
    # ui.controlThread.start()
    # !old code

    if __name__ == "__main__":  
        #run app
        window.show()
        sys.exit(finish())

        
except Exception as e:
    print(e)
    