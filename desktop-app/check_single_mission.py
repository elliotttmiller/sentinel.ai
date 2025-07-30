#!/usr/bin/env python3
"""
Check Single Mission
Check details of a specific mission
"""

import requests
import json

def check_mission(mission_id):
    """Check details of a specific mission"""
    try:
        response = requests.get(f"http://localhost:8001/mission/{mission_id}", timeout=10)
        if response.status_code == 200:
            mission = response.json()
            print(f"🔍 Mission: {mission_id}")
            print(f"📝 Title: {mission.get('title', 'N/A')}")
            print(f"📋 Status: {mission.get('status', 'N/A')}")
            print(f"🤖 Agent Type: {mission.get('agent_type', 'N/A')}")
            print(f"⏱️ Execution Time: {mission.get('execution_time', 'N/A')}s")
            
            # Show the prompt
            prompt = mission.get('prompt', 'N/A')
            print(f"🎯 Prompt: {prompt[:300]}{'...' if len(prompt) > 300 else ''}")
            
            # Show the result
            result = mission.get('result', 'N/A')
            print(f"📄 Result: {result[:1000]}{'...' if len(result) > 1000 else ''}")
            
            # Show error if any
            error = mission.get('error_message', 'N/A')
            if error != 'N/A':
                print(f"❌ Error: {error}")
            
            # Show the plan
            plan = mission.get('plan', {})
            if plan:
                steps = plan.get('steps', [])
                print(f"📋 Plan Steps: {len(steps)}")
                for i, step in enumerate(steps[:3], 1):
                    print(f"  {i}. {step.get('agent_role', 'N/A')}: {step.get('task_description', 'N/A')[:100]}...")
        else:
            print(f"❌ Failed to get mission: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    # Check the most recent mission
    check_mission("mission_56461d4a") 