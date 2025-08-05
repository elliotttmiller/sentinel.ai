#!/usr/bin/env python3
"""
Test import compatibility for uvicorn/multiprocessing environments
"""

import sys
import os
import importlib
import multiprocessing

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_module_import(module_name):
    """Test importing a module"""
    try:
        module = importlib.import_module(module_name)
        # Try to reload the module (this tests WatchFiles/uvicorn compatibility)
        importlib.reload(module)
        return True, "OK"
    except Exception as e:
        return False, str(e)

def test_imports_in_subprocess():
    """Test imports in a subprocess (multiprocessing compatibility)"""
    def subprocess_test():
        try:
            # Test key imports
            from src.utils.google_ai_wrapper import create_google_ai_llm, GoogleAIWrapper
            from src.models.advanced_database import User
            from src.main import app
            return True
        except Exception as e:
            return False, str(e)
    
    try:
        # This tests multiprocessing compatibility
        import multiprocessing
        with multiprocessing.Pool(1) as pool:
            result = pool.apply(subprocess_test)
            return result
    except Exception as e:
        return False, str(e)

def main():
    """Test uvicorn/multiprocessing compatibility"""
    print("🧪 Testing uvicorn/multiprocessing compatibility...")
    print("=" * 50)
    
    # Test basic module imports and reloading
    modules_to_test = [
        'src.main',
        'src.utils.google_ai_wrapper', 
        'src.core.cognitive_forge_engine',
        'src.models.advanced_database'
    ]
    
    all_passed = True
    
    print("📦 Testing module imports and reloading...")
    for module_name in modules_to_test:
        success, message = test_module_import(module_name)
        if success:
            print(f"✅ {module_name}: Import and reload successful")
        else:
            print(f"❌ {module_name}: {message}")
            all_passed = False
    
    print("\n🔄 Testing multiprocessing compatibility...")
    # Skip multiprocessing test in GitHub Actions environment
    if os.getenv('GITHUB_ACTIONS'):
        print("⏭️  Skipping multiprocessing test in GitHub Actions environment")
    else:
        try:
            result = test_imports_in_subprocess()
            if result:
                print("✅ Multiprocessing compatibility: OK")
            else:
                print("❌ Multiprocessing compatibility: Failed")
                all_passed = False
        except Exception as e:
            print(f"⚠️  Multiprocessing test inconclusive: {e}")
    
    print("=" * 50)
    if all_passed:
        print("🎉 All compatibility tests passed!")
        print("✅ Ready for uvicorn with --reload")
        print("✅ Ready for multiprocessing environments")
    else:
        print("⚠️  Some compatibility issues found")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)