#!/usr/bin/env python3
"""
Database Initialization Script for Cognitive Forge
Creates all required database tables and initializes ChromaDB
"""

import os
import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

from src.models.advanced_database import Base, engine, db_manager
from loguru import logger

def init_database():
    """Initialize the database with all required tables"""
    print("🔧 Initializing Cognitive Forge Database...")
    
    try:
        # Create all tables
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created successfully")
        
        # Test database connection
        stats = db_manager.get_system_stats()
        print(f"✅ Database connection test successful: {stats}")
        
        print("🎉 Database initialization complete!")
        return True
        
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        logger.error(f"Database initialization error: {e}")
        return False

if __name__ == "__main__":
    init_database() 