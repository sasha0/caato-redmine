# -*- coding: utf-8 -*-
from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# using SQLite database for log
engine = create_engine('sqlite:///sync_log.db')
Base = declarative_base()
Base.metadata.create_all(engine)


class SyncLog(Base):
    """
    Model for logging time entry synchronization.
    Needed to avoid repeated synchronization and time entry duplication.
    """
    
    __tablename__ = 'synclog'
    
    id = Column(Integer, primary_key=True)
    task_id = Column(Integer)   # task ID in Redmine
    start_datetime = Column(DateTime)
    end_datetime = Column(DateTime)
    duration = Column(Float)


Session = sessionmaker(bind=engine)
session = Session()
