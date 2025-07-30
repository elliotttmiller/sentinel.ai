import os
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Mission(Base):
    __tablename__ = "missions"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=True)  # Optional mission title
    prompt = Column(Text, nullable=False)
    agent_type = Column(String(50), default="researcher")  # Type of agent used
    status = Column(String(32), default="pending")  # pending, executing, completed, failed
    result = Column(Text, nullable=True)
    error_message = Column(Text, nullable=True)  # Detailed error if failed
    execution_time = Column(Integer, nullable=True)  # Execution time in seconds
    tokens_used = Column(Integer, nullable=True)  # LLM tokens consumed
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)  # When mission was completed
    is_archived = Column(Boolean, default=False)  # For soft deletion


class SystemLog(Base):
    __tablename__ = "system_logs"

    id = Column(Integer, primary_key=True, index=True)
    level = Column(String(20), nullable=False)  # INFO, WARNING, ERROR, DEBUG
    message = Column(Text, nullable=False)
    source = Column(String(100), nullable=False)  # Component that generated the log
    created_at = Column(DateTime, default=datetime.utcnow)
    log_metadata = Column(Text, nullable=True)  # JSON string for additional data


# Create all tables
Base.metadata.create_all(bind=engine)
