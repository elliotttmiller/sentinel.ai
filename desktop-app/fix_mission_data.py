#!/usr/bin/env python3
"""
Fix mission data format to match expected API schema
Converts string IDs to integer IDs and sets mission_id_str properly
"""

import os
import sys
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.exc import SQLAlchemyError
from dotenv import load_dotenv
import re

# Load environment variables
load_dotenv()

def fix_mission_data():
    """Fix mission data format"""
    print("Fixing mission data format...")
    
    try:
        # Get database URL
        database_url = os.getenv("DATABASE_URL", "sqlite:///db/sentinel_missions.db")
        engine = create_engine(database_url)
        
        # Test connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("Database connection successful")
        
        # Get inspector
        inspector = inspect(engine)
        
        # Check if missions table exists
        if "missions" not in inspector.get_table_names():
            print("Missions table not found. Nothing to fix.")
            return True
        
        # Get existing missions
        with engine.connect() as conn:
            result = conn.execute(text("SELECT id, mission_id_str FROM missions"))
            missions = result.fetchall()
        
        print(f"Found {len(missions)} missions to process")
        
        # Process each mission
        for i, (old_id, mission_id_str) in enumerate(missions):
            print(f"Processing mission {i+1}/{len(missions)}: {old_id}")
            
            # Check if this is already in the correct format
            if isinstance(old_id, int) and mission_id_str:
                print(f"  Mission {old_id} already in correct format")
                continue
            
            # Extract the UUID part from the old ID
            if isinstance(old_id, str) and old_id.startswith("mission_"):
                # Extract UUID from "mission_<uuid>"
                uuid_part = old_id.replace("mission_", "")
                
                # Generate a new integer ID (simple increment)
                new_id = i + 1
                
                # Update the mission record
                update_sql = """
                UPDATE missions 
                SET id = :new_id, mission_id_str = :mission_id_str 
                WHERE id = :old_id
                """
                
                with engine.connect() as conn:
                    conn.execute(text(update_sql), {
                        "new_id": new_id,
                        "mission_id_str": old_id,  # Keep the original string as mission_id_str
                        "old_id": old_id
                    })
                    conn.commit()
                
                print(f"  Updated mission: {old_id} -> ID: {new_id}, mission_id_str: {old_id}")
            else:
                print(f"  Skipping mission {old_id} (unexpected format)")
        
        # Verify the fix
        print("\nVerifying data format...")
        with engine.connect() as conn:
            result = conn.execute(text("SELECT id, mission_id_str FROM missions LIMIT 5"))
            sample_missions = result.fetchall()
            
            for mission_id, mission_id_str in sample_missions:
                print(f"  ID: {mission_id} (type: {type(mission_id).__name__})")
                print(f"  mission_id_str: {mission_id_str} (type: {type(mission_id_str).__name__})")
        
        print("\nMission data format fix completed!")
        return True
        
    except Exception as e:
        print(f"Error fixing mission data: {e}")
        return False

def test_api_compatibility():
    """Test if the API can now handle the data"""
    print("\nTesting API compatibility...")
    
    try:
        import requests
        
        # Test the missions endpoint
        response = requests.get("http://localhost:8001/missions", timeout=10)
        
        if response.status_code == 200:
            print("✅ API is working correctly!")
            missions = response.json()
            print(f"Found {len(missions)} missions")
            
            # Show first mission structure
            if missions:
                first_mission = missions[0]
                print(f"Sample mission structure:")
                for key, value in first_mission.items():
                    print(f"  {key}: {value} (type: {type(value).__name__})")
        else:
            print(f"❌ API returned status {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ API test failed: {e}")

if __name__ == "__main__":
    print("Mission Data Format Fix Tool")
    print("=" * 50)
    
    if fix_mission_data():
        print("\nTesting API compatibility...")
        test_api_compatibility()
    else:
        print("\nMission data fix failed. Check the error messages above.") 