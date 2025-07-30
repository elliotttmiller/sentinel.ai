#!/usr/bin/env python3
"""
Fix Database Schema Issues
Handles existing data when adding new columns
"""

import os
import sys
from pathlib import Path
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.exc import SQLAlchemyError
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

def fix_database_schema():
    """Fix database schema issues"""
    print("Fixing database schema issues...")
    
    try:
        # Test connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("Database connection successful")
        
        # Get inspector
        inspector = inspect(engine)
        
        # Check missions table
        if "missions" in inspector.get_table_names():
            print("[INFO] Checking missions table...")
            
            existing_columns = [col['name'] for col in inspector.get_columns("missions")]
            print(f"   Existing columns: {existing_columns}")
            
            # Add missing columns with proper defaults
            missing_columns = [
                ("mission_id_str", "VARCHAR", "NULL"),
                ("prompt", "TEXT", "''"),
                ("agent_type", "VARCHAR", "'developer'"),
                ("execution_time", "INTEGER", "NULL"),
                ("tokens_used", "INTEGER", "NULL"),
                ("error_message", "TEXT", "NULL"),
                ("is_archived", "BOOLEAN", "FALSE")
            ]
            
            for col_name, col_type, default_value in missing_columns:
                if col_name not in existing_columns:
                    print(f"   [ADD] Adding column: {col_name}")
                    try:
                        # Add column with default value
                        if default_value == "NULL":
                            sql = f"ALTER TABLE missions ADD COLUMN {col_name} {col_type}"
                        else:
                            sql = f"ALTER TABLE missions ADD COLUMN {col_name} {col_type} DEFAULT {default_value}"
                        
                        with engine.connect() as conn:
                            conn.execute(text(sql))
                            conn.commit()
                        
                        print(f"   [OK] Added column: {col_name}")
                        
                        # Update existing rows if needed
                        if default_value != "NULL" and default_value != "FALSE":
                            update_sql = f"UPDATE missions SET {col_name} = {default_value} WHERE {col_name} IS NULL"
                            with engine.connect() as conn:
                                conn.execute(text(update_sql))
                                conn.commit()
                            print(f"   [OK] Updated existing rows for: {col_name}")
                            
                    except SQLAlchemyError as e:
                        print(f"   [WARN] Column {col_name} might already exist: {e}")
                else:
                    print(f"   [OK] Column exists: {col_name}")
        
        # Check mission_updates table
        if "mission_updates" in inspector.get_table_names():
            print("[INFO] Checking mission_updates table...")
            existing_columns = [col['name'] for col in inspector.get_columns("mission_updates")]
            print(f"   Existing columns: {existing_columns}")
            
            # All required columns should be present
            required_columns = ["id", "mission_id_str", "update_message", "update_type", "timestamp", "agent_role", "step_number"]
            for col in required_columns:
                if col not in existing_columns:
                    print(f"   [WARN] Missing column: {col}")
        
        # Check system_logs table
        if "system_logs" in inspector.get_table_names():
            print("[INFO] Checking system_logs table...")
            existing_columns = [col['name'] for col in inspector.get_columns("system_logs")]
            print(f"   Existing columns: {existing_columns}")
            
            # Add missing columns
            missing_columns = [
                ("component", "VARCHAR", "NULL"),
                ("log_metadata", "JSON", "NULL")
            ]
            
            for col_name, col_type, default_value in missing_columns:
                if col_name not in existing_columns:
                    print(f"   [ADD] Adding column: {col_name}")
                    try:
                        sql = f"ALTER TABLE system_logs ADD COLUMN {col_name} {col_type}"
                        with engine.connect() as conn:
                            conn.execute(text(sql))
                            conn.commit()
                        print(f"   [OK] Added column: {col_name}")
                    except SQLAlchemyError as e:
                        print(f"   [WARN] Column {col_name} might already exist: {e}")
                else:
                    print(f"   [OK] Column exists: {col_name}")
        
        print("[SUCCESS] Database schema fixes completed!")
        return True
        
    except Exception as e:
        print(f"[ERROR] Database schema fix failed: {e}")
        return False

def test_schema():
    """Test the schema by running queries"""
    try:
        print("\n[TEST] Testing schema...")
        
        with engine.connect() as conn:
            # Test missions table
            result = conn.execute(text("SELECT COUNT(*) FROM missions"))
            count = result.scalar()
            print(f"[OK] Missions table: {count} records")
            
            # Test a sample query
            result = conn.execute(text("SELECT id, mission_id_str, title, prompt FROM missions LIMIT 1"))
            row = result.fetchone()
            if row:
                print(f"[OK] Sample mission data: {row}")
            else:
                print("[OK] Missions table is empty (normal)")
            
            # Test mission_updates table
            result = conn.execute(text("SELECT COUNT(*) FROM mission_updates"))
            count = result.scalar()
            print(f"[OK] Mission updates table: {count} records")
            
            # Test system_logs table
            result = conn.execute(text("SELECT COUNT(*) FROM system_logs"))
            count = result.scalar()
            print(f"[OK] System logs table: {count} records")
        
        print("[OK] All schema tests passed!")
        return True
        
    except Exception as e:
        print(f"[ERROR] Schema test failed: {e}")
        return False

if __name__ == "__main__":
    print("Sentinel Database Schema Fix Tool")
    print("=" * 50)
    
    if fix_database_schema():
        print("\nTesting schema...")
        if test_schema():
            print("\nSchema fixes completed successfully!")
            print("Your desktop app should now work without database errors!")
        else:
            print("\nSchema fixes completed but tests failed.")
    else:
        print("\nSchema fixes failed. Check the error messages above.") 