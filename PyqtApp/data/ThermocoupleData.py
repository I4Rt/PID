

from config import *
from data.BaseData import BaseData 
from tools.DBSessionMaker import *

class ThermocoupleData(BaseData):
    __tablename__ = 'ThermocoupleData'
    
    experimentId = Column(Integer, ForeignKey('Experiment.id', ondelete="CASCADE"), nullable=False)
    value = Column(Double, unique=False)
    time = Column(Double, unique=True, nullable=False)
    
    def __init__(self, value, time, expId = None):
        BaseData.__init__(self)
        self.value = value
        self.time = time
        self.experimentId = expId

    @classmethod
    def selectByExperimentId(cls, experimentId, last=False):
        with DBSessionMaker.getSession() as ses:
            if not last:
                return ses.query(cls).filter_by(experimentId=experimentId).order_by(cls.time).all()
            return ses.query(cls).filter_by(experimentId=experimentId).order_by(cls.time.desc()).first()