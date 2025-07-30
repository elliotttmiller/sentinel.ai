#!/usr/bin/env python3
"""
Debug Mission Data
Check the actual structure of mission data from the API
"""

import requests
import json

def debug_mission_data():
    """Debug the mission data structure"""
    print("🔍 Debugging Mission Data Structure...")
    
    try:
        # Get all missions
        print("\n1️⃣ Getting all missions...")
        response = requests.get("http://localhost:8001/missions", timeout=10)
        if response.status_code == 200:
            missions = response.json()
            print(f"✅ Found {len(missions)} missions")
            
            if missions:
                # Show the structure of the first mission
                first_mission = missions[0]
                print(f"\n📋 First Mission Structure:")
                print(json.dumps(first_mission, indent=2, default=str))
                
                # Get detailed mission info
                mission_id = first_mission.get('mission_id_str', first_mission.get('id'))
                print(f"\n2️⃣ Getting detailed info for mission: {mission_id}")
                
                response = requests.get(f"http://localhost:8001/mission/{mission_id}", timeout=10)
                if response.status_code == 200:
                    mission_details = response.json()
                    print(f"\n📋 Detailed Mission Structure:")
                    print(json.dumps(mission_details, indent=2, default=str))
                    
                    # Check specific fields
                    print(f"\n🔍 Key Field Check:")
                    print(f"   mission_id_str: {mission_details.get('mission_id_str')}")
                    print(f"   id: {mission_details.get('id')}")
                    print(f"   title: {mission_details.get('title')}")
                    print(f"   status: {mission_details.get('status')}")
                    print(f"   agent_type: {mission_details.get('agent_type')}")
                    print(f"   prompt: {mission_details.get('prompt', 'N/A')[:100]}...")
                    print(f"   result: {mission_details.get('result', 'N/A')[:100]}...")
                    print(f"   plan: {type(mission_details.get('plan'))}")
                    if mission_details.get('plan'):
                        print(f"   plan keys: {list(mission_details.get('plan').keys())}")
                        if 'steps' in mission_details.get('plan', {}):
                            print(f"   plan steps count: {len(mission_details.get('plan', {}).get('steps', []))}")
                    
                else:
                    print(f"❌ Failed to get mission details: {response.status_code}")
                    print(f"Response: {response.text}")
            else:
                print("❌ No missions found")
        else:
            print(f"❌ Failed to get missions: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error debugging mission data: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_mission_data() 