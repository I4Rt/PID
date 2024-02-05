from data.BaseData import *

class AmperageDataMeasurement(BaseData):
    __tablename__ = 'AmperageDataMeasurement'
    
    time = Column(Integer, unique=False)
    value = Column(Double, unique=False)
    
    experimentId = Column(Integer, ForeignKey('Experiment.id', ondelete="CASCADE"), nullable=False)
    
    
    def __init__(self, value:float, time:int, expId:int = None):
        self.value = value
        self.time = time
        self.expId = expId
        
    
    @classmethod
    def selectByExperimentId(cls, experimentId):
        with DBSessionMaker.getSession() as ses:
            return ses.query(cls).filter_by(experimentId=experimentId).order_by(cls.time).all()