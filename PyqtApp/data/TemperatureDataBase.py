from config import *
from data.BaseData import BaseData 


from sqlalchemy import ForeignKey
from datetime import datetime
from tools.DBSessionMaker import *
class TemperatureDataBase(BaseData):
    __abstract__ = True
    
    value = Column(Double, unique=False)
    time = Column(Double, unique=False)
    # experimentId = Column(Integer, ForeignKey('Experiment.id'), nullable=False)
    
    def __init__(self, value, time):
        BaseData.__init__(self)
        self.value = value
        self.time = time
    
    @classmethod
    def selectByExperimentId(cls, experimentId):
        with DBSessionMaker.getSession() as ses:
            return ses.query(cls).filter_by(experimentId=experimentId).all()
    
    
    