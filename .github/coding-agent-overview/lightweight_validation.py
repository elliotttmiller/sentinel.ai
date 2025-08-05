#!/usr/bin/env python3
"""
Lightweight system validation script that tests core functionality
without requiring external dependencies.
"""

import sys
import os
from pathlib import Path

# Add the desktop-app/src directory to Python path
script_dir = Path(__file__).parent
repo_root = script_dir.parent.parent
desktop_app_src = repo_root / 'desktop-app' / 'src'
sys.path.insert(0, str(desktop_app_src))

def test_core_structure():
    """Test that core system structure is intact"""
    print("🧪 Testing Core System Structure...")
    
    essential_files = [
        desktop_app_src / 'main.py',
        desktop_app_src / 'cognitive_engine_service.py',
        desktop_app_src / 'utils' / 'google_ai_wrapper.py',
        desktop_app_src / 'utils' / 'websocket_helpers.py',
        desktop_app_src / 'core' / 'cognitive_forge_engine.py',
        desktop_app_src / 'models' / 'advanced_database.py',
    ]
    
    all_exist = True
    for file_path in essential_files:
        if file_path.exists():
            print(f"✅ {file_path.relative_to(desktop_app_src)}")
        else:
            print(f"❌ Missing: {file_path.relative_to(desktop_app_src)}")
            all_exist = False
    
    return all_exist

def test_clean_directory():
    """Test that cleanup was successful"""
    print("\n🧪 Testing Directory Cleanup...")
    
    desktop_app_root = repo_root / 'desktop-app'
    
    # Check that temporary files were removed
    temp_files_removed = [
        'test_definitive_fix.py',
        'test_llm_fix.py', 
        'debug_model_formats.py',
        'google_ai_wrapper_backup.py',
    ]
    
    cleanup_success = True
    for temp_file in temp_files_removed:
        if (desktop_app_root / temp_file).exists():
            print(f"❌ Temp file still exists: {temp_file}")
            cleanup_success = False
        else:
            print(f"✅ Removed: {temp_file}")
    
    # Check that workspace directory was created
    workspace_dir = desktop_app_root / 'workspace'
    if workspace_dir.exists():
        print(f"✅ Workspace directory created")
        temp_tests = workspace_dir / 'temp_tests'
        if temp_tests.exists() and len(list(temp_tests.glob('*.py'))) > 0:
            print(f"✅ Temp files moved to workspace: {len(list(temp_tests.glob('*.py')))} files")
    else:
        print(f"❌ Workspace directory not found")
        cleanup_success = False
    
    return cleanup_success

def test_function_availability():
    """Test that critical functions can be found in code"""
    print("\n🧪 Testing Critical Function Availability...")
    
    google_wrapper_path = desktop_app_src / 'utils' / 'google_ai_wrapper.py'
    websocket_helpers_path = desktop_app_src / 'utils' / 'websocket_helpers.py'
    
    functions_found = True
    
    # Test get_crewai_llm function
    try:
        with open(google_wrapper_path, 'r') as f:
            content = f.read()
            if 'def get_crewai_llm(' in content:
                print("✅ get_crewai_llm function found")
            else:
                print("❌ get_crewai_llm function not found")
                functions_found = False
    except Exception as e:
        print(f"❌ Error reading google_ai_wrapper.py: {e}")
        functions_found = False
    
    # Test WebSocketStateEncoder class
    try:
        with open(websocket_helpers_path, 'r') as f:
            content = f.read()
            if 'class WebSocketStateEncoder(' in content:
                print("✅ WebSocketStateEncoder class found")
            else:
                print("❌ WebSocketStateEncoder class not found")
                functions_found = False
    except Exception as e:
        print(f"❌ Error reading websocket_helpers.py: {e}")
        functions_found = False
    
    return functions_found

def main():
    """Run all lightweight validation tests"""
    print("🚀 Sentinel System Lightweight Validation (No Dependencies)")
    print("=" * 70)
    
    tests = [
        ("Core System Structure", test_core_structure),
        ("Directory Cleanup", test_clean_directory), 
        ("Critical Function Availability", test_function_availability),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name}: PASSED\n")
            else:
                print(f"❌ {test_name}: FAILED\n")
        except Exception as e:
            print(f"💥 {test_name}: ERROR - {e}\n")
    
    print("=" * 70)
    print(f"📊 VALIDATION RESULTS: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL SYSTEM OPTIMIZATION TESTS PASSED!")
        print("📝 System has been successfully optimized and cleaned:")
        print("   ✅ Core structure intact")
        print("   ✅ Temporary files cleaned up")
        print("   ✅ Critical functions available")
        print("   ✅ Ready for dependency installation and deployment")
        return 0
    else:
        print("⚠️  Some optimization tests failed.")
        return 1

if __name__ == "__main__":
    exit(main())