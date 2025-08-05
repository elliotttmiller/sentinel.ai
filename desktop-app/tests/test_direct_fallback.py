#!/usr/bin/env python3
"""
Test Direct File Creation
Tests the improved fallback implementation directly
"""

import os
import sys
# Add the parent directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.execution_workflow import ExecutionWorkflow
import asyncio

async def test_file_creation():
    """Test the improved fallback implementation"""
    print("="*60)
    print(" 📁 TESTING IMPROVED FALLBACK IMPLEMENTATION ".center(60, "="))
    print("="*60)
    
    # Create a workflow instance
    workflow = ExecutionWorkflow()
    
    # Create a mission request
    user_request = "Create a file named 'direct_test.txt' with the content 'This file was created by the improved fallback implementation.'"
    mission_context = {"mission_id": "test_mission_123"}
    
    print(f"Executing mission: {user_request}")
    
    # Execute the mission
    result = await workflow.execute_mission(user_request, mission_context)
    
    print(f"\nExecution result:")
    print(f"  Success: {result.get('success')}")
    print(f"  Message: {result.get('message')}")
    print(f"  Output: {result.get('execution_output')}")
    
    # Check if the file was created
    print("\nChecking if the file was created:")
    workspace_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "workspace")
    file_path = os.path.join(workspace_dir, "direct_test.txt")
    
    if os.path.exists(file_path):
        print(f"✅ Success! File exists at: {file_path}")
        with open(file_path, "r") as f:
            content = f.read()
        print(f"   Content: {content}")
    else:
        print(f"❌ File not found at: {file_path}")
        print("   Files in workspace:")
        try:
            for file in os.listdir(workspace_dir):
                print(f"   - {file}")
        except Exception as e:
            print(f"   Error listing workspace: {e}")

if __name__ == "__main__":
    asyncio.run(test_file_creation())
