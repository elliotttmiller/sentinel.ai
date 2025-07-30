#!/usr/bin/env python3
"""
Fix Mission ID Auto-increment Issue
Updates the database to properly handle auto-incrementing IDs
"""

import os
import sys
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.exc import SQLAlchemyError

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.models.advanced_database import engine, Base

def fix_mission_id_autoincrement():
    """Fix the mission ID auto-increment issue"""
    print("🔧 Fixing mission ID auto-increment issue...")
    
    try:
        # Check if we're using SQLite or PostgreSQL
        database_url = os.getenv("DATABASE_URL", "sqlite:///db/sentinel_missions.db")
        
        if "sqlite" in database_url.lower():
            print("📁 Using SQLite database")
            # For SQLite, we need to recreate the table with proper auto-increment
            with engine.connect() as conn:
                # Check if missions table exists
                inspector = inspect(engine)
                if "missions" in inspector.get_table_names():
                    print("📋 Missions table exists, checking structure...")
                    
                    # Get current table info
                    columns = inspector.get_columns("missions")
                    id_column = next((col for col in columns if col['name'] == 'id'), None)
                    
                    if id_column and not id_column.get('autoincrement', False):
                        print("⚠️ ID column is not auto-incrementing, fixing...")
                        
                        # Create a backup of existing data
                        result = conn.execute(text("SELECT * FROM missions"))
                        existing_missions = result.fetchall()
                        print(f"📦 Backing up {len(existing_missions)} existing missions...")
                        
                        # Drop and recreate the table with proper auto-increment
                        conn.execute(text("DROP TABLE IF EXISTS missions"))
                        conn.execute(text("""
                            CREATE TABLE missions (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                mission_id_str VARCHAR UNIQUE,
                                title VARCHAR,
                                prompt TEXT NOT NULL,
                                agent_type VARCHAR DEFAULT 'developer',
                                status VARCHAR DEFAULT 'pending',
                                result TEXT,
                                plan JSON,
                                execution_time INTEGER,
                                tokens_used INTEGER,
                                error_message TEXT,
                                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                                completed_at DATETIME,
                                is_archived BOOLEAN DEFAULT FALSE
                            )
                        """))
                        
                        # Restore data if any existed
                        if existing_missions:
                            print("🔄 Restoring existing mission data...")
                            for mission in existing_missions:
                                # Skip the old id column and use new auto-increment
                                conn.execute(text("""
                                    INSERT INTO missions (
                                        mission_id_str, title, prompt, agent_type, status,
                                        result, plan, execution_time, tokens_used, error_message,
                                        created_at, updated_at, completed_at, is_archived
                                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                                """), mission[1:])  # Skip the old id
                        
                        conn.commit()
                        print("✅ Missions table fixed with proper auto-increment!")
                    else:
                        print("✅ Missions table already has proper auto-increment")
                        
        else:
            print("🐘 Using PostgreSQL database")
            # For PostgreSQL, we need to set the sequence
            with engine.connect() as conn:
                # Check if the sequence exists
                result = conn.execute(text("""
                    SELECT sequence_name 
                    FROM information_schema.sequences 
                    WHERE sequence_name = 'missions_id_seq'
                """))
                
                if not result.fetchone():
                    print("⚠️ Auto-increment sequence missing, creating...")
                    # Create the sequence
                    conn.execute(text("CREATE SEQUENCE missions_id_seq"))
                    conn.execute(text("ALTER TABLE missions ALTER COLUMN id SET DEFAULT nextval('missions_id_seq')"))
                    conn.execute(text("ALTER SEQUENCE missions_id_seq OWNED BY missions.id"))
                    conn.commit()
                    print("✅ PostgreSQL sequence created!")
                else:
                    print("✅ PostgreSQL sequence already exists")
                    
    except SQLAlchemyError as e:
        print(f"❌ Database error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error fixing database: {e}")
        return False
    
    print("✅ Mission ID auto-increment fix completed!")
    return True

def test_mission_creation():
    """Test if mission creation works after the fix"""
    print("\n🧪 Testing mission creation...")
    
    try:
        from src.models.advanced_database import db_manager
        
        # Try to create a test mission
        test_mission = db_manager.create_mission(
            mission_id_str="test_mission_123",
            title="Test Mission",
            prompt="This is a test mission",
            agent_type="developer"
        )
        
        print(f"✅ Test mission created successfully with ID: {test_mission.id}")
        
        # Clean up the test mission
        from sqlalchemy.orm import Session
        db = Session(engine)
        db.query(db_manager.Base.classes.Mission).filter_by(mission_id_str="test_mission_123").delete()
        db.commit()
        db.close()
        
        print("✅ Test mission cleaned up")
        return True
        
    except Exception as e:
        print(f"❌ Test mission creation failed: {e}")
        return False

if __name__ == "__main__":
    print("🔧 Mission ID Auto-increment Fix Tool")
    print("=" * 50)
    
    if fix_mission_id_autoincrement():
        if test_mission_creation():
            print("\n🎉 All fixes applied successfully!")
            print("Your agent deployment system should now work properly.")
        else:
            print("\n⚠️ Fix applied but test failed. There may be other issues.")
    else:
        print("\n❌ Failed to apply database fixes.") 