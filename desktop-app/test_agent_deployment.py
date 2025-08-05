"""
Agent Deployment Test Script
Tests if Sentinel AI agents actually create real files and perform tasks
"""

import requests
import time
import os
import json
from pathlib import Path

def test_agent_deployment():
    """Test that agents actually create real files"""
    print("🧪 Testing Sentinel AI Agent Deployment")
    print("=" * 50)
    
    # Test mission data
    mission_data = {
        "prompt": "Create a test file called agent_test.txt with the content 'Agent deployment successful! This file was created by Sentinel AI.'",
        "agent_type": "developer",
        "priority": "high"
    }
    
    print("📝 Creating test mission...")
    try:
        # Create mission
        response = requests.post(
            "http://localhost:8001/api/missions",
            json=mission_data,
            timeout=10
        )
        
        if response.status_code == 200:
            mission_info = response.json()
            mission_id = mission_info.get("mission", {}).get("mission_id_str")
            print(f"✅ Mission created: {mission_id}")
            
            # Wait for mission to complete
            print("⏳ Waiting for agent to complete mission...")
            for i in range(30):  # Wait up to 30 seconds
                time.sleep(1)
                print(f"   Checking... ({i+1}/30)")
                
                # Check for workspace files
                workspace_path = Path(f"sentinel_workspace/mission_{mission_id}")
                if workspace_path.exists():
                    print(f"📁 Workspace found: {workspace_path}")
                    
                    # List all files in the workspace
                    files = list(workspace_path.rglob("*"))
                    if files:
                        print("🎉 AGENT DEPLOYMENT SUCCESSFUL!")
                        print("📄 Files created by the agent:")
                        for file in files:
                            if file.is_file():
                                print(f"   - {file}")
                                # Read file content if it's the test file
                                if file.name == "agent_test.txt":
                                    with open(file, 'r') as f:
                                        content = f.read()
                                        print(f"   📖 Content: {content}")
                        return True
                
            print("⚠️  No files found after 30 seconds")
            
            # Check if workspace directory exists at all
            workspace_dir = Path("sentinel_workspace")
            if workspace_dir.exists():
                print(f"📁 Workspace directory exists: {workspace_dir}")
                all_missions = list(workspace_dir.glob("mission_*"))
                print(f"🔍 Found {len(all_missions)} mission directories:")
                for mission_dir in all_missions:
                    print(f"   - {mission_dir}")
                    files = list(mission_dir.rglob("*"))
                    if files:
                        print(f"     Files: {[f.name for f in files if f.is_file()]}")
            else:
                print("❌ No workspace directory found")
            
            return False
            
        else:
            print(f"❌ Failed to create mission: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing agent deployment: {e}")
        return False

def check_current_workspace():
    """Check what's currently in the workspace"""
    print("\n🔍 Checking current workspace...")
    workspace_dir = Path("sentinel_workspace")
    
    if workspace_dir.exists():
        print(f"📁 Workspace exists: {workspace_dir}")
        missions = list(workspace_dir.glob("mission_*"))
        print(f"Found {len(missions)} mission directories:")
        
        for mission_dir in missions:
            print(f"\n📂 {mission_dir.name}:")
            files = list(mission_dir.rglob("*"))
            for file in files:
                if file.is_file():
                    print(f"   📄 {file.relative_to(mission_dir)} ({file.stat().st_size} bytes)")
    else:
        print("❌ No workspace directory found")

if __name__ == "__main__":
    # First check existing workspace
    check_current_workspace()
    
    # Then test new deployment
    success = test_agent_deployment()
    
    if success:
        print("\n🎉 CONCLUSION: Agents are successfully deployed and creating real files!")
    else:
        print("\n❌ CONCLUSION: Agents may not be creating real files. Check configuration.")
