from config import *
from data.BaseData import BaseData 
from tools.DBSessionMaker import *

from data.FSTargetDataMeasurement import *
from data.FSRealDataMeasurement import *
from data.SSRealDataMeasurement import *


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

    def __init__(self,  name, descriotion='', beginningTime=datetime.now(), fsTargetData=[], fsRealData=[], ssTarget=20, ssRealData=[]):
        BaseData.__init__(self)
        self.name = name
        self.description = descriotion
        
        self.beginingTime = beginningTime
        
        self.fsTargetData = fsTargetData
        self.fsRealData = fsRealData
        self.ssTarget = ssTarget
        self.ssRealData = ssRealData
            
    def __addLinkedClassData(self, dataclass:type[TemperatureDataBase], temperature:float, time:float, __needSaveSelf:bool=True):
        if __needSaveSelf:
            self.save()
        targetData = dataclass(temperature, time, self.id)
        targetData.save()
        
    def __dropLinkedClassData(self, dataclass):
        with DBSessionMaker.getSession() as ses:
            ses.query(dataclass).filter_by(experimentId = self.id).delete()
       
    def getData(self, className:type[TemperatureDataBase]):
        targetId = self.id
        return className.selectByExperimentId(targetId)
            
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
        
    def dropFSTargetData(self):
        self.__dropLinkedClassData(FSTargetDataMeasurement)
        
    def dropFSRealData(self):
        self.__dropLinkedClassData(FSRealDataMeasurement)
            
    def dropSSRealData(self):
        self.__dropLinkedClassData(SSRealDataMeasurement)
    
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
            self.addFSTargetData(point[0], point[1], False)
            
            



    
            
    