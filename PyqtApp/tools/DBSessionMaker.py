from config import *
from contextlib import contextmanager

class DBSessionMaker:
    
    @contextmanager
    @staticmethod
    def getSession() -> Session:
        """ Creates a context with an open SQLAlchemy session."""
        db_session = scoped_session(sessionmaker(autocommit=False, autoflush=True, bind=e))
        yield db_session
        db_session.close()
        