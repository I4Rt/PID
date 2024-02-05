from config import *
from data.BaseData import BaseData 
from tools.DBSessionMaker import *

from data.FSTargetDataMeasurement import *
from data.FSRealDataMeasurement import *
from data.SSRealDataMeasurement import *

from data.AmperageDataMeasurement import *

from data.Comment import *


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
    
    comments = relationship('Comment', cascade="all,delete", backref='Experiment', lazy='subquery')
    
    amperageData = relationship('AmperageDataMeasurement', cascade="all,delete", backref='Experiment', lazy='subquery')
    
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
        if __needSaveSelf:
            self.save()
        targetData = dataclass(value, time, self.id)
        targetData.save()
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
    
    def getData(self, className:type[TemperatureDataBase|AmperageDataMeasurement]):
        targetId = self.id
        return className.selectByExperimentId(targetId)
    
    def getComments(self, limit = None):
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
        
    def addAmperageData(self, value:float, time:int|float, __needSaveSelf=True):
        self.__addLinkedClassData(AmperageDataMeasurement, value, time, __needSaveSelf)
        
    def dropFSTargetData(self):
        return self.__dropLinkedClassData(FSTargetDataMeasurement)
        
    def dropFSRealData(self):
        return self.__dropLinkedClassData(FSRealDataMeasurement)
            
    def dropSSRealData(self):
        return self.__dropLinkedClassData(SSRealDataMeasurement)
    
    def dropAmperageData(self):
        return self.__dropLinkedClassData(AmperageDataMeasurement)
    
    def dropComments(self):
        return self.__dropLinkedClassData(Comment)
    
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
