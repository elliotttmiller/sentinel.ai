#!/usr/bin/env python3
"""
Check Mission Results
Examine what the agents actually produced in their missions
"""

import requests
import json
from datetime import datetime

def check_mission_results():
    """Check the actual results of recent missions"""
    print("🔍 Checking Mission Results...")
    print("=" * 50)
    
    try:
        # Get all missions
        response = requests.get("http://localhost:8001/missions", timeout=10)
        if response.status_code != 200:
            print(f"❌ Failed to get missions: {response.status_code}")
            return
        
        missions = response.json()
        print(f"📊 Found {len(missions)} missions")
        
        # Get the most recent missions (last 4 from our tests)
        recent_missions = missions[-4:] if len(missions) >= 4 else missions
        
        for i, mission in enumerate(recent_missions, 1):
            mission_id = mission.get('mission_id_str', mission.get('id'))
            print(f"\n🔍 Mission {i}: {mission_id}")
            print("-" * 30)
            
            # Get detailed mission info
            mission_response = requests.get(f"http://localhost:8001/mission/{mission_id}", timeout=10)
            if mission_response.status_code == 200:
                mission_details = mission_response.json()
                
                print(f"📝 Title: {mission_details.get('title', 'N/A')}")
                print(f"📋 Status: {mission_details.get('status', 'N/A')}")
                print(f"🤖 Agent Type: {mission_details.get('agent_type', 'N/A')}")
                print(f"⏱️ Execution Time: {mission_details.get('execution_time', 'N/A')}s")
                
                # Show the prompt
                prompt = mission_details.get('prompt', 'N/A')
                print(f"🎯 Prompt: {prompt[:200]}{'...' if len(prompt) > 200 else ''}")
                
                # Show the result
                result = mission_details.get('result', 'N/A')
                print(f"📄 Result: {result[:500]}{'...' if len(result) > 500 else ''}")
                
                # Show the plan
                plan = mission_details.get('plan', {})
                if plan:
                    steps = plan.get('steps', [])
                    print(f"📋 Plan Steps: {len(steps)}")
                    for j, step in enumerate(steps[:3], 1):  # Show first 3 steps
                        print(f"  {j}. {step.get('agent_role', 'N/A')}: {step.get('task_description', 'N/A')[:100]}...")
                
                print()
            else:
                print(f"❌ Failed to get mission details: {mission_response.status_code}")
        
        # Check if any files were actually created
        print("🔍 Checking for Created Files...")
        print("-" * 30)
        
        import os
        desktop_path = os.path.expanduser("~/Desktop")
        if os.path.exists(desktop_path):
            desktop_files = os.listdir(desktop_path)
            sentinel_files = [f for f in desktop_files if 'sentinel' in f.lower()]
            if sentinel_files:
                print(f"✅ Found Sentinel files on desktop: {sentinel_files}")
            else:
                print("❌ No Sentinel files found on desktop")
        
        # Check current directory for generated files
        current_files = os.listdir('.')
        generated_files = [f for f in current_files if any(keyword in f.lower() for keyword in ['test', 'random', 'system', 'flask', 'requirements'])]
        if generated_files:
            print(f"✅ Found generated files in current directory: {generated_files}")
        else:
            print("❌ No generated files found in current directory")
            
    except Exception as e:
        print(f"❌ Error checking mission results: {e}")

if __name__ == "__main__":
    check_mission_results() 