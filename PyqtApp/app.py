from config import *

from view.TabsView import *
from time import time
import sys

from data.Experiment import Experiment
from data.SSRealDataMeasurement import *
import data
Base.metadata.create_all(e)


import serial
try:
    port = "COM5"  # Replace with the appropriate COM port name
    baudrate = 38400  # Replace with the desired baud rate
    ser = serial.Serial(port, baudrate=baudrate, timeout=0.1)
    ser.flush()
except:
    ser = None


app = QtWidgets.QApplication(sys.argv)
MainWindow = QtWidgets.QMainWindow()
ui = Ui_MainWindow(ser)
ui.setupUi(MainWindow)
# ui.startUpdate()
# ui.controlThread.start()

def finish():
    # with flask_app.app_context():
    Experiment.deleteAll()
    print('\n\n\nhere\n\n\n')
    exp = Experiment('ptf', 'kjffffkldfk')
    exp.setSSTarget(30)
    exp.addFSRealData(30, 0)
    exp.addFSRealData(31, 15)
    
    exp.updateFSTargetProfile([[30, 0], [100, 50], [100, 100]])
    exp.save()
    
    print(exp.getData(SSRealDataMeasurement))
    
    # app.exec_()
    
    # ui.controlThread.stop()
    
    
if __name__ == "__main__":    
    # MainWindow.show()
    
    sys.exit(finish())
    
    