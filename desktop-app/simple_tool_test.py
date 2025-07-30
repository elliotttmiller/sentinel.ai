#!/usr/bin/env python3
"""
Simple Tool Test
Test the tools directly without CrewAI
"""

import os
import sys

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.tools.crewai_tools import (
    write_file_tool, read_file_tool, list_files_tool, 
    execute_shell_command_tool, analyze_python_file_tool
)

def test_tools():
    """Test each tool individually"""
    print("🧪 Testing Tools Individually...")
    
    try:
        # Test 1: Write File Tool
        print("\n1️⃣ Testing Write File Tool...")
        result = write_file_tool._run("test_output.txt", "Hello from CrewAI Tools!")
        print(f"Result: {result}")
        
        # Test 2: Read File Tool
        print("\n2️⃣ Testing Read File Tool...")
        result = read_file_tool._run("test_output.txt")
        print(f"Result: {result}")
        
        # Test 3: List Files Tool
        print("\n3️⃣ Testing List Files Tool...")
        result = list_files_tool._run(".")
        print(f"Result: {result}")
        
        # Test 4: Execute Shell Command Tool
        print("\n4️⃣ Testing Execute Shell Command Tool...")
        result = execute_shell_command_tool._run("echo 'Hello from shell command'")
        print(f"Result: {result}")
        
        # Test 5: Analyze Python File Tool
        print("\n5️⃣ Testing Analyze Python File Tool...")
        result = analyze_python_file_tool._run("simple_tool_test.py")
        print(f"Result: {result}")
        
        # Clean up
        if os.path.exists("test_output.txt"):
            os.remove("test_output.txt")
            print("\n🧹 Cleaned up test file")
        
        print("\n✅ All tools tested successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error testing tools: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🧪 Simple Tool Test")
    print("=" * 50)
    
    if test_tools():
        print("\n✅ Tool test completed successfully!")
    else:
        print("\n❌ Tool test failed!") 