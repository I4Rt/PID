from config import *
from data.BaseData import BaseData 
from tools.DBSessionMaker import *

class Comment(BaseData):
    __tablename__ = 'Comment'
    
    experimentId = Column(Integer, ForeignKey('Experiment.id', ondelete="CASCADE"), nullable=False)
    text = Column(Text, unique=False)
    time = Column(Double, unique=True, nullable=False)
    
    def __init__(self, text, time, expId = None):
        BaseData.__init__(self)
        self.text = text
        self.time = time
        self.experimentId = expId
        
    