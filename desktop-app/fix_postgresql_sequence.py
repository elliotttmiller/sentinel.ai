#!/usr/bin/env python3
"""
PostgreSQL Sequence Fix
Fixes the auto-increment sequence for PostgreSQL database
"""

import os
import sys
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.exc import SQLAlchemyError

def fix_postgresql_sequence():
    """Fix the PostgreSQL sequence for auto-increment"""
    print("🔧 Fixing PostgreSQL sequence...")
    
    try:
        # Get database URL from environment
        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            print("❌ DATABASE_URL not found in environment")
            return False
            
        print(f"📁 Using database: {database_url}")
        
        # Create engine
        engine = create_engine(database_url)
        
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
                
                # Set the sequence to start from 1 (since table is likely empty)
                conn.execute(text("SELECT setval('missions_id_seq', 1, false)"))
                
                conn.commit()
                print("✅ PostgreSQL sequence created!")
            else:
                print("✅ PostgreSQL sequence already exists")
                
                # Check if the sequence is properly linked to the table
                result = conn.execute(text("""
                    SELECT column_default 
                    FROM information_schema.columns 
                    WHERE table_name = 'missions' AND column_name = 'id'
                """))
                
                default_value = result.fetchone()
                if default_value and 'nextval' not in str(default_value[0]):
                    print("⚠️ Sequence not linked to table, fixing...")
                    conn.execute(text("ALTER TABLE missions ALTER COLUMN id SET DEFAULT nextval('missions_id_seq')"))
                    conn.commit()
                    print("✅ Sequence linked to table!")
                else:
                    print("✅ Sequence properly linked to table")
                
                # Fix the sequence value to avoid conflicts
                print("🔧 Fixing sequence value...")
                result = conn.execute(text("SELECT MAX(CAST(id AS INTEGER)) FROM missions WHERE id ~ '^[0-9]+$'"))
                max_id = result.fetchone()[0]
                if max_id is None:
                    max_id = 0
                next_val = max_id + 1
                conn.execute(text(f"SELECT setval('missions_id_seq', {next_val}, true)"))
                conn.commit()
                print(f"✅ Sequence set to start from {next_val}")
                    
    except SQLAlchemyError as e:
        print(f"❌ Database error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error fixing database: {e}")
        return False
    
    print("✅ PostgreSQL sequence fix completed!")
    return True

def test_mission_creation():
    """Test if mission creation works after the fix"""
    print("\n🧪 Testing mission creation...")
    
    try:
        database_url = os.getenv("DATABASE_URL")
        engine = create_engine(database_url)
        
        with engine.connect() as conn:
            # Try to create a test mission with all required fields
            result = conn.execute(text("""
                INSERT INTO missions (
                    mission_id_str, title, description, prompt, agent_type, status
                )
                VALUES (
                    :mission_id_str, :title, :description, :prompt, :agent_type, :status
                )
                RETURNING id
            """), {
                "mission_id_str": "test_mission_789",
                "title": "Test Mission",
                "description": "This is a test mission description",
                "prompt": "This is a test mission",
                "agent_type": "developer",
                "status": "pending"
            })
            
            # Get the auto-generated ID
            mission_id = result.fetchone()[0]
            print(f"✅ Test mission created successfully with ID: {mission_id}")
            
            # Clean up the test mission
            conn.execute(text("DELETE FROM missions WHERE mission_id_str = :mission_id_str"), {
                "mission_id_str": "test_mission_789"
            })
            conn.commit()
            
            print("✅ Test mission cleaned up")
            return True
        
    except Exception as e:
        print(f"❌ Test mission creation failed: {e}")
        return False

if __name__ == "__main__":
    print("🔧 PostgreSQL Sequence Fix Tool")
    print("=" * 50)
    
    if fix_postgresql_sequence():
        if test_mission_creation():
            print("\n🎉 All fixes applied successfully!")
            print("Your agent deployment system should now work properly.")
        else:
            print("\n⚠️ Fix applied but test failed. There may be other issues.")
    else:
        print("\n❌ Failed to apply database fixes.") 