from sqlalchemy import Column, String, Integer, JSON, DateTime
from sqlalchemy.sql import func
from .database import Base

class Mission(Base):
    __tablename__ = "missions"
    id = Column(String, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String)
    status = Column(String(50), default="pending")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    steps = Column(JSON, nullable=True)
    plan = Column(JSON, nullable=True)
    result = Column(JSON, nullable=True)

class Agent(Base):
    __tablename__ = "agents"
    id = Column(String, primary_key=True, index=True)
    name = Column(String, index=True)
    type = Column(String)
    description = Column(String)
    capabilities = Column(JSON)
    status = Column(String, default="available")
    last_active = Column(DateTime, nullable=True)
    missions_completed = Column(Integer, default=0) 