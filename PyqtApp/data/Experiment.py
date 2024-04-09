from config import *
from data.BaseData import BaseData 
from tools.DBSessionMaker import *

from data.FSTargetDataMeasurement import *
from data.FSRealDataMeasurement import *
from data.SSRealDataMeasurement import *

from data.ThermocoupleData import *


from data.AmperageDataMeasurement import *
from data.VoltageDataMeasurement import *

from data.Comment import *
from data.Filling import *


from datetime import datetime

class Experiment(BaseData):
    __tablename__ = 'Experiment'
    name = Column(Text, unique=True)
    description = Column(Text, unique=False)
    beginingTime = Column(DateTime(timezone=False))
    
    fsTargetData = relationship('FSTargetDataMeasurement', cascade="all,delete", backref='Experiment', lazy='subquery')
    fsRealData = relationship('FSRealDataMeasurement', cascade="all,delete", backref='Experiment', lazy='subquery')
    
    ssTarget = Column(Double, unique=False)
    ssRealData = relationship('SSRealDataMeasurement', cascade="all,delete", backref='Experiment', lazy='subquery')
    
    thermocoupleData = relationship('ThermocoupleData', cascade="all,delete", backref='Experiment', lazy='subquery')
    
    comments = relationship('Comment', cascade="all,delete", backref='Experiment', lazy='subquery')
    fillings = relationship('Filling', cascade="all,delete", backref='Experiment', lazy='subquery')
    
    ssTargetAmperage = Column(Double, unique=False)
    amperageData = relationship('AmperageDataMeasurement', cascade="all,delete", backref='Experiment', lazy='subquery')
    voltageData = relationship('VoltageDataMeasurement', cascade="all,delete", backref='Experiment', lazy='subquery')
    
    def __init__(self,  name, descriotion='', beginningTime=datetime.now(), fsTargetData:list[FSTargetDataMeasurement]=[], fsRealData:list[FSRealDataMeasurement]=[], ssTarget=20, ssRealData:list[SSRealDataMeasurement]=[], amperageData:list[AmperageDataMeasurement]=[], comments:list[Comment]=[]):
        BaseData.__init__(self)
        self.name = name
        self.description = descriotion
        
        self.beginingTime = beginningTime
        
        self.fsTargetData:list[FSTargetDataMeasurement] = fsTargetData
        self.fsRealData:list[FSRealDataMeasurement] = fsRealData
        self.ssTarget = ssTarget
        self.ssRealData:list[SSRealDataMeasurement] = ssRealData
        
        self.amperageData:list[AmperageDataMeasurement] = amperageData
        self.comments:list[Comment] = comments
        
        self.needPID = False
        self.step = 1
        
    def setStep(self, step:int):
        '''Step of experiment might be 1 or 2'''
        if step in [1, 2]:
            self.step = step
        
    def startPID(self):
        self.needPID = True
        
    def stopPID(self):
        self.needPID = False
            
    def __addLinkedClassData(self, dataclass:type[TemperatureDataBase], value:float, time:float, __needSaveSelf:bool=True):
        targetData = dataclass(value, time, self.id)
        targetData.save()
        if __needSaveSelf:
            self.save()
        
    def __dropLinkedClassData(self, dataclass):
        with DBSessionMaker.getSession() as ses:
            res = ses.query(dataclass).filter(dataclass.experimentId==self.id).all()
            i = 0
            for data in res:
                ses.delete(data)
                i+=1
            ses.commit()
            return i
    
    def addComment(self, text, time:float, __needSaveSelf:bool=True):
        if __needSaveSelf:
            self.save()
        comment = Comment(text, time, self.id)
        comment.save()
        self.save()
        
    def addFilling(self, name, value, time:float, __needSaveSelf:bool=True):
        
        comment = Filling(name, value, time, self.id)
        comment.save()
        if __needSaveSelf:
            self.save()
    
    def getData(self, className:type[TemperatureDataBase|AmperageDataMeasurement|ThermocoupleData], last=False):
        targetId = self.id
        return className.selectByExperimentId(targetId, last)
    
    def getComments(self, limit = None) -> list[Comment]:
        with DBSessionMaker.getSession() as ses:
            if limit:   
                return ses.query(Comment).filter_by(experimentId=self.id).order_by(Comment.time).limit(limit).all()
            else:
                return ses.query(Comment).filter_by(experimentId=self.id).order_by(Comment.time).all()
                  
    def setSSTarget(self, temperature, needSaveSelf=True):
        self.ssTarget = temperature
        if needSaveSelf:
            self.save()
        
    def addFSTargetData(self, targetTemp:float, time:int|float, __needSaveSelf=True):
        self.__addLinkedClassData(FSTargetDataMeasurement, targetTemp, time, __needSaveSelf)
        
    def addFSRealData(self, realTemp:float, time:int|float, __needSaveSelf=True):
        self.__addLinkedClassData(FSRealDataMeasurement, realTemp, time, __needSaveSelf)
        
    def addSSRealData(self, realTemp:float, time:int|float, __needSaveSelf=True):
        self.__addLinkedClassData(SSRealDataMeasurement, realTemp, time, __needSaveSelf)
        
    def addVoltageData(self, realTemp:float, time:int|float, __needSaveSelf=True):
        self.__addLinkedClassData(VoltageDataMeasurement, realTemp, time, __needSaveSelf)
    
    def addThermocoupleData(self, realTemp:float, time:int|float, __needSaveSelf=True):
        self.__addLinkedClassData(ThermocoupleData, realTemp, time, __needSaveSelf)
    
    def addAmperageData(self, value:float, targetValue:float, time:int|float, __needSaveSelf=True):
        targetData = AmperageDataMeasurement(value, targetValue, time, self.id)
        targetData.save()
        if __needSaveSelf:
            self.save()
        
    def dropFSTargetData(self):
        return self.__dropLinkedClassData(FSTargetDataMeasurement)
        
    def dropFSRealData(self):
        return self.__dropLinkedClassData(FSRealDataMeasurement)
            
    def dropSSRealData(self):
        return self.__dropLinkedClassData(SSRealDataMeasurement)
    
    def getFillingRecords(self, groupTime=30):
        with DBSessionMaker.getSession() as ses:
            res = ses.execute(text(f'''with fillings as (select "name", ceil("time"/{groupTime})*{groupTime} as "res_time", sum("value")  from "Filling" where "experimentId"={self.id} group by ("res_time", "name")order by "res_time") select fillings.res_time as "time", ARRAY_AGG(fillings.name) as "names", ARRAY_AGG(fillings.sum) as weights from fillings group by "res_time";'''))
            ses.commit()
            return list(map( lambda row: row[:], res))
            
    def getTotalData(self, groupTime=30):
        try:
            with DBSessionMaker.getSession() as ses:
                sqlQuery = f'with experiment_data as ( with data_ as ( select ceil( coalesce(tmp.time, amp_vlt.time)/ {groupTime} )* {groupTime} as "time", tmp.temperature_value, tmp.thermocouple_value, amp_vlt.amperage, amp_vlt.real_amperage, amp_vlt.voltage from ( select * from ( select temp_data."experimentId", coalesce(temp_data.time, tc_data.time) as "time", temp_data."value" as temperature_value, tc_data."value" as thermocouple_value from "SSRealDataMeasurement" as temp_data full join "ThermocoupleData" as tc_data on tc_data."experimentId" = temp_data."experimentId" ) where "experimentId" = {self.id} ) as tmp full join ( select amp."time", amp.amperage, amp.real_amperage, vlt.voltage from ( select "time", "value" as amperage, "targetValue" as real_amperage, "experimentId" as exp_id from "AmperageDataMeasurement" where "experimentId" = {self.id} ) as amp join ( select "time", "value" as voltage, "experimentId" as exp_id from "VoltageDataMeasurement" where "experimentId" = {self.id} ) as vlt on amp.time = vlt.time ) as amp_vlt on tmp.time = amp_vlt.time order by "time" ) select data_.time, max(data_.temperature_value) as temperature_value, max(data_.thermocouple_value) as thermocouple_value, max(data_.amperage) as amperage, max(data_.real_amperage) as real_amperage, max(data_.voltage) as voltage from data_ group by data_.time ), filling_data as ( with fillings as ( select "name", ceil("time" / {groupTime})* {groupTime} as "res_time", sum("value") from "Filling" where "experimentId" = {self.id} group by ("res_time", "name") order by "res_time" ) select fillings.res_time as "time", ARRAY_AGG(fillings.name) as "names", ARRAY_AGG(fillings.sum) as weights from fillings group by "res_time" ), comments_data as ( select ceil("time" / {groupTime})* {groupTime} as "res_time", ARRAY_AGG("text") as "comment_text" from "Comment" where "experimentId" = {self.id} group by ("res_time") order by "res_time" ) select coalesce( filling_data.time, experiment_data.time, comments_data.res_time ) as time, experiment_data.temperature_value, experiment_data.thermocouple_value, experiment_data.amperage, experiment_data.real_amperage, experiment_data.voltage, comments_data.comment_text, filling_data.names, filling_data.weights from filling_data full outer join experiment_data on filling_data.time = experiment_data.time full outer join comments_data on experiment_data.time = comments_data.res_time;'
                res = ses.execute(text(sqlQuery))
                ses.commit()
                return list(map( lambda row: row[:], res))
        except Exception as e:
            print('\n\n\n\n\n\n\nexport exception', e,'\n\n\n\n\n\n\n')
        
    
    def dropAmperageData(self):
        return self.__dropLinkedClassData(AmperageDataMeasurement)
    
    def dropVoltageData(self):
        return self.__dropLinkedClassData(VoltageDataMeasurement)
    
    def dropThermocoupleData(self):
        return self.__dropLinkedClassData(ThermocoupleData)
    
    def dropComments(self):
        return self.__dropLinkedClassData(Comment)
    def dropFillings(self):
        return self.__dropLinkedClassData(Filling)
    
    def updateFSTargetProfile(self, targetPoints:list[list[float]]=[], __needSaveSelf=True):
        """
        Set new sequency of target temperatures
        Params:
         - targetPoints: array of the tuples (or array like sequences) like [temperature:float, time:float] data
        """
        
        self.dropFSTargetData()
        if __needSaveSelf:
            
            self.save() 
        for point in targetPoints:
            self.addFSTargetData(point[0], point[1], True)
        self.save()
