from config import *
from typing import List
from tools.Jsonifyer import *
from sqlalchemy import or_, and_

from tools.DBSessionMaker import *

class BaseData(Jsonifyer, Base):
    __abstract__ = True
    
    id = Column(Integer, primary_key=True)
    
    def __init__(self, id = None):
        Base
        Jsonifyer.__init__(self)
        self.id = id
             
    def __save(self):
        with DBSessionMaker.getSession() as ses:
            ses.add(self)
            ses.commit()
            return self.id
        
    def save(self):
        self:self.__class__ = self.getByID(self.__save())
        
    @classmethod 
    def getAll(cls) -> List["BaseData"]:
        with DBSessionMaker.getSession() as ses:
            return ses.query(cls).all()
        
    @classmethod 
    def getByID(cls, searchId:int) -> "BaseData":
        with DBSessionMaker.getSession() as ses:
            return ses.query(cls).filter_by(id=searchId).first() 

    def delete(self):
        with DBSessionMaker.getSession() as ses:
            ses.delete(self)
            ses.commit()
            
    @classmethod
    def deleteAll(cls):
        with DBSessionMaker.getSession() as ses:
            res = ses.query(cls).delete()
            ses.commit()
            print(f'deleted {res}')
              
    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self.getParamsList()}>"
    
    def __str__(self) -> str:
        return f"{self.__class__.__name__} {self.getParamsList()}"
    
    
    
        
    