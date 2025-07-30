#!/usr/bin/env python3
"""
Database Migration Script
Updates PostgreSQL schema to match current models
"""

import os
import sys
from pathlib import Path
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.exc import SQLAlchemyError
from dotenv import load_dotenv

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

from src.models.advanced_database import Base, engine, SessionLocal
from loguru import logger

# Load environment variables
load_dotenv()

def migrate_database():
    """Migrate the database schema to match current models"""
    print("🔧 Starting database migration...")
    
    try:
        # Test connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("✅ Database connection successful")
        
        # Get inspector
        inspector = inspect(engine)
        
        # Check if tables exist
        existing_tables = inspector.get_table_names()
        print(f"📋 Existing tables: {existing_tables}")
        
        # Define the expected schema
        expected_schema = {
            "missions": [
                "id INTEGER PRIMARY KEY",
                "mission_id_str VARCHAR UNIQUE",
                "title VARCHAR",
                "prompt TEXT NOT NULL",
                "agent_type VARCHAR DEFAULT 'developer'",
                "status VARCHAR DEFAULT 'pending'",
                "result TEXT",
                "plan JSON",
                "execution_time INTEGER",
                "tokens_used INTEGER",
                "error_message TEXT",
                "created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
                "updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
                "completed_at TIMESTAMP",
                "is_archived BOOLEAN DEFAULT FALSE"
            ],
            "mission_updates": [
                "id INTEGER PRIMARY KEY",
                "mission_id_str VARCHAR",
                "update_message TEXT NOT NULL",
                "update_type VARCHAR DEFAULT 'info'",
                "timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
                "agent_role VARCHAR",
                "step_number INTEGER"
            ],
            "system_logs": [
                "id INTEGER PRIMARY KEY",
                "level VARCHAR NOT NULL",
                "message TEXT NOT NULL",
                "component VARCHAR",
                "source VARCHAR",
                "created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
                "log_metadata JSON"
            ]
        }
        
        # Create tables if they don't exist
        for table_name, columns in expected_schema.items():
            if table_name not in existing_tables:
                print(f"📝 Creating table: {table_name}")
                
                # Create table with proper schema
                create_sql = f"""
                CREATE TABLE {table_name} (
                    {', '.join(columns)}
                )
                """
                
                with engine.connect() as conn:
                    conn.execute(text(create_sql))
                    conn.commit()
                
                print(f"✅ Created table: {table_name}")
            else:
                print(f"✅ Table exists: {table_name}")
                
                # Check for missing columns
                existing_columns = [col['name'] for col in inspector.get_columns(table_name)]
                print(f"   Existing columns: {existing_columns}")
                
                # Add missing columns
                for column_def in columns:
                    column_name = column_def.split()[0]
                    if column_name not in existing_columns:
                        print(f"   📝 Adding column: {column_name}")
                        try:
                            with engine.connect() as conn:
                                conn.execute(text(f"ALTER TABLE {table_name} ADD COLUMN {column_def}"))
                                conn.commit()
                            print(f"   ✅ Added column: {column_name}")
                        except SQLAlchemyError as e:
                            print(f"   ⚠️ Column {column_name} might already exist: {e}")
        
        print("🎉 Database migration completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Database migration failed: {e}")
        logger.error(f"Migration error: {e}")
        return False

def test_migration():
    """Test the migration by running a simple query"""
    try:
        db = SessionLocal()
        
        # Test missions table
        result = db.execute(text("SELECT COUNT(*) FROM missions"))
        count = result.scalar()
        print(f"✅ Missions table test: {count} records")
        
        # Test mission_updates table
        result = db.execute(text("SELECT COUNT(*) FROM mission_updates"))
        count = result.scalar()
        print(f"✅ Mission updates table test: {count} records")
        
        # Test system_logs table
        result = db.execute(text("SELECT COUNT(*) FROM system_logs"))
        count = result.scalar()
        print(f"✅ System logs table test: {count} records")
        
        db.close()
        print("✅ All database tables are working correctly!")
        return True
        
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Sentinel Database Migration Tool")
    print("=" * 50)
    
    if migrate_database():
        print("\n🧪 Testing migration...")
        if test_migration():
            print("\n🎉 Migration completed successfully!")
            print("📱 Your desktop app should now work with the database!")
        else:
            print("\n⚠️ Migration completed but tests failed. Check the logs.")
    else:
        print("\n❌ Migration failed. Check the error messages above.") 