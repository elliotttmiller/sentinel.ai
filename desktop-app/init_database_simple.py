#!/usr/bin/env python3
"""
Simple Database Initialization Script for Cognitive Forge
Creates database tables without ChromaDB dependency
"""

import os
import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, JSON, Boolean
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database Configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///db/sentinel_missions.db")

# Configure engine
if DATABASE_URL.startswith("postgresql"):
    engine = create_engine(DATABASE_URL)
else:
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Define models without ChromaDB dependency
class Mission(Base):
    __tablename__ = "missions"
    id = Column(Integer, primary_key=True, index=True)
    mission_id_str = Column(String, unique=True, index=True)
    title = Column(String, nullable=True)
    prompt = Column(Text, nullable=False)
    agent_type = Column(String, default="developer")
    status = Column(String, default="pending")
    result = Column(Text, nullable=True)
    plan = Column(JSON, nullable=True)
    execution_time = Column(Integer, nullable=True)
    tokens_used = Column(Integer, nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    is_archived = Column(Boolean, default=False)

class MissionUpdate(Base):
    __tablename__ = "mission_updates"
    id = Column(Integer, primary_key=True, index=True)
    mission_id_str = Column(String, index=True)
    update_message = Column(Text, nullable=False)
    update_type = Column(String, default="info")
    timestamp = Column(DateTime, default=datetime.utcnow)
    agent_role = Column(String, nullable=True)
    step_number = Column(Integer, nullable=True)

class SystemLog(Base):
    __tablename__ = "system_logs"
    id = Column(Integer, primary_key=True, index=True)
    level = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    component = Column(String, nullable=True)
    source = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    log_metadata = Column(JSON, nullable=True)

def init_database():
    """Initialize the database with all required tables"""
    print("🔧 Initializing Cognitive Forge Database (Simple Mode)...")
    
    try:
        # Ensure db directory exists
        os.makedirs("db", exist_ok=True)
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created successfully")
        
        # Test database connection
        db = SessionLocal()
        try:
            mission_count = db.query(Mission).count()
            print(f"✅ Database connection test successful: {mission_count} missions found")
        finally:
            db.close()
        
        print("🎉 Database initialization complete!")
        return True
        
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        return False

if __name__ == "__main__":
    init_database() 