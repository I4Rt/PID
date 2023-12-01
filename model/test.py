import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLineEdit, QPushButton
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.animation import FuncAnimation
import numpy as np

import PID
import os
from reciever import *
from sender import *
from threading import *

TARGET_TEMPERATURE = 100

def setTarterTemperature(value):
    global TARGET_TEMPERATURE
    TARGET_TEMPERATURE = value
temperature = None
targetT = TARGET_TEMPERATURE
P = 50
I = 50
D = 100

pid = PID.PID(P, I, D)
pid.SetPoint = TARGET_TEMPERATURE
pid.setSampleTime(1)

def readConfig ():
        global targetT
        with open ('/tmp/pid.conf', 'r') as f:
            config = f.readline().split(',')
            pid.SetPoint = TARGET_TEMPERATURE
            targetT = pid.SetPoint
            pid.setKp (float(config[1]))
            pid.setKi (float(config[2]))
            pid.setKd (float(config[3]))

def createConfig ():
    if not os.path.isfile('/tmp/pid.conf'):
        with open ('/tmp/pid.conf', 'w') as f:
            f.write('%s,%s,%s,%s'%(TARGET_TEMPERATURE,P,I,D))
def control():
    global temperature
    global PID

    port = "COM5"  # Replace with the appropriate COM port name
    baudrate = 38400  # Replace with the desired baud rate
    ser = serial.Serial(port, baudrate=baudrate, timeout=0.1)
    ser.flush()
    createConfig()

    while True:
        readConfig()
        #read temperature data
        t = None
        while not t:
            t = getTemperature(ser, b'\x02\x04\x00\x00\x00\x02')
        print(t)
        pid.update(t)
        temperature = t
        targetPwm = pid.output
        targetPwm = max(min( int(targetPwm), 100 ),0)
        print ("Target: %.1f C | Current: %.1f C | PWM: %s %%"%(targetT, temperature, targetPwm))
        # Set PWM expansion channel 0 to the target setting
        set_power(ser, int(10000 * targetPwm / 100))
        sleep(0.05)
    ser.close()

t = Thread(target=control)
t.start()

class MyMplCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super(MyMplCanvas, self).__init__(fig)
        self.setParent(parent)

        self.x = np.linspace(0, 5, 100)
        self.line, = self.axes.plot(self.x, np.sin(self.x))

    def update_plot(self, frame):
        global temperature
        y = temperature
        self.line.set_ydata([y for i in range(0, 100)])
        return self.line,

    def init_plot(self):
        self.line.set_ydata(np.ma.array(self.x, mask=True))
        return self.line,

    def animate(self):
        animation = FuncAnimation(self.figure, self.update_plot, frames=100,
                                  init_func=self.init_plot, blit=True, interval=50)
        return animation

class ExtendedMainWindow(QMainWindow):
    def __init__(self):
        super(ExtendedMainWindow, self).__init__()

        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)
        layout = QVBoxLayout(self.central_widget)

        self.mpl_canvas = MyMplCanvas(self, width=5, height=4, dpi=100)
        layout.addWidget(self.mpl_canvas)

        # Добавление поля ввода
        self.input_line = QLineEdit(self)
        layout.addWidget(self.input_line)

        # Добавление кнопки
        self.set_button = QPushButton('Set', self)
        layout.addWidget(self.set_button)

        # Подключение события к кнопке
        self.set_button.clicked.connect(self.update_plot)

        self.animation = self.mpl_canvas.animate()  # Запуск анимации

    def update_plot(self):
        # Получение значения из поля ввода и использование его для обновления данных графика
        try:
            value = float(self.input_line.text())
            setTarterTemperature(int(value))
        except ValueError:
            print("Invalid input. Please enter a numeric value.")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_win = ExtendedMainWindow()
    main_win.show()
    sys.exit(app.exec_())
