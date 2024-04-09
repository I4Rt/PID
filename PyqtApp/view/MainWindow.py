from __future__ import annotations

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QTimer, QAbstractTableModel
from PyQt5.QtWidgets import QFileDialog

from view.TabsViewPlain import *
from model.ViewState import ViewState

from data.FSRealDataMeasurement import *
from data.SSRealDataMeasurement import *
from data.AmperageDataMeasurement import *
from data.VoltageDataMeasurement import *
from data.ThermocoupleData import *

from model.Apparats import *
from model.ConnectionHolder import ConnectionHolder
import winsound

import pandas as pd 

class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    
    def __init__(self,ser:serial.Serial, *args, **kwargs):
        Ui_MainWindow.__init__(self, *args, **kwargs)
        QtWidgets.QMainWindow.__init__(self, *args, *kwargs)
        # self.setFixedSize(1440, 880)
        
        self.comHolder = []
        self.state = ViewState.getState()
        self.state.experiment = Experiment('') # fucked
        self.setupUi(self)
        self.__initButtons()
        self.setFirstPosition()
        
        self.plotUpdater =  self.__DinamicalViewControll(self)
        self.plotUpdater.startUpdate()
    
    
    def setFirstPosition(self):
        self.tabWidget.setTabEnabled(1, False)
        self.tabWidget.setTabEnabled(2, False)
        self.deleteExpButton.setEnabled(False)
        self.copyExpButton.setEnabled(False)
    
    def setSecondPosition(self):
        self.tabWidget.setTabEnabled(1, True)
        self.tabWidget.setTabEnabled(2, True)
        self.deleteExpButton.setEnabled(True)
        self.copyExpButton.setEnabled(True)
    
    def __initButtons(self):
        self.expName.textEdited.connect(self.setExperimentName)
        self.plainTextEdit.textChanged.connect(self.setExperimentDescription)
        self.saveExpButton.clicked.connect(self.saveExperiment)
        self.dropExpButton.clicked.connect(self.newExperiment)
        self.copyExpButton.clicked.connect(self.copyExperiment)
        self.deleteExpButton.clicked.connect(self.dropExperiment)
        
        self.load_file.triggered.connect(self.loadExperiment)
        self.loadExpButton.clicked.connect(self.loadExperiment)
        self.excelExportButton.clicked.connect(self.export)
        self.tableWidget.itemChanged.connect(self.updateDataFromTable)
        
        
        # control PID buttons
        self.start_btn.clicked.connect(self.playFirstPID)
        self.stop_btn.clicked.connect(self.pauseFirstPID)
        self.startTest.clicked.connect(self.playSecondPID)
        self.stopTest.clicked.connect(self.pauseSecondPID)
        
        #comments
        self.submitComment.clicked.connect(self.addComment)
        self.free_real_track.triggered.connect(self.dropExperimentData)
        self.free_real_track_btn.clicked.connect(self.dropExperimentData)
        self.backfillRecordButton.clicked.connect(self.recordBackflill)
        self.pushButton_4.clicked.connect(lambda: self.textEdit.setText(''))
        #motors
        self.doubleSpinBoxSmash.valueChanged.connect(self.setSmashSpeed)
        self.smashSwitch.clicked.connect(self.toggleNeedShuffle)
        self.setTargetDeep.clicked.connect(self.setDeepth)
        self.baseSearch.clicked.connect(self.goHome)
        self.zeroSearch.clicked.connect(self.zeroSearchFunc)
        self.stopMotorBtn.clicked.connect(self.stopMotors)
        
        #alram
        self.muteButton.clicked.connect(self.togleMute)        
           
        
        # power suply control
        self.setPowerButton.clicked.connect(self.togglePower)
        self.amperageDoubleSpinBox.valueChanged.connect(self.changeTargetAmperage)
      
    def __setExpId(self, id):
        if id:
            self.label_10.setText("0" * (5-len(str(self.state.experiment.id))) + str(self.state.experiment.id))
        else:
            self.label_10.setText("XXXXX")
    
    def __setExperimentDataToView(self):
        self.__setExpId(self.state.experiment.id)
        self.expName.setText(self.state.experiment.name)
        self.plainTextEdit.setPlainText(self.state.experiment.description)
        #TODO: Set Table Data
          
    def showMessage(self, title:str, message:str):
        msg = QtWidgets.QMessageBox()
        msg.setWindowTitle(title)
        msg.setText(message)
        msg.exec_()
          
    def showPermit(self, title, question):
        result = QtWidgets.QMessageBox.question(self, title, question, 
           QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No, 
           QtWidgets.QMessageBox.No)
        if result == QtWidgets.QMessageBox.Yes:
            return True
        else:
            return False
        
    def resetExperimentBooleans(self, expIsNew=True):
        self.state.plot1Pause=True
        self.state.plot2Pause=True
        if expIsNew:
            self.state.plot1Stopped=False
        else:
            self.state.plot1Stopped=True
        self.state.plot2Stopped=False
        self.state.firstPID1Run = True
        self.state.firstPID2Run = True
        
    #status updater
    def updateTemperatureKoef(self):
        self.temp_ind_input.setValue(self.state.tempDelta)
    
    def updatePowerDisable(self):
        if self.state.needSearchZero:
            self.amperageDoubleSpinBox.setDisabled(True)
            self.setPowerButton.setDisabled(True)
        else:
            self.amperageDoubleSpinBox.setDisabled(False)
            self.setPowerButton.setDisabled(False)
    
    
    def updateHeaterStatusUI(self):
        print('heater status error is', self.state.heaterError)
        if self.state.heaterError:
            self.heat_status.setText('Ошибка')
            return    
        self.heat_status.setText('Норма')
        
    def updatePowerSupplyStatusUI(self):
        if self.state.powerError:
            self.power_status.setText('Ошибка')
            return    
        self.power_status.setText('Норма')
        
    def updateThermocouple1StatusUI(self):
        if self.state.thermocouple1Error:
            self.temperature1_status.setText('Ошибка')
            return    
        self.temperature1_status.setText('Норма')
        
    def updateThermocouple2StatusUI(self):
        if self.state.thermocouple2Error:
            self.temperature2_status.setText('Ошибка')
            return    
        self.temperature2_status.setText('Норма')
    
    def updateMotor1StatusUI(self):
        if self.state.motor1Error:
            self.motor1_status.setText('Ошибка')
            return    
        self.motor1_status.setText('Норма')
    
    def updateMotor2StatusUI(self):
        if self.state.motor2Error:
            self.motor2_status.setText('Ошибка')
            return    
        self.motor2_status.setText('Норма')
    
    def updateComNameUI(self):
        name = ConnectionHolder.getComName()
        if name:
            self.current_com.setText(name)
            return
        self.current_com.setText("Не выбран")
        
    def updateRealPowerUI(self):
        self.realPower_1.setText(str(round(self.state.curPower,1)))
        self.realPower_2.setText(str(round(self.state.curPower,1)))
            
    def updateAvaliablePorts(self):
        self.comHolder.clear()
        for action in self.menu_COM.actions():
            self.menu_COM.removeAction(action)
        i = 0
        for avaliablePort in ConnectionHolder.getAvaliableComs():
            self.comHolder.append(QtWidgets.QAction())
            self.comHolder[i].setText(f'{avaliablePort[0]} | {avaliablePort[1]}')
            self.comHolder[i].name = avaliablePort[0]
            self.menu_COM.addAction(self.comHolder[i])
            i += 1
        for button in self.comHolder:
            button.triggered.connect(lambda _, b=button: ConnectionHolder.changePort(b.name))
            
    def updateTextCommentsRecords(self):
        if self.state.experiment.id:
            res = self.state.experiment.getFillingRecords(10)
            self.textBrowser.setText('')
            fillings=[]
            for row in res:
                row_str = 'ПОДСЫПКА: '
                for cur_index in range(len(row[1])):
                    row_str += f'{row[1][cur_index]} {row[2][cur_index]} '
                fillings.append([row[0]/60, row_str])
                
            comments=[]
            res = self.state.experiment.getComments()
            for com in res:
                self.subplot2.axvline(x=com.time/60, color='skyblue')
                comments.append([round(com.time/60,1), com.text])
               
            res = fillings + comments
            res.sort(key=lambda x: x[0])
            
            for row in res:    
                self.textBrowser.append(f'<p><b>{round(row[0], 1)}</b><span>: {row[1]}</span></p>')
                
        
        
    
    # buttons actions
    def addComment(self):
        if self.textEdit.toPlainText() != '':
            text = self.textEdit.toPlainText()
            time = self.state.lastSSTime
            if self.state.plot2Pause:
                self.showMessage('Недопустимое действие', 'Эксперимент не начался')
            else:
                if self.state.lastSSTime is None:
                    self.showMessage('Недопустимое действие', 'Подождите первой записи данных и повторите попытку')
                else:
                    self.state.experiment.addComment(text, time)
                    self.textBrowser.append(f'<p><b>{round(time/60, 1)}</b><span>: {text}</span></p>')
                    self.subplot2.axvline(x=time/60, color='skyblue')
                    self.textEdit.setPlainText('')
                    self.showMessage('Уведомление', 'Сохранено')
        else:
            self.showMessage('Недопустимое действие', 'Пустое поле текста комментария')
    
    def recordBackflill(self):
        if self.state.plot2Pause:
            self.showMessage('Недопустимое действие', 'Эксперимент не начался')
        else:
            if self.state.lastSSTime is None:
                self.showMessage('Недопустимое действие', 'Подождите первой записи данных и повторите попытку')
            else:
                backfillings = {}
                if self.inputBackfills_elem_1.text() != '':
                    backfillings[self.inputBackfills_elem_1.text()]=self.inputBackfills_elem_value_1.value()
                if self.inputBackfills_elem_2.text() != '':
                    backfillings[self.inputBackfills_elem_2.text()]=self.inputBackfills_elem_value_2.value()
                if self.inputBackfills_elem_3.text() != '':
                    backfillings[self.inputBackfills_elem_3.text()]=self.inputBackfills_elem_value_3.value()
                if self.inputBackfills_elem_4.text() != '':
                    backfillings[self.inputBackfills_elem_4.text()]=self.inputBackfills_elem_value_4.value()
                if self.inputBackfills_elem_5.text() != '':
                    backfillings[self.inputBackfills_elem_5.text()]=self.inputBackfills_elem_value_5.value()
                
                res_str = ''
                for pair in backfillings.items():
                    res_str += str(pair[0]) + ' ' + str(pair[1]) + ' '
                    self.state.experiment.addFilling(pair[0], pair[1], self.state.lastSSTime)
                    
                self.textBrowser.append(f'<p><b>{round(self.state.lastSSTime/60, 1)}</b><span>: ПОДСЫПКА: {res_str}</span></p>')
                self.showMessage('Уведомление', 'Сохранено')
    
    def playFirstPID(self):
        if self.state.firstPID1Run:
            if len(self.state.experiment.fsRealData) != 0:
                check1Passed = self.showPermit('Предупреждение', 'В подготовительном этапе эксперимента присутствуют данные, вы хотите продолжить его? (данные основного этапа будут удалены)')
                if check1Passed:
                    self.state.experiment.dropSSRealData()
                    self.state.experiment.dropComments()
                    self.state.experiment.save()
                    
                    self.state.plot1Stopped = False
                    self.state.firstPID1Run = False
                    
                    
                    difTime = self.state.experiment.getData(FSRealDataMeasurement)[-1].time
                    print(f'dif time: {difTime}\n\n\n\n\n\n')
                    self.state.playTime1 = time()
                    self.state.pausePlot1()
                    self.state.pauseDuration1 -= difTime
                    print(f'set start time to {self.state.playTime1}')
                    
                else:
                    return
        if not self.state.plot1Stopped:
            self.state.playPlot1()
            self.state.plot1Pause = False
            return
        self.showMessage('Недопустимое действие', 'Подготовительный этап уже окончен')
    
    
    def togleMute(self):
        if not self.state.mute:
            self.muteButton.setText('Включить')
            self.state.mute = True
        else:
            self.muteButton.setText('Выключить')
            self.state.mute = False
            
    
    
    def pauseFirstPID(self):
        if not self.state.plot1Stopped:
            self.state.pausePlot1()
            self.state.plot1Pause = True
            return
        self.showMessage('Недопустимое действие', 'Подготовительный этап уже окончен')
        
    def stopFirstPID(self):
        if not self.state.plot1Stopped:
            self.state.pausePlot1()
            self.state.plot1Pause = True
            self.state.plot1Stopped = True
            return
        self.showMessage('Недопустимое действие', 'Подготовительный этап уже окончен')
        
    def playSecondPID(self):
        
        if self.state.firstPID2Run:
            if len(self.state.experiment.ssRealData) != 0:
                check1Passed = self.showPermit('Предупреждение', 'В основном этапе эксперимента присутствуют данные, вы хотите продолжить его?')
                if check1Passed:
                    self.state.firstPID1Run = False
                    self.state.firstPID2Run = False
                    self.state.plot1Stopped = True
                    self.state.plot2Stopped = False
                    
                    difTime = self.state.experiment.getData(SSRealDataMeasurement)[-1].time
                    print(f'dif time: {difTime}\n\n\n\n\n\n')
                    self.state.playTime2 = time()
                    self.state.pausePlot2()
                    self.state.pauseDuration2 -= difTime
                    print(f'set start time to {self.state.playTime2}')
                else:
                    return
                
        check2Passed = True
        if not self.state.plot1Stopped:
            check2Passed = self.showPermit('Предупреждение', 'Подготовительный этап еще не окончен, вы уверены что хотите запустить испытание? (вы не сможете вернуться)')
        if check2Passed:
            self.state.plot1Pause = True
            self.state.plot1Stopped = True
            if not self.state.plot2Stopped:
                self.state.firstPID1Run = True
                self.state.playPlot2()
                self.state.plot2Pause = False
                self.state.plot1Pause = True #fucked
                self.state.plot1Stopped = True #fucked
                return
            self.showMessage('Недопустимое действие', 'Эксперимент уже окончен')
        
    def pauseSecondPID(self):
        check1Passed = True
        if not self.state.plot1Stopped:
            check1Passed = self.showPermit('Предупреждение', 'Подготовительный этап еще не окончен, вы уверены что хотите запустить испытание? (вы не сможете вернуться)')
        if check1Passed:
            self.state.plot1Pause = True
            self.state.plot1Stopped = True
            if not self.state.plot2Stopped:
                self.state.pausePlot2()
                self.state.plot2Pause = True
                return
            self.showMessage('Недопустимое действие', 'Эксперимент уже окончен')
            
    def stopSecondPID(self):
        check1Passed = True
        if not self.state.plot1Stopped:
            check1Passed = self.showPermit('Предупреждение', 'Подготовительный этап еще не окончен, вы уверены что хотите запустить испытание? (вы не сможете вернуться)')
        if check1Passed:
            self.state.plot1Pause = True
            self.state.plot1Stopped = True
            if not self.state.plot2Stopped:
                self.state.pausePlot2()
                self.state.plot2Pause = True
                self.state.plot2Stopped = True
                return
            self.showMessage('Недопустимое действие', 'Эксперимент уже окончен')
    
    def setExperimentName(self):
        newName = self.expName.text()
        self.state.experiment.name=newName
        print(self.state.experiment.name)
    
    def setExperimentDescription(self):
        newDescription = self.plainTextEdit.toPlainText()
        self.state.experiment.description=newDescription
        print(self.state.experiment.description)
    
    def dropExperimentData(self):
        if self.state.experiment.id:
            if len(self.state.experiment.fsRealData)!=0 or len(self.state.experiment.ssRealData)!=0:
                res = self.showPermit('Предупреждение', 'Вы уверены, что хотите\n удалить данные? (обоих этапов)')
                if not res:
                    return
            self.state.experiment.dropFSRealData()
            self.state.experiment.dropSSRealData()
            self.state.experiment.dropAmperageData()
            self.state.experiment.dropThermocoupleData()
            self.state.experiment.dropVoltageData()
            self.state.experiment.dropComments()
            self.state.experiment.dropFillings()
            
            
            self.subplot.cla()
            self.subplot.grid()
            self.subplot2.cla()
            self.subplot2.grid()
            
            self.resetExperimentBooleans(True)#(False)
            self.__setExperimentDataToView()
            self.setTargetDataFromExperiment()
            self.setSecondPosition()
            
            self.textEdit.setPlainText('')
            self.textBrowser.setText('')
            
            self.updateTextCommentsRecords()
                
            self.state.dropPlotTimes()
            #drop pid data
            self.state.pidModule.prev_temperatures = []
            self.state.pidModule.prev_time = None
            self.state.pidModule.prev_power = 0
            self.state.pidModuleIndustrial.d_T_prev = None
            self.state.pidModuleIndustrial.prev_time = None
            self.state.pidModuleIndustrial.prev_power = None
        else:
            self.showMessage('Недопустимое действие', 'Не выбран эксперимент')
            
    def saveExperiment(self):
        try:
            if self.expName.text() != '':
                self.state.experiment.save()
                self.__setExpId(self.state.experiment.id)
                self.setSecondPosition()
                self.resetExperimentBooleans(True)
            else:
                self.__setExperimentDataToView()
                raise Exception('Введите название эксперимента')
        except Exception as e:
            self.showMessage('Ошибка', str(e))
            
    def dropExperiment(self):
        res = self.showPermit('Предупреждение','Вы действительно хотите \nудалить эксперимент?')
        if res:
            self.resetExperimentBooleans(True)
            self.state.experiment.delete()
            self.state.experiment = Experiment('')
            self.__setExperimentDataToView()
            self.resetExperimentBooleans(True)
            self.setFirstPosition()
            #drop pid data
            self.state.pidModule.prev_temperatures = []
            self.state.pidModule.prev_time = None
            self.state.pidModule.prev_power = 0
            self.state.pidModuleIndustrial.d_T_prev = None
            self.state.pidModuleIndustrial.prev_time = None
            self.state.pidModuleIndustrial.prev_power = None
        
    def newExperiment(self):
        self.resetExperimentBooleans(True)
        self.state.experiment = Experiment('')
        self.__setExperimentDataToView()
        self.resetExperimentBooleans(True)
        self.setFirstPosition()
        #drop pid data
        self.state.pidModule.prev_temperatures = []
        self.state.pidModule.prev_time = None
        self.state.pidModule.prev_power = 0
        self.state.pidModuleIndustrial.d_T_prev = None
        self.state.pidModuleIndustrial.prev_time = None
        self.state.pidModuleIndustrial.prev_power = None
        
    def copyExperiment(self):
        i = 1
        while i <= 100:
            try:
                tempExp = Experiment(self.state.experiment.name + f' - копия{i}', self.state.experiment.description, fsTargetData=self.state.experiment.fsTargetData)
                tempExp.save()
                break
            except Exception:
                i += 1
            
        self.state.experiment = tempExp
        
        self.subplot.cla()
        self.subplot.grid()
        self.subplot2.cla()
        self.subplot2.grid()
        
        self.resetExperimentBooleans(True)#(False)
        self.__setExperimentDataToView()
        self.setTargetDataFromExperiment()
        self.setSecondPosition()
        
        self.textEdit.setPlainText('')
        self.textBrowser.setText('')
        
        self.updateTextCommentsRecords()
            
        self.state.dropPlotTimes()
        if len(self.state.experiment.fsRealData):
            self.state.plot1Stopped = True
            
        self.state.realVolrage = None
        vm = self.state.experiment.getData(VoltageDataMeasurement, True)
        if vm:
            self.state.realVolrage = vm.value
            
        self.state.realAmperage = None
        am = self.state.experiment.getData(AmperageDataMeasurement, True)
        if am:
            self.state.realAmperage = am.value
            
        self.state.realTemperature_1 = None
        t1 = self.state.experiment.getData(FSRealDataMeasurement, True)
        if t1:
            self.state.realTemperature_1 = t1.value
            
        self.state.realTemperature_2 = None
        t2 = self.state.experiment.getData(SSRealDataMeasurement, True)
        if t2:
            self.state.realTemperature_2 = t2.value
            
        self.state.realThermocouple = None
        tc = self.state.experiment.getData(ThermocoupleData, True)
        if tc:
            self.state.realThermocouple = tc.value
     
    def loadExperiment(self):        
        
        self.sideDialog = QTDBSelector(Experiment.getAll())
        self.sideWindow = QtWidgets.QDialog()
        self.sideDialog.setupUi(self.sideWindow)
        self.sideWindow.exec()
        
        if self.sideDialog.selected:
            self.subplot.cla()
            self.subplot.grid()
            self.subplot2.cla()
            self.subplot2.grid()
            
            self.state.experiment = Experiment.getByID(self.sideDialog.selected)
            self.resetExperimentBooleans(True)#(False)
            self.__setExperimentDataToView()
            self.setTargetDataFromExperiment()
            self.setSecondPosition()
            
            self.textEdit.setPlainText('')
            self.textBrowser.setText('')
            
            self.updateTextCommentsRecords()
                
            self.state.dropPlotTimes()
            if len(self.state.experiment.fsRealData):
                self.state.plot1Stopped = True
              
            self.state.realVolrage = None
            vm = self.state.experiment.getData(VoltageDataMeasurement, True)
            if vm:
                self.state.realVolrage = vm.value
                
            self.state.realAmperage = None
            am = self.state.experiment.getData(AmperageDataMeasurement, True)
            if am:
                self.state.realAmperage = am.value
                
            self.state.realTemperature_1 = None
            t1 = self.state.experiment.getData(FSRealDataMeasurement, True)
            if t1:
                self.state.realTemperature_1 = t1.value
                
            self.state.realTemperature_2 = None
            t2 = self.state.experiment.getData(SSRealDataMeasurement, True)
            if t2:
                self.state.realTemperature_2 = t2.value
                
            self.state.realThermocouple = None
            tc = self.state.experiment.getData(ThermocoupleData, True)
            if tc:
                self.state.realThermocouple = tc.value
            
            #drop pid data
            self.state.pidModule.prev_temperatures = []
            self.state.pidModule.prev_time = None
            self.state.pidModule.prev_power = 0
            self.state.pidModuleIndustrial.d_T_prev = None
            self.state.pidModuleIndustrial.prev_time = None
            self.state.pidModuleIndustrial.prev_power = None
            
        self.sideDialog = None 
    
    def export(self):
        if self.state.experiment.id is None:
            self.showMessage('Ошибка', "Сначала сохраните эксперимент")
        else:
            fileName =  QFileDialog.getSaveFileName(self, 'Загрузить', None, "All files (*.xlsx)")[0]
            if fileName:
                try:
                    df = pd.DataFrame()
                    data = self.state.experiment.getTotalData()

                    df['time']             = list(map(lambda x: x[0], data))
                    df['temperature_values']      = list(map(lambda x: x[1], data))
                    df['thermocouple_values']      = list(map(lambda x: x[2], data))
                    df['amperage']         = list(map(lambda x: x[3], data))
                    df['real_amperage']    = list(map(lambda x: x[4], data))
                    df['voltage']          = list(map(lambda x: x[5], data))
                    df['comment']          = list(map(lambda x: x[6], data))
                    df['fillings(names)']  = list(map(lambda x: x[7], data))
                    df['fillings(values)'] = list(map(lambda x: x[8], data))
                    
                    # Converting to excel 
                    
                    writer = pd.ExcelWriter(fileName, engine="xlsxwriter")
                    df.to_excel(writer, startrow=3, sheet_name='Sheet1',index = False)
                    print('keys', list(writer.sheets.keys()))
                    worksheet = writer.sheets['Sheet1']
                    worksheet.write(0, 0, self.state.experiment.name)
                    worksheet.write(1, 0, self.state.experiment.description)
                    writer.close()
                    
                except Exception as e:
                    print(e)
                    self.showMessage('Ошибка', str(e))
    
            
    
    # powerSupply area button functions
    
    def togglePower(self):
        if self.state.powerError:
            self.showMessage('Ошибка', "Устрйоство недоступно")
            return
        self.state.powerIsOn = not self.state.powerIsOn
        if self.state.powerIsOn:
            self.setPowerButton.setText("Выключить")
            return
        self.setPowerButton.setText("Включить")
        
    def changeTargetAmperage(self):
        self.state.targetAmperage = self.amperageDoubleSpinBox.value()
        
    # motors area button functions
    def toggleNeedShuffle(self):
        if self.state.motor2Error:
            self.showMessage('Ошибка', "Устрйоство недоступно")
            return
        self.state.needShuffle = not self.state.needShuffle
        if self.state.needShuffle:
            self.smashSwitch.setText('Остановить')
        else:
            self.smashSwitch.setText('Начать')
            
    def setDeepth(self):
        if self.state.motor1Error:
            self.showMessage('Ошибка', "Устрйоство недоступно")
            return
        if self.state.commandMotorVerticalIsRunning:
            self.showMessage('Недопустимая команда', 'Платформа занята')
        else:
            if self.state.currentDeep is None:
                self.showMessage('Недопустимая команда', 'Неизвестное положение платформы\nОтправьте платформу на базу')
            else:
                
                newDeepth = self.targetDeepSpinBox.value()
                difference = newDeepth - self.state.currentDeep
                # print('in runner', self.state.zeroDeep, difference,'\n\n\n')
                if self.state.zeroDeep != None:
                    self.state.zeroDeep += difference
                # print('in runner after', self.state.zeroDeep,'\n\n\n')
                    
                self.state.targetDeep = newDeepth
                self.state.needMoveDistance = True
        
    def goHome(self):
        if self.state.motor1Error:
            self.showMessage('Ошибка', "Устрйоство недоступно")
            return
        if not self.showPermit('Предупреждение', "Вы дествительно хотите\nвернуть платформу на базу?"):
            return
        if self.state.commandMotorVerticalIsRunning:
            self.showMessage('Недопустимая команда', 'Платформа занята')
        else:
            self.state.needGoHome = True
            self.state.targetDeep = 0
            self.state.currentDeep = None
            self.realDeepLabel.setText('?')
            
    def setSmashSpeed(self):
        if not self.state.needShuffle:
            self.state.smashSpeed = round(self.doubleSpinBoxSmash.value(), 2)
        else:
            self.showMessage('Недопустимая команда', 'Двигатель занят. \nИзменения не вступили в силу, \nостановите вращение и повторите попытку.')
            
    def zeroSearchFunc(self):
        if self.state.motor1Error or self.state.powerError:
            self.showMessage('Ошибка', "Устрйоство недоступно")
            return
        self.state.targetAmperage = 2.
        self.state.powerIsOn = True
        
        if self.state.commandMotorVerticalIsRunning:
            self.showMessage('Недопустимая команда', 'Платформа занята')
            return
        print(self.state.currentDeep)
        if self.state.currentDeep is None:
            self.showMessage('Недопустимая команда', 'Сперва необходимо определить базу')
            return
        self.state.needSearchZero = True
        self.state.commandMotorVerticalIsRunning = True 
        
          

        
    def stopMotors(self):
        #updated to stop power supply when emergency stop clicked
        if self.state.needSearchZero:
            self.state.targetAmperage = 0.
            self.state.powerIsOn = False
            
        self.state.needSearchZero = False
        self.state.needShuffle = False
        self.state.commandMotorRotateIsRunning = False
        self.state.commandMotorRotateIsRunning = False
        motorVertical.stop(ConnectionHolder.getConnection())
        motorRotate.stop(ConnectionHolder.getConnection())
        self.smashSwitch.setText('Начать')
        self.state.currentDeep =None
        self.state.zeroDeep = None
        
        
        
            
    #TableFunctions
    def clearTable(self):
        model:QtCore.QAbstractItemModel  = self.tableWidget.model()
        itemsId = [model.index(r, c) for r in range(model.rowCount()) for c in range(model.columnCount())]
        for iId in itemsId:
            model.setData(iId, None)
    
    def updateDataFromTable(self):
        # print('update data')
        model:QtCore.QAbstractItemModel = self.tableWidget.model()
        tableData = []
        needSetNull = False
        firstSet = False
        for rowId in range(model.rowCount()):
            rowData = []
            for colId in range(model.columnCount()):
                itemId = model.index(rowId, colId)
                
                
                if not (rowId or colId):                       # проверка для выставления нуля
                    curData = model.data(itemId)
                    if curData != None and curData != '':
                        nextItemId = model.index(rowId, colId+1)
                        nextData = model.data(nextItemId)
                        if nextData == '' or nextData == None:
                            model.setData(nextItemId, self.state.indipendTemperature if self.state.indipendTemperature else 25)
                            
                if not needSetNull:
                    data = model.data(itemId)
                    try:
                        data = int(data)
                        prevX = tableData[-1][0] if len(tableData) > 0 else -1
                        if data == None or (colId == 0 and prevX >= data) or (colId == 1 and data < 25):
                            model.setData(itemId, None)
                            needSetNull = True
                        elif colId % 2 == 1 and data >=1000 :
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

        reversed = []
        for pair in tableData:
            reversed.append([pair[1], pair[0]])
        
        self.state.experiment.updateFSTargetProfile(reversed)
        # print('outside', len(self.state.experiment.fsTargetData))
    
    def setTargetDataFromExperiment(self):
        self.plotUpdater.stopUpdate()
        self.tableWidget.itemChanged.disconnect()
        # print('disconnected')
        self.doubleSpinBox.setValue(self.state.experiment.ssTarget)
        self.clearTable()
        model:QtCore.QAbstractItemModel = self.tableWidget.model()
        rowId = 0
        data = self.state.experiment.getData(FSTargetDataMeasurement)
        print(len(data))
        for targetData in data:
            ind1 = model.index(rowId, 0)
            ind2 = model.index(rowId, 1)
            model.setData(ind1, targetData.time)
            model.setData(ind2, targetData.value)
            rowId += 1
            #TODO:check row count is enough
        
        self.updateDataFromTable()
        self.tableWidget.itemChanged.connect(self.updateDataFromTable)
        print('connected again')
        self.plotUpdater.startUpdate()
    
    #alramFuncs
    def alram(self):
        if self.state.needAlram:
            self.allertIndicator.setStyleSheet("QLabel {background-color : red; border-color : black; border-width : 1px; border-style : solid; border-radius : 3px; min-height: 20px; min-width: 20px; max-height:20px}")
            
            if not self.state.mute:
                frequency = 2500  # Set Frequency To 2500 Hertz
                duration = 500  # Set Duration To 1000 ms == 1 second
                winsound.Beep(frequency, duration)
        else:
            self.allertIndicator.setStyleSheet("QLabel {background-color : gray; border-color : black; border-width : 1px; border-style : solid; border-radius : 3px; min-height: 20px; min-width: 20px; max-height:20px}")
            
    class __DinamicalViewControll():
        def __init__(self, model:MainWindow):
            self.model = model
            pass
            
        def stopUpdate(self):
            try:
                self.model.plotupdater.stop()
            except:
                pass
            
        def startUpdate(self):
                # Repeating timer, calls random_pick over and over.
                self.model.ui_target_plot_data,  = self.model.subplot.plot([],[]) 
                self.model.ui_real_plot_data, = self.model.subplot.plot([], [], linewidth=2) 
                
                self.model.secondPlotTarget = self.model.subplot2.axhline(y=self.model.state.experiment.ssTarget, color="black", linestyle="--")
                self.model.ui_real_plot2_data, = self.model.subplot2.plot([], [], color="orange", linewidth=2) 
                self.model.ui_real_thermocouple_plot2_data, = self.model.subplot2.plot([], [], color="yellow") 
        
                self.model.ui_target_amperage_plot_data, = self.model.amperateSubplot.plot([], [], color="teal")
                self.model.ui_real_amperage_plot_data, = self.model.amperateSubplot.plot([], [], color="forestgreen")
                
                self.model.ui_real_voltage_plot_data, = self.model.voltageSubplot.plot([], [], color="red") 
                self.model.subplot.set_xlabel('Время, мин')
                self.model.subplot.set_ylabel('Температура, °C')
            
                
                self.model.subplot2.set_xlabel('Время, мин')
                self.model.subplot2.set_ylabel('Температура, °C')
                self.model.subplot2.legend(('Целевая температура, °C', 'Температура, °C', 'Температура электролита, °C'), loc=2)
                
                self.model.amperateSubplot.set_ylabel('Сила тока, А')
                self.model.amperateSubplot.spines['right'].set_position(('outward', 60))
                self.model.amperateSubplot.legend(('Сила тока (целевая), А', 'Сила тока (измеренная), А'), loc=9)
                
                self.model.voltageSubplot.set_ylabel('Напряжение, В')
                self.model.voltageSubplot.legend(('Напряжение, В',))
                
                self.prevTime = time()
                self.model.updateAvaliablePorts()
                # self.model.approx_figure = self.model.subplot.fill_between(np.array([]),np.array([]),np.array([]), color='blue', alpha=0.3)
                self.model.plotupdater = QTimer()
                self.model.plotupdater.setInterval(1000)
                self.model.plotupdater.timeout.connect(self.updatePlots)
                self.model.plotupdater.start()
            
        def updatePlots(self):
            self.model.updatePowerDisable()
            self.model.updateTemperatureKoef()
            
            if time()-self.prevTime>15:
                self.model.updateAvaliablePorts()
                self.prevTime = time()
            self.model.updateComNameUI()
            self.model.updateHeaterStatusUI()
            self.model.updatePowerSupplyStatusUI()
            self.model.updateThermocouple1StatusUI()
            self.model.updateThermocouple2StatusUI()
            self.model.updateMotor1StatusUI()
            self.model.updateMotor2StatusUI()
            self.model.updateRealPowerUI()
            self.model.alram()
            
            
            
            self.setPlot1Data()
            self.setPlot2Data()
            self.updateDeepth()
            self.updateLastParams()
            self.motorControlUIUpdate()
            
            self.indipendUpdate()
            
        
        def indipendUpdate(self):
            if self.model.state.indipendTemperature is None:
                self.model.statusTemperature.setText('?')
            else:
                self.model.statusTemperature.setText(str(round(self.model.state.indipendTemperature, 2)))
                
                
            if self.model.state.currentTime is None:
                self.model.statusTime.setText('?')
            else:
                self.model.statusTime.setText(str(round(self.model.state.currentTime/60, 1)))
        
        def motorControlUIUpdate(self):
            if self.model.state.currentDeep is None:
                self.model.state.zeroDeep = None
                self.model.realDeepLabel.setText('?')
                self.model.realDeepLabelOfZero.setText('?')
                self.model.setTargetDeep.setDisabled(True)
                self.model.zeroSearch.setDisabled(True)
            else:
                self.model.setTargetDeep.setDisabled(False)
                self.model.zeroSearch.setDisabled(False)
                self.model.realDeepLabel.setText(str(self.model.state.currentDeep))

            # print('in updater', self.model.state.zeroDeep , '\n\n\n')
            if self.model.state.zeroDeep != None:
                self.model.realDeepLabelOfZero.setText(str(self.model.state.zeroDeep))
            
                
        def updateDeepth(self):
            if self.model.state.needUpdateDeepth:
                print('needUpdateDeepth')
                self.model.state.needUpdateDeepth = False
                self.model.state.currentDeep = self.model.state.targetDeep
                self.model.realDeepLabel.setText(f'{self.model.state.currentDeep}')
                
            
        def setPlot1Data(self):
            targetData = self.model.state.experiment.getData(FSTargetDataMeasurement)
            targetDataArray = [[], []]
            for index in range(len(targetData)):
                targetDataArray[0].append(targetData[index].time)
                targetDataArray[1].append(targetData[index].value)
                
            realData = self.model.state.experiment.getData(FSRealDataMeasurement)
            realDataArray = [[], []]
            for index in range(len(realData)):
                realDataArray[0].append(realData[index].time/60)
                realDataArray[1].append(realData[index].value)
                
            # self.approx_figure = self.model.subplot.fill_between(np.array(targetDataArray[0]), np.array(targetDataArray[1]) + self.model.state.spaceValue, np.array(targetDataArray[1]) - self.model.state.spaceValue, color='blue', alpha=0.3)
            try:
                self.model.approx_figure.remove()
            except:
                print('approx_figure del err')
                
            self.model.approx_figure = self.model.subplot.fill_between(np.array(targetDataArray[0]), np.array(targetDataArray[1]) + self.model.state.spaceValue, np.array(targetDataArray[1]) - self.model.state.spaceValue, color='blue', alpha=0.3)
            
            self.model.ui_target_plot_data.set_xdata(targetDataArray[0])
            self.model.ui_target_plot_data.set_ydata(targetDataArray[1])

            self.model.ui_real_plot_data.set_xdata(realDataArray[0])
            self.model.ui_real_plot_data.set_ydata(realDataArray[1])
                
            if self.model.state.needAIM:
                try:
                    self.model.subplot.set_xbound(0, targetDataArray[0][-1])
                    self.model.subplot.set_ybound(min(targetDataArray[1])-10, max(targetDataArray[1])+10)
                except Exception as e:
                    pass

            # self.graphicsView.getFigure().canvas.draw()
            self.model.graphicsView.getFigure().canvas.draw_idle()
                
        def setPlot2Data(self):
            targetAmperage = 0   
            targetVoltage = 0   
            
            
            
            
            self.model.secondPlotTarget.set_ydata(self.model.state.experiment.ssTarget)
            
            
            # self.model.secondPlotTarget = self.model.subplot2.axhline(y=self.model.state.experiment.ssTarget, color="black", linestyle="--")
            realData = self.model.state.experiment.getData(SSRealDataMeasurement)
            realDataArray = [[], []]
            for index in range(len(realData)):
                realDataArray[0].append(realData[index].time/60)
                realDataArray[1].append(realData[index].value)
                
            self.model.ui_real_plot2_data.set_xdata(realDataArray[0])
            self.model.ui_real_plot2_data.set_ydata(realDataArray[1])
            
            realData = self.model.state.experiment.getData(ThermocoupleData)
            realThermocoupleDataArray = [[], []]
            for index in range(len(realData)):
                realThermocoupleDataArray[0].append(realData[index].time/60)
                realThermocoupleDataArray[1].append(realData[index].value)
                
            self.model.ui_real_thermocouple_plot2_data.set_xdata(realThermocoupleDataArray[0])
            self.model.ui_real_thermocouple_plot2_data.set_ydata(realThermocoupleDataArray[1])
        

            realData = self.model.state.experiment.getData(AmperageDataMeasurement)
        
            targetAmperageDataArray = [[], []]
            realAmperageDataArray = [[], []]
            for index in range(len(realData)):
                targetAmperageDataArray[0].append(realData[index].time/60) # that is ok
                targetAmperageDataArray[1].append(realData[index].targetValue)
                
                realAmperageDataArray[0].append(realData[index].time/60)
                realAmperageDataArray[1].append(realData[index].value)
                targetAmperage = realData[index].value
            
            self.model.ui_target_amperage_plot_data.set_xdata(targetAmperageDataArray[0])
            self.model.ui_target_amperage_plot_data.set_ydata(targetAmperageDataArray[1])
            
            self.model.ui_real_amperage_plot_data.set_xdata(realAmperageDataArray[0])
            self.model.ui_real_amperage_plot_data.set_ydata(realAmperageDataArray[1])
            
            realData = self.model.state.experiment.getData(VoltageDataMeasurement)
            realVoltageDataArray = [[], []]
            for index in range(len(realData)):
                realVoltageDataArray[0].append(realData[index].time/60)
                realVoltageDataArray[1].append(realData[index].value)
                targetVoltage = realData[index].value
        
            self.model.ui_real_voltage_plot_data.set_xdata(realVoltageDataArray[0])
            self.model.ui_real_voltage_plot_data.set_ydata(realVoltageDataArray[1])
            
            
            if self.model.state.needAIM:
                try:
                    self.model.subplot2.set_ybound(self.model.state.experiment.ssTarget - 50, self.model.state.experiment.ssTarget + 50)
                    self.model.subplot2.set_xbound(realDataArray[0][0], realDataArray[0][-1])
                            
                    # print('amperage', targetAmperage)
                    self.model.amperateSubplot.set_ybound(min(realAmperageDataArray[1]) - 1, max(realAmperageDataArray[1]) + 1)
                    
                    # print('voltage', targetVoltage)         
                    self.model.voltageSubplot.set_ybound(min(realVoltageDataArray[1]) - 1, max(realVoltageDataArray[1]) + 1)
                    
                except Exception as e:
                    pass
            
            
            # self.graphicsView.getFigure().canvas.draw()
            self.model.graphicsView_2.getFigure().canvas.draw_idle()
            
            
        def updateLastParams(self):
            try:
                lastT1 = self.model.state.realTemperature_1
                if not lastT1 and lastT1 != 0:
                    lastT1='?'
                
                self.model.realTemperature_1.setText(str(lastT1))
                lastT2 = self.model.state.realTemperature_2
                if not lastT2 and lastT2 != 0:
                    lastT2='?'
                self.model.realTemperature_2.setText(str(lastT2))
                lastTC = self.model.state.realThermocouple
                if not lastTC and lastTC != 0:
                    lastTC = '?'
                self.model.realThermocouple.setText(str(lastTC))
                lastA = self.model.state.realAmperage
                if not lastA and lastA != 0:
                    lastA = '?'
                self.model.realAmperage.setText(str(lastA))
                lastV = self.model.state.realVolrage
                if not lastV and lastV != 0:
                    lastV = '?'
                self.model.realVoltage.setText(str(lastV))
            except Exception as e:
                print('labels update', e)
            
            
    