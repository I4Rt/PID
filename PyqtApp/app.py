from config import *

from view.TabsViewPlain import *
from view.MainWindow import *
from view.QTDBSelector import *
from time import time 
import sys

from data.Experiment import Experiment
from data.Filling import Filling
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



os.environ["QT_DEBUG_PLUGINS"] = "1"
Base.metadata.create_all(e)



try: 
    f = open('run.tmp', 'r')
    f.close()
    app = QtWidgets.QApplication(sys.argv)
    msg = QtWidgets.QMessageBox()
    msg.setWindowTitle("Ошибка")
    msg.setText("Программа уже запущена")
    msg.exec_()
    sys.exit()
except:
    with open('run.tmp', 'w') as tmpFile:
        tmpFile.write('')
    
        

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
    try:
        os.remove('run.tmp')
    except Exception as e:
        print(e)


if __name__ == "__main__":  
    #run app
    window.show()
    sys.exit(finish())

    

