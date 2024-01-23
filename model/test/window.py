from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QTimer, QAbstractTableModel
from pyqtgraph.widgets.MatplotlibWidget import MatplotlibWidget
import numpy as np

from matplotlib.lines import Line2D

from random import randint

from threading import Thread
from time import time, sleep

class Ui_MainWindow(object):
    
    
    def __init__(self):
        object.__init__(self)
        self.curModelName = 'Степенная'
        self.plotData = [[], []]
        self.realPlotData = [[], []]
        self.K_1 = 0.
        self.K_2 = 0.
        self.K_3 = 0.
        self.K_4 = 0.
        self.K_5 = 0.
        self.inProgrewss = False
        self.startTime = time()
        
    def startUpdate(self):
        # Repeating timer, calls random_pick over and over.
        self.ui_target_plot_data,  = self.subplot.plot(self.plotData[0], self.plotData[1]) 
        self.ui_real_plot_data,  = self.subplot.plot(np.array(self.realPlotData[0]), self.realPlotData[1]) 
        self.plotupdater = QTimer()
        self.plotupdater.setInterval(500)
        self.plotupdater.timeout.connect(self.updatePlot)
        self.plotupdater.start()

    def updatePlot(self):
        # self.graphicsView.getFigure().gca().fill_between(self.plotData[0], np.array(self.plotData[1]) - 1, np.array(self.plotData[1]) + 1, color="#3F5D7D") 
        # updating data values
        self.ui_target_plot_data.set_xdata(self.plotData[0])
        self.ui_target_plot_data.set_ydata(self.plotData[1])
        
        self.ui_real_plot_data.set_xdata(self.realPlotData[0])
        self.ui_real_plot_data.set_ydata(self.realPlotData[1])
        # drawing updated values
        self.graphicsView.getFigure().canvas.draw_idle()
        
        # self.graphicsView.draw()  
        
        
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1126, 896)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")
        self.formLayout = QtWidgets.QFormLayout()
        self.formLayout.setObjectName("formLayout")
        self.label_6 = QtWidgets.QLabel(self.centralwidget)
        self.label_6.setObjectName("label_6")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label_6)
        self.cur_model_layout = QtWidgets.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.cur_model_layout.setFont(font)
        self.cur_model_layout.setObjectName("cur_model_layout")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.cur_model_layout)
        self.gridLayout.addLayout(self.formLayout, 0, 1, 1, 1)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.graphicsView = MatplotlibWidget(self.centralwidget)
        self.subplot = self.graphicsView.getFigure().add_subplot()
        self.subplot.set_xlim(0, 400)
        self.subplot.set_ylim(0, 400)
        
        
    
        self.horizontalLayout.addWidget(self.graphicsView)
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)
        self.k1_input = QtWidgets.QDoubleSpinBox(self.centralwidget)
        self.k1_input.setObjectName("k1_input")
        self.k1_input.valueChanged.connect(lambda: self.setK_1(self.k1_input.value()))
        self.verticalLayout.addWidget(self.k1_input)
        
        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        self.label_2.setObjectName("label_2")
        self.verticalLayout.addWidget(self.label_2)
        self.k2_input = QtWidgets.QDoubleSpinBox(self.centralwidget)
        self.k2_input.setObjectName("k2_input")
        self.verticalLayout.addWidget(self.k2_input)
        self.k2_input.valueChanged.connect(lambda: self.setK_2(self.k2_input.value()))
        
        self.label_3 = QtWidgets.QLabel(self.centralwidget)
        self.label_3.setObjectName("label_3")
        self.verticalLayout.addWidget(self.label_3)
        self.k3_input = QtWidgets.QDoubleSpinBox(self.centralwidget)
        self.k3_input.setObjectName("k3_input")
        self.verticalLayout.addWidget(self.k3_input)
        self.k3_input.valueChanged.connect(lambda: self.setK_3(self.k3_input.value()))
        
        self.label_4 = QtWidgets.QLabel(self.centralwidget)
        self.label_4.setObjectName("label_4")
        self.verticalLayout.addWidget(self.label_4)
        self.k4_input = QtWidgets.QDoubleSpinBox(self.centralwidget)
        self.k4_input.setObjectName("k4_input")
        self.k4_input.valueChanged.connect(lambda: self.setK_4(self.k4_input.value()))
        self.verticalLayout.addWidget(self.k4_input)
        
        self.label_5 = QtWidgets.QLabel(self.centralwidget)
        self.label_5.setObjectName("label_5")
        self.verticalLayout.addWidget(self.label_5)
        self.k5_input = QtWidgets.QDoubleSpinBox(self.centralwidget)
        self.k5_input.setObjectName("k5_input")
        self.k5_input.valueChanged.connect(lambda: self.setK_5(self.k5_input.value()))
        self.verticalLayout.addWidget(self.k5_input)
        
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton.setObjectName("pushButton")
        self.verticalLayout.addWidget(self.pushButton)
        self.horizontalLayout.addLayout(self.verticalLayout)
        self.gridLayout.addLayout(self.horizontalLayout, 3, 1, 1, 1)
        # Table
        
        self.tableWidget = QtWidgets.QTableWidget(self.centralwidget)
        self.tableWidget.setMinimumSize(QtCore.QSize(301, 0))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tableWidget.sizePolicy().hasHeightForWidth())
        self.tableWidget.setSizePolicy(sizePolicy)
        self.tableWidget.setColumnCount(2)
        self.tableWidget.setRowCount(30)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setVerticalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setVerticalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setVerticalHeaderItem(2, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setVerticalHeaderItem(3, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setVerticalHeaderItem(4, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setVerticalHeaderItem(5, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setVerticalHeaderItem(6, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setVerticalHeaderItem(7, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setVerticalHeaderItem(8, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setVerticalHeaderItem(9, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setVerticalHeaderItem(10, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setVerticalHeaderItem(11, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setVerticalHeaderItem(12, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setVerticalHeaderItem(13, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setVerticalHeaderItem(14, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setVerticalHeaderItem(15, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setVerticalHeaderItem(16, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setVerticalHeaderItem(17, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setVerticalHeaderItem(18, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setVerticalHeaderItem(19, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setVerticalHeaderItem(20, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setVerticalHeaderItem(21, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setVerticalHeaderItem(22, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setVerticalHeaderItem(23, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setVerticalHeaderItem(24, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setVerticalHeaderItem(25, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setVerticalHeaderItem(26, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setVerticalHeaderItem(27, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setVerticalHeaderItem(28, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setVerticalHeaderItem(29, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(1, item)
        self.tableWidget.itemChanged.connect(self.setTargetPlotData)
        self.gridLayout.addWidget(self.tableWidget, 3, 0, 1, 1)
        self.pushButton_2 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_2.setObjectName("pushButton_2")
        self.gridLayout.addWidget(self.pushButton_2, 4, 0, 1, 1)
        
        
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.start_btn = QtWidgets.QPushButton(self.centralwidget)
        self.start_btn.setObjectName("start_btn")
        self.horizontalLayout_2.addWidget(self.start_btn)
        self.stop_btn = QtWidgets.QPushButton(self.centralwidget)
        self.stop_btn.setObjectName("stop_btn")
        self.horizontalLayout_2.addWidget(self.stop_btn)
        self.gridLayout.addLayout(self.horizontalLayout_2, 4, 1, 1, 1)
        self.label_7 = QtWidgets.QLabel(self.centralwidget)
        self.label_7.setObjectName("label_7")
        self.gridLayout.addWidget(self.label_7, 0, 0, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1126, 26))
        self.menubar.setObjectName("menubar")
        self.menuFile = QtWidgets.QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        self.menu = QtWidgets.QMenu(self.menubar)
        self.menu.setObjectName("menu")
        self.menu_2 = QtWidgets.QMenu(self.menu)
        self.menu_2.setObjectName("menu_2")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.save_as_file = QtWidgets.QAction(MainWindow)
        self.save_as_file.setObjectName("save_as_file")
        self.free_track = QtWidgets.QAction(MainWindow)
        self.free_track.setObjectName("free_track")
        self.base_model = QtWidgets.QAction(MainWindow)
        self.base_model.setObjectName("base_model")
        self.powered_model = QtWidgets.QAction(MainWindow)
        self.powered_model.setObjectName("powered_model")
        self.production_model = QtWidgets.QAction(MainWindow)
        self.production_model.setObjectName("production_model")
        self.load_file = QtWidgets.QAction(MainWindow)
        self.load_file.setObjectName("load_file")
        self.menuFile.addAction(self.save_as_file)
        self.menuFile.addAction(self.load_file)
        self.menuFile.addAction(self.free_track)
        self.menu_2.addAction(self.base_model)
        self.menu_2.addSeparator()
        self.menu_2.addAction(self.powered_model)
        self.menu_2.addAction(self.production_model)
        self.menu.addAction(self.menu_2.menuAction())
        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menu.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        
        
        
        
    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        self.k1_input.setMaximum(10000)
        self.k2_input.setMaximum(10000)
        self.k3_input.setMaximum(10000)
        self.k4_input.setMaximum(10000)
        self.k5_input.setMaximum(10000)
        
        global pidModule
        self.k1_input.setValue(pidModule.k1)
        self.k2_input.setValue(pidModule.k2)
        self.k3_input.setValue(pidModule.k3)
        self.k4_input.setValue(pidModule.k4)
        self.k5_input.setValue(pidModule.k5)
        
        
        
        
        
        self.pushButton_2.setText(_translate("MainWindow", "Добавить"))
        item = self.tableWidget.verticalHeaderItem(0)
        item.setText(_translate("MainWindow", "1"))
        item = self.tableWidget.verticalHeaderItem(1)
        item.setText(_translate("MainWindow", "2"))
        item = self.tableWidget.verticalHeaderItem(2)
        item.setText(_translate("MainWindow", "3"))
        item = self.tableWidget.verticalHeaderItem(3)
        item.setText(_translate("MainWindow", "4"))
        item = self.tableWidget.verticalHeaderItem(4)
        item.setText(_translate("MainWindow", "5"))
        item = self.tableWidget.verticalHeaderItem(5)
        item.setText(_translate("MainWindow", "6"))
        item = self.tableWidget.verticalHeaderItem(6)
        item.setText(_translate("MainWindow", "7"))
        item = self.tableWidget.verticalHeaderItem(7)
        item.setText(_translate("MainWindow", "8"))
        item = self.tableWidget.verticalHeaderItem(8)
        item.setText(_translate("MainWindow", "9"))
        item = self.tableWidget.verticalHeaderItem(9)
        item.setText(_translate("MainWindow", "10"))
        item = self.tableWidget.verticalHeaderItem(10)
        item.setText(_translate("MainWindow", "11"))
        item = self.tableWidget.verticalHeaderItem(11)
        item.setText(_translate("MainWindow", "12"))
        item = self.tableWidget.verticalHeaderItem(12)
        item.setText(_translate("MainWindow", "13"))
        item = self.tableWidget.verticalHeaderItem(13)
        item.setText(_translate("MainWindow", "14"))
        item = self.tableWidget.verticalHeaderItem(14)
        item.setText(_translate("MainWindow", "15"))
        item = self.tableWidget.verticalHeaderItem(15)
        item.setText(_translate("MainWindow", "16"))
        item = self.tableWidget.verticalHeaderItem(16)
        item.setText(_translate("MainWindow", "17"))
        item = self.tableWidget.verticalHeaderItem(17)
        item.setText(_translate("MainWindow", "18"))
        item = self.tableWidget.verticalHeaderItem(18)
        item.setText(_translate("MainWindow", "19"))
        item = self.tableWidget.verticalHeaderItem(19)
        item.setText(_translate("MainWindow", "20"))
        item = self.tableWidget.verticalHeaderItem(20)
        item.setText(_translate("MainWindow", "21"))
        item = self.tableWidget.verticalHeaderItem(21)
        item.setText(_translate("MainWindow", "22"))
        item = self.tableWidget.verticalHeaderItem(22)
        item.setText(_translate("MainWindow", "23"))
        item = self.tableWidget.verticalHeaderItem(23)
        item.setText(_translate("MainWindow", "24"))
        item = self.tableWidget.verticalHeaderItem(24)
        item.setText(_translate("MainWindow", "25"))
        item = self.tableWidget.verticalHeaderItem(25)
        item.setText(_translate("MainWindow", "26"))
        item = self.tableWidget.verticalHeaderItem(26)
        item.setText(_translate("MainWindow", "27"))
        item = self.tableWidget.verticalHeaderItem(27)
        item.setText(_translate("MainWindow", "28"))
        item = self.tableWidget.verticalHeaderItem(28)
        item.setText(_translate("MainWindow", "29"))
        item = self.tableWidget.verticalHeaderItem(29)
        item.setText(_translate("MainWindow", "30"))
        item = self.tableWidget.horizontalHeaderItem(0)
        item.setText(_translate("MainWindow", "Время"))
        item = self.tableWidget.horizontalHeaderItem(1)
        
        
        
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.label_6.setText(_translate("MainWindow", "Текущая модель:"))
        self.cur_model_layout.setText(_translate("MainWindow", "Степенная"))
        self.label.setText(_translate("MainWindow", "K_1"))
        self.label_2.setText(_translate("MainWindow", "K_2"))
        self.label_3.setText(_translate("MainWindow", "K_3"))
        self.label_4.setText(_translate("MainWindow", "K_4"))
        self.label_5.setText(_translate("MainWindow", "K_5"))
        self.pushButton.setText(_translate("MainWindow", "Применить"))
        self.start_btn.setText(_translate("MainWindow", "Продолжить"))
        self.stop_btn.setText(_translate("MainWindow", "Остановить"))
        self.label_7.setText(_translate("MainWindow", "Протокол"))
        self.menuFile.setTitle(_translate("MainWindow", "Испытание"))
        self.menu.setTitle(_translate("MainWindow", "Настройки"))
        self.menu_2.setTitle(_translate("MainWindow", "Выбрать модель ПИД"))
        self.save_as_file.setText(_translate("MainWindow", "Сохранить трек"))
        self.free_track.setText(_translate("MainWindow", "Отчистить"))
        self.free_track.triggered.connect(self.dropData)
        self.base_model.setText(_translate("MainWindow", "Базовая"))
        self.base_model.triggered.connect(lambda : self.setCurrentModel(self.base_model.text()))
        self.powered_model.setText(_translate("MainWindow", "Степенная"))
        self.powered_model.triggered.connect(lambda : self.setCurrentModel(self.powered_model.text()))
        self.production_model.setText(_translate("MainWindow", "Промышленная"))
        self.production_model.triggered.connect(lambda : self.setCurrentModel(self.production_model.text()))
        self.load_file.setText(_translate("MainWindow", "Загрузить трек"))
        
        self.start_btn.pressed.connect(self.startTest)
        self.stop_btn.pressed.connect(controlThread.pause)
    
    def startTest(self):
        global controlThread
        self.startTime = time() # не работает пауза
        controlThread.start()
    
    def dropData(self):
        self.plotData = [[], []] 
        self.realPlotData = [[], []]
        self.inProgress = False
        self.clearTable()
        
    def clearTable(self):
        model = self.tableWidget.model()
        itemsId = [model.index(r, c) for r in range(model.rowCount()) for c in range(model.columnCount())]
        for iId in itemsId:
            model.setData(iId, None)
        
        
            
      
    def setCurrentModel(self, value):
        self.cur_model_layout.setText(value)
        self.curModelName = value
        
    def setK_1(self, value):
        self.K_1 = value
        print('K_1', self.K_1)
        
    def setK_2(self, value):
        self.K_2 = value
        print('K_2', self.K_2)
        
    def setK_3(self, value):
        self.K_3 = value
        print('K_3', self.K_3)
        
    def setK_4(self, value):
        self.K_4 = value
        print('K_4', self.K_4)
        
    def setK_5(self, value):
        self.K_5 = value
        print('K_5', self.K_5)
        
    def append(self):
        self.plotData[0].append(self.plotData[0][-1] + 1)
        self.plotData[1].append(randint(0,100)/10)
        
        self.plotData[0] = self.plotData[0][-100:]
        self.plotData[1] = self.plotData[1][-100:]
        
    def setTargetPlotData(self):
        model = self.tableWidget.model()
        tableData = []
        needSetNull = False
        for rowId in range(model.rowCount()):
            rowData = []
            for colId in range(model.columnCount()):
                itemId = model.index(rowId, colId)
                if not needSetNull:
                    
                    data = model.data(itemId)
                    try:
                        data = int(data)
                        prevX = tableData[-1][0] if len(tableData) > 0 else -1
                        if data == None or (colId == 0 and prevX >= data) or (colId == 1 and data < 25):
                            model.setData(itemId, None)
                            needSetNull = True
                        else:
                            rowData.append(data)
                    except:
                        model.setData(itemId, None)
                        needSetNull = True
                else:
                    model.setData(itemId, None)
            if not needSetNull:
                tableData.append(rowData)

        
        self.plotData[0] = [row[0] for row in tableData]
        self.plotData[1] = [row[1] for row in tableData]
        return tableData
                