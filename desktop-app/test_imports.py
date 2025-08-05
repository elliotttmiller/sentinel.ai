#!/usr/bin/env python3
"""
Simple test script to validate import structure
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_import(module_path, description):
    """Test importing a module"""
    try:
        exec(f"import {module_path}")
        print(f"✅ {description}: {module_path}")
        return True
    except ImportError as e:
        print(f"❌ {description}: {module_path} - {e}")
        return False

def test_from_import(module_path, symbols, description):
    """Test importing specific symbols from a module"""
    try:
        exec(f"from {module_path} import {', '.join(symbols)}")
        print(f"✅ {description}: from {module_path} import {', '.join(symbols)}")
        return True
    except ImportError as e:
        print(f"❌ {description}: from {module_path} import {', '.join(symbols)} - {e}")
        return False

def main():
    print("🧪 Testing import structure...")
    print("=" * 50)
    
    # Test basic modules
    results = []
    
    # Test config
    results.append(test_import("src.config.settings", "Config settings"))
    
    # Test google_ai_wrapper exports
    results.append(test_from_import("src.utils.google_ai_wrapper", 
                                  ["create_google_ai_llm", "GoogleAIWrapper", "google_ai_wrapper", "direct_inference", "GoogleGenerativeAIWrapper"], 
                                  "Google AI Wrapper exports"))
    
    # Test database models
    results.append(test_from_import("src.models.advanced_database", ["User", "db_manager"], "Database models"))
    
    # Test main imports
    results.append(test_import("src.main", "Main application"))
    
    # Test cognitive forge engine
    results.append(test_import("src.core.cognitive_forge_engine", "Cognitive Forge Engine"))
    
    # Test agents
    results.append(test_import("src.agents.advanced_agents", "Advanced agents"))
    results.append(test_import("src.agents.specialized_agents", "Specialized agents"))
    
    print("=" * 50)
    passed = sum(results)
    total = len(results)
    print(f"📊 Results: {passed}/{total} imports successful")
    
    if passed == total:
        print("🎉 All imports working correctly!")
        return True
    else:
        print("⚠️  Some imports failed - see details above")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)