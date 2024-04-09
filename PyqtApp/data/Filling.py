from config import *
from data.BaseData import BaseData 
from tools.DBSessionMaker import *



class Filling(BaseData):
    __tablename__ = 'Filling'

    experimentId = Column(Integer, ForeignKey('Experiment.id', ondelete="CASCADE"), nullable=False)
    name = Column(Text, unique=False)
    value= Column(Double, unique=False, nullable=False)
    time = Column(Double, nullable=False)
    
    def __init__(self, name, value, time, expId = None):
        BaseData.__init__(self)
        self.name = name
        self.value = value
        self.time = time
        self.experimentId = expId
    