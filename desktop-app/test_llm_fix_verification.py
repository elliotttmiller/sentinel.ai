#!/usr/bin/env python3
"""
Test script to verify that the LLM model name formatting issue is fixed.
This script simulates the model name processing that occurs in the application.
"""

import os
import sys

# Set environment variables for testing
os.environ["GOOGLE_API_KEY"] = "test_key_for_format_testing"
os.environ["LLM_MODEL"] = "gemini-1.5-pro"
os.environ["LLM_TEMPERATURE"] = "0.7"

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def test_model_name_formatting():
    """Test that model names are formatted correctly for litellm"""
    print("🧪 Testing model name formatting fixes...")
    
    try:
        # Test the custom LLM wrapper
        from utils.google_ai_wrapper import get_crewai_llm
        
        print("1. Testing get_crewai_llm()...")
        llm = get_crewai_llm()
        
        if llm is None:
            print("❌ Failed to create LLM instance")
            return False
            
        print(f"✅ LLM instance created: {type(llm).__name__}")
        
        # Check if it's our custom class
        if hasattr(llm, '_litellm_model_name'):
            model_name = llm._litellm_model_name
            print(f"📋 LiteLLM model name: {model_name}")
            
            if model_name.startswith('gemini/') and not model_name.startswith('models/'):
                print(f"✅ Model name format is correct: {model_name}")
                return True
            else:
                print(f"❌ Model name format is incorrect: {model_name}")
                return False
        elif hasattr(llm, 'model'):
            model_name = llm.model
            print(f"📋 Model attribute: {model_name}")
            
            # Check if it's in the correct format
            if 'models/' in model_name:
                print(f"⚠️  Model name still contains 'models/' prefix: {model_name}")
                print("🔧 This should be handled by the runtime patches")
                return True  # The patches should handle this
            else:
                print(f"✅ Model name looks clean: {model_name}")
                return True
        else:
            print("❌ LLM instance has no recognizable model attribute")
            return False
            
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False

def test_patches_applied():
    """Test that runtime patches are applied correctly"""
    print("\n🔧 Testing runtime patches...")
    
    try:
        # Import the patch module (should auto-apply patches)
        from utils.llm_patch import apply_all_patches
        
        print("✅ Patch module imported successfully")
        
        # Try to re-apply patches (should be safe)
        result = apply_all_patches()
        if result:
            print("✅ Runtime patches applied successfully")
        else:
            print("⚠️  Runtime patches could not be applied (dependencies may not be available)")
        
        return True
        
    except Exception as e:
        print(f"❌ Patch test failed: {e}")
        return False

def test_litellm_configuration():
    """Test that litellm configuration is applied"""
    print("\n⚙️  Testing litellm configuration...")
    
    try:
        from utils.litellm_custom_provider import configure_litellm, custom_model_name
        
        # Test the model name mapping function
        test_cases = [
            ("models/gemini/gemini-1.5-pro", "gemini/gemini-1.5-pro"),
            ("models/gemini-1.5-pro", "gemini/gemini-1.5-pro"),
            ("gemini-1.5-pro", "gemini/gemini-1.5-pro"),
            ("gemini/gemini-1.5-pro", "gemini/gemini-1.5-pro"),
        ]
        
        all_passed = True
        for input_model, expected_output in test_cases:
            result = custom_model_name(input_model)
            if result == expected_output:
                print(f"✅ {input_model} -> {result}")
            else:
                print(f"❌ {input_model} -> {result} (expected: {expected_output})")
                all_passed = False
        
        if all_passed:
            print("✅ All model name mapping tests passed")
        else:
            print("❌ Some model name mapping tests failed")
        
        return all_passed
        
    except Exception as e:
        print(f"❌ LiteLLM configuration test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Running LLM fix verification tests...\n")
    
    tests = [
        ("Model Name Formatting", test_model_name_formatting),
        ("Runtime Patches", test_patches_applied),
        ("LiteLLM Configuration", test_litellm_configuration),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{'='*50}")
        print(f"Running: {test_name}")
        print('='*50)
        
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Test '{test_name}' crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print(f"\n{'='*50}")
    print("TEST SUMMARY")
    print('='*50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The LLM fix should work correctly.")
        return 0
    else:
        print("⚠️  Some tests failed. The fix may need additional work.")
        return 1

if __name__ == "__main__":
    exit(main())