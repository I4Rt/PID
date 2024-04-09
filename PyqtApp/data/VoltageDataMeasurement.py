from data.BaseData import *

class VoltageDataMeasurement(BaseData):
    __tablename__ = 'VoltageDataMeasurement'
    
    time = Column(Double, unique=False)
    value = Column(Double, unique=False)
    
    experimentId = Column(Integer, ForeignKey('Experiment.id', ondelete="CASCADE"), nullable=False)
    
    
    def __init__(self, value:float, time:float, expId:int = None):
        self.value = value
        self.time = time
        self.experimentId = expId
        
    
    @classmethod
    def selectByExperimentId(cls, experimentId, last=False):
        with DBSessionMaker.getSession() as ses:
            if not last:
                return ses.query(cls).filter_by(experimentId=experimentId).order_by(cls.time).all()
            return ses.query(cls).filter_by(experimentId=experimentId).order_by(cls.time.desc()).first()