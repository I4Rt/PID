from __future__ import annotations

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QTimer, QAbstractTableModel
from PyQt5.QtWidgets import QFileDialog

from view.TabsViewPlain import *
from model.ViewState import ViewState



class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    
    def __init__(self, *args, **kwargs):
        Ui_MainWindow.__init__(self, *args, **kwargs)
        QtWidgets.QMainWindow.__init__(self, *args, *kwargs)
        
        self.state = ViewState.getState()
        self.state.experiment = Experiment('') # fucked
        self.setupUi(self)
        self.__initButtons()
        self.setFirstPosition()
        
        self.plotUpdater =  self.__PlotControll(self)
        self.plotUpdater.startUpdate()
    
    
    def setFirstPosition(self):
        self.tabWidget.setTabEnabled(1, False)
        self.tabWidget.setTabEnabled(2, False)
        self.deleteExpButton.setEnabled(False)
    
    def setSecondPosition(self):
        self.tabWidget.setTabEnabled(1, True)
        self.tabWidget.setTabEnabled(2, True)
        self.deleteExpButton.setEnabled(True)
    
    def __initButtons(self):
        self.expName.textEdited.connect(self.setExperimentName)
        self.plainTextEdit.textChanged.connect(self.setExperimentDescription)
        self.saveExpButton.clicked.connect(self.saveExperiment)
        self.deleteExpButton.clicked.connect(self.dropExperiment)
        
        self.load_file.triggered.connect(self.loadExperiment)
        self.tableWidget.itemChanged.connect(self.updateDataFromTable)
        
        # control PID buttons
        self.start_btn.clicked.connect(self.playFirstPID)
        self.stop_btn.clicked.connect(self.pauseFirstPID)
        self.startTest.clicked.connect(self.playSecondPID)
        self.stopTest.clicked.connect(self.pauseSecondPID)
        
        #comments
        self.submitComment.clicked.connect(self.addComment)
        self.free_real_track.triggered.connect(self.dropExperimentData)
        
        #motors
        self.smashSwitch.clicked.connect(self.toggleNeedShuffle)
        self.setTargetDeep.clicked.connect(self.setDeepth)
        self.baseSearch.clicked.connect(self.goHome)
        
      
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
        
    # buttons actions
    def addComment(self):
        
        if self.textEdit.toPlainText() != '':
            text = self.textEdit.toPlainText()
            time = self.state.getPlot2NowTime()
            if not time:
                try:
                    time = self.state.experiment.getData(SSRealDataMeasurement)[-1].time
                except:
                    time = None
            if time:
                try:
                    self.state.experiment.addComment(text, time)
                    self.textEdit.setPlainText('')
                    self.textBrowser.append(f'<p><b>{time}</b><span>: {text}</span></p>')
                    self.subplot2.axvline(x=time, color="red")
                except:
                    self.showMessage('Недопустимое действие', 'Недопустимое время комментария\n(на данное время уже есть комментарий)')
            else:
                self.showMessage('Недопустимое действие', 'Недопустимое время комментария')
        else:
            self.showMessage('Недопустимое действие', 'Пустое поле текста комментария')
            
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
            self.state.experiment.dropFSRealData()
            self.state.experiment.dropSSRealData()
            self.state.experiment.dropComments()
            self.state.experiment.save()
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
        self.resetExperimentBooleans(True)
        self.state.experiment.delete()
        self.state.experiment = Experiment('')
        self.__setExperimentDataToView()
        self.resetExperimentBooleans(True)
        self.setFirstPosition()
     
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
            for comment in self.state.experiment.getComments():
                time = comment.time
                text = comment.text
                self.textBrowser.append(f'<p><b>{time}</b><span>: {text}</span></p>')
                self.subplot2.axvline(x=time, color="red")
                
            self.state.dropPlotTimes()
            if len(self.state.experiment.fsRealData):
                self.state.plot1Stopped = True
            
        self.sideDialog = None 
        
        
    # motors area button functions
    def toggleNeedShuffle(self):
        self.state.needShuffle = not self.state.needShuffle
        if self.state.needShuffle:
            self.smashSwitch.setText('Остановить')
        else:
            self.smashSwitch.setText('Начать')
            
    def setDeepth(self):
        if self.state.commandMotorVerticalIsRunning:
            self.showMessage('Недопустимая команда', 'Платформа занята')
        else:
            if self.state.currentDeep is None:
                self.showMessage('Недопустимая команда', 'Неизвестное положение платформы\nОтправьте платформу на базу')
            else:
                newDeepth = self.targetDeepSpinBox.value()
                self.state.targetDeep = newDeepth
                self.state.needMoveDistance = True
        
    def goHome(self):
        if self.state.commandMotorVerticalIsRunning:
            self.showMessage('Недопустимая команда', 'Платформа занята')
        else:
            self.state.needGoHome = True
            self.state.targetDeep = 0
            self.realDeepLabel.setText('?')
            
    
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
    
        
    class __PlotControll():
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
                self.model.ui_real_plot_data, = self.model.subplot.plot([], []) 
                
                self.model.secondPlotTarget = self.model.subplot2.axhline(y=self.model.state.experiment.ssTarget, color="black", linestyle="--")
                self.model.ui_real_plot2_data, = self.model.subplot2.plot([], []) 
                
                # self.model.approx_figure = self.model.subplot.fill_between(np.array([]),np.array([]),np.array([]), color='blue', alpha=0.3)
                self.model.plotupdater = QTimer()
                self.model.plotupdater.setInterval(1000)
                self.model.plotupdater.timeout.connect(self.updatePlots)
                self.model.plotupdater.start()
            
        def updatePlots(self):
            self.setPlot1Data()
            self.setPlot2Data()
            self.updateDeepth()
                
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
                realDataArray[0].append(realData[index].time)
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
                
            # self.graphicsView.getFigure().canvas.draw()
            self.model.graphicsView.getFigure().canvas.draw_idle()
                
        def setPlot2Data(self):
            self.model.secondPlotTarget.set_ydata(self.model.state.experiment.ssTarget)
            
            
            # self.model.secondPlotTarget = self.model.subplot2.axhline(y=self.model.state.experiment.ssTarget, color="black", linestyle="--")
            
            realData = self.model.state.experiment.getData(SSRealDataMeasurement)
            realDataArray = [[], []]
            for index in range(len(realData)):
                realDataArray[0].append(realData[index].time)
                realDataArray[1].append(realData[index].value)
                
            self.model.ui_real_plot2_data.set_xdata(realDataArray[0])
            self.model.ui_real_plot2_data.set_ydata(realDataArray[1])
            if self.model.state.needAIM:
                try:
                    self.model.subplot2.set_ybound(self.model.state.experiment.ssTarget - 50, self.model.state.experiment.ssTarget + 50)
                    self.model.subplot2.set_xbound(realDataArray[0][0], realDataArray[0][-1])
                except:
                    pass

            # self.graphicsView.getFigure().canvas.draw()
            self.model.graphicsView_2.getFigure().canvas.draw_idle()