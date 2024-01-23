from config import *
from data.TemperatureDataBase import TemperatureDataBase 
from datetime import datetime

class FSTargetDataMeasurement(TemperatureDataBase):
    __tablename__ = 'FSTargetDataMeasurement'
    experimentId = Column(Integer, ForeignKey('Experiment.id', ondelete="CASCADE"), nullable=False)
    def __init__(self, value, time, expId = None):
        TemperatureDataBase.__init__(self, value, time)
        self.experimentId = expId
        
    
    
    