#!/usr/bin/env python3
"""
Direct demonstration of the improved fallback implementation
"""

import asyncio
import sys
import os
import time
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.core.execution_workflow import ExecutionWorkflow
from src.core.real_mission_executor import RealMissionExecutor

async def demonstrate_file_creation():
    """Demonstrate file creation using the improved fallback system"""
    print("="*60)
    print(" 🚀 DEMONSTRATING FILE CREATION ".center(60, "="))
    print("="*60)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Create an executor
    executor = RealMissionExecutor()
    
    # Define a mission
    mission_id = f"demo_{int(time.time())}"
    mission_data = {
        "id": mission_id,
        "objective": "Create a file named 'demo_success.txt' with the content 'This file was created by the improved fallback implementation'",
        "agent_type": "developer",
        "complexity": "simple"
    }
    
    print(f"Mission: {mission_data['objective']}")
    
    try:
        # Execute the mission
        print("\nExecuting mission...")
        result = await executor.execute_mission(mission_data)
        
        print(f"\nExecution complete!")
        print(f"  Success: {result.get('success')}")
        print(f"  Message: {result.get('message')}")
        
        # Check if file was created
        workspace_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "workspace")
        file_path = os.path.join(workspace_dir, "demo_success.txt")
        
        print("\nChecking for created file...")
        if os.path.exists(file_path):
            print(f"✅ File successfully created: {file_path}")
            with open(file_path, 'r') as f:
                content = f.read()
            print(f"   Content: {content}")
        else:
            print(f"❌ File not found at: {file_path}")
            print("   Files in workspace:")
            for file in os.listdir(workspace_dir):
                print(f"   - {file}")
                
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(demonstrate_file_creation())
