#!/usr/bin/env python3
"""
Simple test script to validate import structure (without external dependencies)
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_basic_structure():
    """Test basic module structure without external dependencies"""
    print("🧪 Testing basic module structure...")
    
    # Test google_ai_wrapper structure (just checking valid exports exist)
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("google_ai_wrapper", 
                                                      "src/utils/google_ai_wrapper.py")
        module = importlib.util.module_from_spec(spec)
        
        # Check if the file contains the required exports
        with open("src/utils/google_ai_wrapper.py", "r") as f:
            content = f.read()
            
        required_exports = [
            "create_google_ai_llm",
            "GoogleAIWrapper", 
            "google_ai_wrapper",
            "direct_inference",
            "GoogleGenerativeAIWrapper"
        ]
        
        all_found = True
        for export in required_exports:
            if f"def {export}" in content or f"class {export}" in content or f"{export} =" in content:
                print(f"✅ Found export: {export}")
            else:
                print(f"❌ Missing export: {export}")
                all_found = False
                
        return all_found
        
    except Exception as e:
        print(f"❌ Error checking google_ai_wrapper structure: {e}")
        return False

def test_import_paths():
    """Test that import paths are correctly structured"""
    print("\n🔍 Testing import path structure...")
    
    # Read files and check import patterns
    files_to_check = [
        "src/main.py",
        "src/core/cognitive_forge_engine.py", 
        "src/agents/advanced_agents.py",
        "src/agents/specialized_agents.py",
        "src/utils/fix_ai.py"
    ]
    
    issues_found = []
    
    for file_path in files_to_check:
        try:
            with open(file_path, "r") as f:
                content = f.read()
                
            # Check for problematic patterns
            if "from ..utils" in content:
                issues_found.append(f"{file_path}: Contains relative imports with '..'")
            if "from .google_ai_wrapper import llm" in content:
                issues_found.append(f"{file_path}: Attempts to import 'llm' symbol")
            if "import llm" in content and "# Import" not in content:
                issues_found.append(f"{file_path}: Contains direct 'llm' import")
                
            print(f"✅ Checked: {file_path}")
            
        except Exception as e:
            issues_found.append(f"{file_path}: Could not read file - {e}")
    
    if issues_found:
        print("\n❌ Import issues found:")
        for issue in issues_found:
            print(f"  - {issue}")
        return False
    else:
        print("\n✅ No import issues found")
        return True

def test_fallback_classes():
    """Test that fallback classes are properly defined"""
    print("\n🛡️  Testing fallback class structure...")
    
    # Check that main.py has fallback User class
    try:
        with open("src/main.py", "r") as f:
            main_content = f.read()
            
        if "class User:" in main_content:
            print("✅ Fallback User class found in main.py")
            return True
        else:
            print("❌ Fallback User class missing in main.py")
            return False
            
    except Exception as e:
        print(f"❌ Error checking fallback classes: {e}")
        return False

def main():
    print("🧪 Testing desktop-app import structure (dependency-free)...")
    print("=" * 60)
    
    results = []
    
    # Run tests
    results.append(test_basic_structure())
    results.append(test_import_paths())
    results.append(test_fallback_classes())
    
    print("=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"📊 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All import structure tests passed!")
        return True
    else:
        print("⚠️  Some tests failed - see details above")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)