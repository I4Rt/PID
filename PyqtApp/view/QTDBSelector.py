# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'QTDBSelector.ui'
#
# Created by: PyQt5 UI code generator 5.15.9
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets
from data.Experiment import *

class QTDBSelector(object):
    def __init__(self, experiments=[]):
        
        self.experiments = experiments
        self.selected = None
        
        self.experimentsView = []
        
    def setupUi(self, Dialog:QtWidgets.QDialog):
        self.dialog = Dialog
        Dialog.setObjectName("Dialog")
        Dialog.resize(704, 281)
        self.centralwidget = QtWidgets.QWidget(Dialog)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")
        self.scrollArea = QtWidgets.QScrollArea(self.centralwidget)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName("scrollArea")
        self.scrollAreaWidgetContents = QtWidgets.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 399, 103))
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayout.setObjectName("verticalLayout")
        
        
        i = 0
        for exp in self.experiments:
            i += 1
            rowLayout = QtWidgets.QHBoxLayout()
            rowLayout.setObjectName(f'rowLayout_{i}')
            
            Radio = QtWidgets.QRadioButton(self.scrollAreaWidgetContents)
            Radio.setObjectName(f'Radio_{i}')
            Radio.clicked.connect(self.selectExperiment)
            rowLayout.addWidget(Radio)
            
            
            line = QtWidgets.QFrame()
            line.setFrameShape(QtWidgets.QFrame.VLine)
            line.setFrameShadow(QtWidgets.QFrame.Sunken)
            line.setObjectName(f'Line_{i}')
            rowLayout.addWidget(line)
            
            DateTime = QtWidgets.QLabel()
            DateTime.setObjectName(f'DateTime_{i}')
            rowLayout.addWidget(DateTime)
            self.verticalLayout.addLayout(rowLayout)
            print(f'here {i}')
            self.experimentsView.append([Radio, DateTime])
            
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.gridLayout.addWidget(self.scrollArea, 0, 0, 1, 1)
        
        self.widget_2 = QtWidgets.QWidget(self.centralwidget)
        self.widget_2.setObjectName("widget_2")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.widget_2)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem1)
        self.acceptBtn = QtWidgets.QPushButton(self.widget_2)
        self.acceptBtn.setObjectName("acceptBtn")
        self.horizontalLayout_2.addWidget(self.acceptBtn)
        self.rejectBtn = QtWidgets.QPushButton(self.widget_2)
        self.rejectBtn.setObjectName("rejectBtn")
        self.horizontalLayout_2.addWidget(self.rejectBtn)
        self.gridLayout.addWidget(self.widget_2, 1, 0, 1, 1)
        
        layout = QtWidgets.QHBoxLayout(self.centralwidget)
        self.centralwidget.setMinimumHeight(280)
        self.centralwidget.setMinimumWidth(704)
        Dialog.setLayout(layout)

        self.retranslateUi(Dialog)
        
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Загрузить"))
        
        for i in range(len(self.experimentsView)):
            expView = self.experimentsView[i]
            exp = self.experiments[i]
            print(expView[0])
            expView[0].setText(_translate(str(i), f'{exp.name}'))
            expView[1].setText(_translate(str(i), f'{exp.beginingTime}'))
            
            
        self.acceptBtn.setText(_translate("Dialog", "Загрузить"))
        self.acceptBtn.setDisabled(True)
        self.rejectBtn.setText(_translate("Dialog", "Отмена"))
        self.acceptBtn.clicked.connect(lambda:self.accept()) # type: ignore
        self.rejectBtn.clicked.connect(lambda:self.reject()) # type: ignore
        
    def selectExperiment(self):
        self.acceptBtn.setDisabled(False)

    def accept(self):
        i = 0
        for btn, text in self.experimentsView:
            if btn.isChecked():
                self.selected = self.experiments[i].id
                print(self.selected)
                break
            i += 1
        self.dialog.close()
        
    def reject(self):
        self.dialog.close()
        
        
"""

def setupUi(self, Dialog):
        Dialog.setObjectName("MainWindow")
        Dialog.resize(423, 162)
        self.centralwidget = QtWidgets.QWidget(Dialog)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")
        self.scrollArea = QtWidgets.QScrollArea(self.centralwidget)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName("scrollArea")
        self.scrollAreaWidgetContents = QtWidgets.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 399, 103))
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayout.setObjectName("verticalLayout")
        
        
        i = 0
        for exp in self.experiments:
            i += 1
            rowLayout = QtWidgets.QHBoxLayout()
            rowLayout.setObjectName(f'rowLayout_{i}')
            
            Radio = QtWidgets.QRadioButton(self.scrollAreaWidgetContents)
            Radio.setObjectName(f'Radio_{i}')
            rowLayout.addWidget(Radio)
            
            line = QtWidgets.QFrame()
            line.setFrameShape(QtWidgets.QFrame.VLine)
            line.setFrameShadow(QtWidgets.QFrame.Sunken)
            line.setObjectName(f'Line_{i}')
            rowLayout.addWidget(line)
            
            DateTime = QtWidgets.QLabel()
            DateTime.setObjectName(f'DateTime_{i}')
            rowLayout.addWidget(DateTime)
            self.verticalLayout.addLayout(rowLayout)
            print(f'here {i}')
            self.experimentsView.append([Radio, DateTime])
            
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.verticalLayout.addWidget(self.scrollArea)
        self.gridLayout.addLayout(self.verticalLayout, 0, 0, 1, 1)


        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.gridLayout.addWidget(self.scrollArea, 0, 0, 1, 1)
        self.buttonBox = QtWidgets.QDialogButtonBox(self.centralwidget)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.gridLayout.addWidget(self.buttonBox, 1, 0, 1, 1)
        Dialog.setCentralWidget(self.centralwidget)
        
        self.buttonBox.accepted.connect(self.accept) # type: ignore
        self.buttonBox.rejected.connect(self.reject) # type: ignore
        
        # self.retranslateUi(MainWindow)
        
        QtCore.QMetaObject.connectSlotsByName(Dialog)

"""