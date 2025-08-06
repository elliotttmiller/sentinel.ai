#!/usr/bin/env python3
"""Test script to verify all imports work correctly"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    print("Testing execution workflow import...")
    from src.core.execution_workflow import ExecutionWorkflow
    print("✅ ExecutionWorkflow imported successfully")
    
    print("Testing real mission executor import...")
    from src.core.real_mission_executor import RealMissionExecutor
    print("✅ RealMissionExecutor imported successfully")
    
    print("Testing sandbox executor...")
    from src.core.sandbox_executor import SandboxExecutor
    print("✅ SandboxExecutor imported successfully")
    
    # Test initialization
    print("\nTesting initialization...")
    workflow = ExecutionWorkflow()
    print("✅ ExecutionWorkflow initialized successfully")
    
    executor = RealMissionExecutor()
    print("✅ RealMissionExecutor initialized successfully")
    
    print("\n🎉 All imports and initializations successful!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
