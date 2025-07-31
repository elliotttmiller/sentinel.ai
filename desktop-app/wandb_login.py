#!/usr/bin/env python3
"""
WandB Login Script for Cognitive Forge System
Automatically logs into WandB with the provided API key
"""

import os
import subprocess
import sys

def wandb_login_with_key(api_key: str):
    """Login to WandB using the provided API key"""
    print("🔐 Logging into WandB...")
    print("="*50)
    
    try:
        # Set the API key as an environment variable
        os.environ["WANDB_API_KEY"] = api_key
        
        # Run wandb login with the API key
        result = subprocess.run(
            ["wandb", "login", api_key],
            capture_output=True,
            text=True,
            check=True
        )
        
        print("✅ WandB login successful!")
        print("   API Key configured and ready to use")
        print("   You can now use Weave observability features")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ WandB login failed: {e}")
        print(f"   Error output: {e.stderr}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_weave_after_login():
    """Test Weave functionality after WandB login"""
    print("\n🧪 Testing Weave after WandB login...")
    print("="*50)
    
    try:
        import weave
        import wandb
        
        print("✅ Weave and WandB imported successfully")
        
        # Test Weave initialization
        weave.init('cognitive-forge-v5')
        print("✅ Weave initialized successfully")
        
        # Test WandB connection
        if wandb.run is None:
            print("✅ WandB ready for new runs")
        else:
            print("✅ WandB run already active")
        
        return True
        
    except Exception as e:
        print(f"❌ Weave/WandB test failed: {e}")
        return False

def main():
    """Main function to handle WandB login"""
    print("🚀 WANDB LOGIN FOR COGNITIVE FORGE v5.0")
    print("="*50)
    
    # Your API key
    api_key = "29935489e31e251ab182e648ff7c9905ba6a5d79"
    
    print(f"🔑 Using API Key: {api_key[:8]}...{api_key[-4:]}")
    print()
    
    # Step 1: Login to WandB
    login_success = wandb_login_with_key(api_key)
    
    if not login_success:
        print("❌ Failed to login to WandB")
        return False
    
    # Step 2: Test Weave functionality
    weave_success = test_weave_after_login()
    
    if not weave_success:
        print("❌ Weave test failed after login")
        return False
    
    # Success summary
    print("\n" + "="*50)
    print("🎉 WANDB LOGIN SUCCESSFUL!")
    print("="*50)
    print("✅ WandB authenticated successfully")
    print("✅ Weave observability ready")
    print("✅ Your Cognitive Forge system is now fully integrated")
    print()
    print("🚀 You can now:")
    print("   • Run missions with full observability")
    print("   • View traces in the WandB dashboard")
    print("   • Monitor system performance")
    print("   • Track AI agent interactions")
    print()
    print("💡 Next: Run 'python test_weave_integration.py' to verify everything works")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 