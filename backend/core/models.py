from sqlalchemy import Column, String, Text, DateTime, JSON
from sqlalchemy.sql import func
from .database import Base

class Mission(Base):
    __tablename__ = "missions"

    id = Column(String, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(Text)
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
    name = Column(String, nullable=False)
    type = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    capabilities = Column(JSON, nullable=True)
    status = Column(String, nullable=False)
    last_active = Column(DateTime, nullable=True)
    missions_completed = Column(String, nullable=True) 