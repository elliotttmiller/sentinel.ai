#!/usr/bin/env python
"""
Test the real agent execution with the fixed LLM configuration
This will execute a simple mission to create a file in the workspace
"""

import sys
import os
from pathlib import Path
import asyncio

# Add the src directory to the path so we can import from there
sys.path.append(os.path.join(os.path.dirname(__file__), 'desktop-app'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'desktop-app/src'))

try:
    from src.core.execution_workflow import ExecutionWorkflow
    print("✅ Successfully imported ExecutionWorkflow")
except ImportError as e:
    print(f"❌ Failed to import ExecutionWorkflow: {e}")
    sys.exit(1)

# Test mission request
mission_request = """
Create a file called litellm_fix_test.txt in the workspace directory
with the content: 'This file was created by a real CrewAI agent with proper LiteLLM configuration'
"""

async def run_test():
    try:
        # Create the execution workflow
        workflow = ExecutionWorkflow()
        print("✅ Successfully created ExecutionWorkflow instance")
        
        # Set a test mission ID for observability
        workflow.set_mission_context("litellm-fix-test")
        
        # Execute the mission
        print(f"🚀 Executing test mission: {mission_request}")
        result = await workflow.execute_mission(mission_request)
        
        # Check the result
        if result.get("success", False):
            print("✅ Mission executed successfully!")
            print(f"Result message: {result.get('message', '')}")
        else:
            print(f"❌ Mission failed: {result.get('error', 'Unknown error')}")
        
        # Check if the file was actually created
        test_file_path = Path("desktop-app/workspace/litellm_fix_test.txt")
        if test_file_path.exists():
            print(f"✅ File successfully created at: {test_file_path}")
            print(f"File content: {test_file_path.read_text()}")
        else:
            print(f"❌ File not found at: {test_file_path}")
        
        return result
    except Exception as e:
        print(f"❌ Test execution failed: {e}")
        return {"success": False, "error": str(e)}

if __name__ == "__main__":
    print("🧪 Starting CrewAI real agent execution test...")
    result = asyncio.run(run_test())
    
    print("\n=== Test Complete ===")
    if result.get("success", False):
        print("✅ Test PASSED: Real agent execution is working!")
        sys.exit(0)
    else:
        print("❌ Test FAILED: Real agent execution is not working!")
        sys.exit(1)
