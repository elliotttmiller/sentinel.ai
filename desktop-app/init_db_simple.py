#!/usr/bin/env python3
"""
Simple Database Initialization
Creates the database tables without ChromaDB dependencies
"""

import os
import sys
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from sqlalchemy import text

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# Create base class
Base = declarative_base()

class Mission(Base):
    """Mission tracking with comprehensive metadata"""
    __tablename__ = "missions"
    
    id = Column(Integer, primary_key=True, index=True)
    mission_id_str = Column(String, unique=True, index=True)
    title = Column(String, nullable=True)
    prompt = Column(Text, nullable=False)
    agent_type = Column(String, default="developer")
    status = Column(String, default="pending")
    result = Column(Text, nullable=True)
    plan = Column(Text, nullable=True)  # Using Text instead of JSON for SQLite compatibility
    execution_time = Column(Integer, nullable=True)
    tokens_used = Column(Integer, nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    is_archived = Column(Boolean, default=False)

class MissionUpdate(Base):
    """Real-time mission updates for observability"""
    __tablename__ = "mission_updates"
    
    id = Column(Integer, primary_key=True, index=True)
    mission_id_str = Column(String, index=True)
    update_message = Column(Text, nullable=False)
    update_type = Column(String, default="info")
    timestamp = Column(DateTime, default=datetime.utcnow)
    agent_role = Column(String, nullable=True)
    step_number = Column(Integer, nullable=True)

class SystemLog(Base):
    """System-level logging and monitoring"""
    __tablename__ = "system_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    level = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    component = Column(String, nullable=True)
    source = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    log_metadata = Column(Text, nullable=True)  # Using Text instead of JSON

def init_database():
    """Initialize the database with all tables"""
    print("🔧 Initializing database...")
    
    try:
        # Get database URL
        database_url = os.getenv("DATABASE_URL", "sqlite:///db/sentinel_missions.db")
        print(f"📁 Using database: {database_url}")
        
        # Create engine
        engine = create_engine(database_url)
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        
        print("✅ Database tables created successfully!")
        
        # Test table creation
        with engine.connect() as conn:
            # Test mission creation
            result = conn.execute(text("""
                INSERT INTO missions (mission_id_str, title, prompt, agent_type, status)
                VALUES (:mission_id_str, :title, :prompt, :agent_type, :status)
            """), {
                "mission_id_str": "test_mission_456",
                "title": "Test Mission",
                "prompt": "This is a test mission",
                "agent_type": "developer",
                "status": "pending"
            })
            
            mission_id = result.lastrowid
            print(f"✅ Test mission created with ID: {mission_id}")
            
            # Clean up test mission
            conn.execute(text("DELETE FROM missions WHERE mission_id_str = :mission_id_str"), {
                "mission_id_str": "test_mission_456"
            })
            conn.commit()
            
            print("✅ Test mission cleaned up")
            
        return True
        
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        return False

if __name__ == "__main__":
    print("🔧 Simple Database Initialization Tool")
    print("=" * 50)
    
    if init_database():
        print("\n🎉 Database initialized successfully!")
        print("Your agent deployment system should now work properly.")
    else:
        print("\n❌ Failed to initialize database.") 