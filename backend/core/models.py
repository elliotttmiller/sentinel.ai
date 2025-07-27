from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Text, DateTime
from sqlalchemy.dialects.postgresql import JSONB
import datetime

Base = declarative_base()

# Example model
# from sqlalchemy import Column, Integer, String
# class Mission(Base):
#     __tablename__ = "missions"
#     id = Column(Integer, primary_key=True, index=True)
#     prompt = Column(String, index=True) 

class Mission(Base):
    __tablename__ = "missions"
    id = Column(String, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    status = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    steps = Column(JSONB, nullable=True)
    plan = Column(JSONB, nullable=True)
    result = Column(JSONB, nullable=True) 

class Agent(Base):
    __tablename__ = "agents"
    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    type = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    capabilities = Column(JSONB, nullable=True)
    status = Column(String, nullable=False)
    last_active = Column(DateTime, nullable=True)
    missions_completed = Column(String, nullable=True) 