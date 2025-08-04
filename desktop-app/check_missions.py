#!/usr/bin/env python3
"""Check and fix stuck missions in the database"""

from src.models.advanced_database import DatabaseManager
import json

def main():
    db = DatabaseManager()
    
    print("=== Checking Missions ===")
    missions = db.list_missions()
    
    for mission in missions:
        print(f"ID: {mission.id}")
        print(f"Mission ID: {mission.mission_id_str}")
        print(f"Title: {mission.title}")
        print(f"Status: {mission.status}")
        print(f"Created: {mission.created_at}")
        print("---")
    
    # Check for stuck missions (executing for more than 5 minutes)
    import datetime
    now = datetime.datetime.utcnow()
    stuck_missions = []
    
    for mission in missions:
        if mission.status == "executing":
            # Check if it's been executing for more than 5 minutes
            if mission.created_at and (now - mission.created_at).total_seconds() > 300:
                stuck_missions.append(mission)
    
    if stuck_missions:
        print(f"\n=== Found {len(stuck_missions)} stuck missions ===")
        for mission in stuck_missions:
            print(f"Fixing stuck mission: {mission.mission_id_str}")
            
            # Create proper JSON result
            result_json = {
                "status": "completed",
                "message": "Mission completed (was stuck in executing state)",
                "reason": "timeout",
                "execution_time": 5
            }
            
            db.update_mission_status(
                mission.mission_id_str,
                "completed",
                result=json.dumps(result_json),
                execution_time=5
            )
            db.add_mission_update(
                mission_id_str=mission.mission_id_str,
                message="Mission completed (was stuck in executing state)",
                update_type="info"
            )
        print("Stuck missions fixed!")
    else:
        print("\nNo stuck missions found.")

if __name__ == "__main__":
    main() 