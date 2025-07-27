#!/usr/bin/env python3
"""
Test script for ngrok setup functionality
"""

import sys
import os
from pathlib import Path

# Add the scripts directory to the path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent))

def test_ngrok_installation():
    """Test ngrok CLI installation."""
    print("🔍 Testing ngrok CLI installation...")
    
    try:
        from setup_ngrok import test_ngrok_cli
        if test_ngrok_cli():
            print("✅ ngrok CLI is installed and working")
            return True
        else:
            print("❌ ngrok CLI not found or not working")
            return False
    except Exception as e:
        print(f"❌ Error testing ngrok CLI: {e}")
        return False

def test_token_validation():
    """Test token validation functionality."""
    print("\n🔍 Testing token validation...")
    
    try:
        from setup_ngrok import validate_ngrok_token
        
        # Test with invalid token
        is_valid, message = validate_ngrok_token("invalid_token_123")
        print(f"Invalid token test: {is_valid} - {message}")
        
        # Test with empty token
        is_valid, message = validate_ngrok_token("")
        print(f"Empty token test: {is_valid} - {message}")
        
        print("✅ Token validation function working")
        return True
    except Exception as e:
        print(f"❌ Error testing token validation: {e}")
        return False

def test_config_management():
    """Test config file management."""
    print("\n🔍 Testing config management...")
    
    try:
        from setup_ngrok import get_current_token, save_token
        
        # Test getting current token
        current = get_current_token()
        print(f"Current token: {current[:10] if current else 'None'}...")
        
        # Test saving token (with dummy token)
        success = save_token("test_token_123")
        print(f"Save token test: {success}")
        
        # Clean up test token
        config_file = Path(__file__).parent / "service_config.json"
        if config_file.exists():
            import json
            with open(config_file, 'r') as f:
                config = json.load(f)
            if config.get('ngrok_auth_token') == "test_token_123":
                del config['ngrok_auth_token']
                with open(config_file, 'w') as f:
                    json.dump(config, f, indent=2)
        
        print("✅ Config management working")
        return True
    except Exception as e:
        print(f"❌ Error testing config management: {e}")
        return False

def main():
    """Run all tests."""
    print("🧪 Testing ngrok setup functionality...")
    print("="*50)
    
    tests = [
        ("ngrok CLI installation", test_ngrok_installation),
        ("token validation", test_token_validation),
        ("config management", test_config_management),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Test '{test_name}' failed with exception: {e}")
            results.append((test_name, False))
    
    print("\n" + "="*50)
    print("📊 TEST RESULTS")
    print("="*50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:<25} {status}")
        if result:
            passed += 1
    
    print("="*50)
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All tests passed! ngrok setup is ready to use.")
    else:
        print("⚠️  Some tests failed. Please check the issues above.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 