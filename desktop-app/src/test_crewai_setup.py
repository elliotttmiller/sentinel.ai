#!/usr/bin/env python3
"""Test script to verify our CrewAI implementation works"""

import sys
import traceback
import os

# Add the src directory to Python path to handle relative imports
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

def test_imports():
    """Test all our imports step by step"""
    try:
        print("🧪 Testing imports...")
        
        print("1. Testing tools import...")
        from tools.file_system_tools import ALL_TOOLS
        print(f"✅ Tools imported: {len(ALL_TOOLS)} tools available")
        
        print("2. Testing executable agents import (bypassing package)...")
        # Import directly from the file to avoid package import issues
        import importlib.util
        spec = importlib.util.spec_from_file_location("executable_agent", "agents/executable_agent.py")
        executable_agent_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(executable_agent_module)
        ExecutableAgents = executable_agent_module.ExecutableAgents
        print("✅ ExecutableAgents imported")
        
        print("3. Testing workflow import...")
        from core.execution_workflow import ExecutionWorkflow
        print("✅ ExecutionWorkflow imported")
        
        print("4. Testing real mission executor...")
        from core.real_mission_executor import RealMissionExecutor
        print("✅ RealMissionExecutor imported")
        
        print("5. Creating instances...")
        executor = RealMissionExecutor()
        print("✅ RealMissionExecutor instance created")
        
        agents = ExecutableAgents()
        print("✅ ExecutableAgents instance created")
        
        workflow = ExecutionWorkflow()
        print("✅ ExecutionWorkflow instance created")
        
        print("\n🎉 ALL TESTS PASSED!")
        print(f"- CrewAI available: {workflow.crewai_available}")
        print(f"- Agents available: {agents.crewai_available}")
        print(f"- Tools count: {len(ALL_TOOLS)}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_imports()
    sys.exit(0 if success else 1)
