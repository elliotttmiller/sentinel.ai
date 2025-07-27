#!/usr/bin/env python3
"""
ngrok Setup Script
Helps users configure their ngrok auth token for Sentinel services.
"""

import os
import json
import subprocess
import requests
from pathlib import Path
from typing import Optional, Tuple

def validate_ngrok_token(token: str) -> Tuple[bool, str]:
    """Validate ngrok auth token by making a test API call."""
    try:
        headers = {
            'Authorization': f'Bearer {token}',
            'Ngrok-Version': '2'
        }
        response = requests.get('https://api.ngrok.com/tunnels', headers=headers, timeout=10)
        
        if response.status_code == 200:
            return True, "Token is valid"
        elif response.status_code == 401:
            return False, "Token is invalid or expired"
        elif response.status_code == 403:
            return True, "Token is valid but lacks API permissions (fine for tunneling)"
        else:
            return False, f"API returned status {response.status_code}"
    except requests.exceptions.RequestException as e:
        return False, f"Network error: {str(e)}"
    except Exception as e:
        return False, f"Validation error: {str(e)}"

def test_ngrok_cli() -> bool:
    """Test if ngrok CLI is installed and working."""
    try:
        result = subprocess.run(['ngrok', 'version'], 
                              capture_output=True, text=True, timeout=5)
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False

def test_ngrok_auth(token: str) -> bool:
    """Test if ngrok auth token works with CLI."""
    try:
        # Set the auth token temporarily
        env = os.environ.copy()
        env['NGROK_AUTHTOKEN'] = token
        
        # Test with ngrok config command
        result = subprocess.run(['ngrok', 'config', 'check'], 
                              capture_output=True, text=True, timeout=10, env=env)
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False

def check_ngrok_installation() -> bool:
    """Check if ngrok is properly installed."""
    if not test_ngrok_cli():
        print("❌ ngrok CLI not found or not working!")
        print("📥 Please install ngrok from https://ngrok.com/download")
        print("💡 After installation, make sure 'ngrok' is in your PATH")
        return False
    return True

def get_current_token() -> Optional[str]:
    """Get current ngrok auth token from config or environment."""
    config_file = Path(__file__).parent / "service_config.json"
    
    # Try config file first
    if config_file.exists():
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
                token = config.get('ngrok_auth_token')
                if token and token != 'your-auth-token-here':
                    return token
        except:
            pass
    
    # Try environment variable
    return os.getenv('NGROK_AUTHTOKEN')

def save_token(token: str) -> bool:
    """Save ngrok auth token to config file and environment."""
    try:
        config_file = Path(__file__).parent / "service_config.json"
        config_file.parent.mkdir(exist_ok=True)
        
        # Load existing config or create new
        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    config = json.load(f)
            except:
                config = {}
        else:
            config = {}
        
        # Save token
        config['ngrok_auth_token'] = token
        
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
        
        # Set environment variable
        os.environ['NGROK_AUTHTOKEN'] = token
        
        return True
    except Exception as e:
        print(f"❌ Error saving token: {e}")
        return False

def refresh_token_interactive() -> Optional[str]:
    """Interactive token refresh process."""
    print("\n🔄 Token Refresh Required")
    print("="*40)
    print("Your ngrok auth token appears to be invalid or expired.")
    print("Let's get a new one!")
    print()
    print("📋 Steps to get a new auth token:")
    print("1. Go to https://ngrok.com/ and login")
    print("2. Visit https://dashboard.ngrok.com/get-started/your-authtoken")
    print("3. Copy your new auth token")
    print("="*40)
    
    while True:
        new_token = input("\n🔑 Enter your new ngrok auth token: ").strip()
        
        if not new_token:
            print("❌ No token provided. Please try again.")
            continue
        
        # Validate the new token
        print("🔍 Validating new token...")
        is_valid, message = validate_ngrok_token(new_token)
        
        if is_valid:
            print("✅ New token is valid!")
            return new_token
        else:
            print(f"❌ Token validation failed: {message}")
            retry = input("Try again? (y/N): ").lower()
            if retry != 'y':
                return None

def setup_ngrok_auth_token():
    """Interactive setup for ngrok auth token with validation and refresh."""
    print("\n" + "="*60)
    print("NGROK AUTH TOKEN SETUP")
    print("="*60)
    
    # Check ngrok installation
    if not check_ngrok_installation():
        return False
    
    # Check current token
    current_token = get_current_token()
    
    if current_token:
        print(f"\n🔍 Found existing auth token: {current_token[:10]}...")
        print("🔍 Validating current token...")
        
        is_valid, message = validate_ngrok_token(current_token)
        
        if is_valid:
            print("✅ Current token is valid!")
            change = input("Do you want to change it? (y/N): ").lower()
            if change != 'y':
                print("✅ Keeping existing valid token.")
                return True
        else:
            print(f"⚠️  Current token is invalid: {message}")
            print("🔄 Let's refresh your token...")
            
            new_token = refresh_token_interactive()
            if new_token:
                if save_token(new_token):
                    print("✅ New token saved successfully!")
                    return True
                else:
                    print("❌ Failed to save new token.")
                    return False
            else:
                print("❌ Token refresh cancelled.")
                return False
    else:
        print("\n🔑 No existing token found. Let's set one up!")
    
    # Get new token
    print("\n📋 Steps to get your ngrok auth token:")
    print("1. Go to https://ngrok.com/ and sign up/login")
    print("2. Go to https://dashboard.ngrok.com/get-started/your-authtoken")
    print("3. Copy your auth token (it looks like: 2abc123def456ghi789jkl...)")
    print("="*60)
    
    while True:
        auth_token = input("\n🔑 Enter your ngrok auth token: ").strip()
        
        if not auth_token:
            print("❌ No auth token provided. ngrok tunnels will not work.")
            return False
        
        # Validate the token
        print("🔍 Validating token...")
        is_valid, message = validate_ngrok_token(auth_token)
        
        if is_valid:
            print("✅ Token is valid!")
            
            # Also test with CLI
            print("🔍 Testing with ngrok CLI...")
            if test_ngrok_auth(auth_token):
                print("✅ Token works with ngrok CLI!")
            else:
                print("⚠️  Token validation passed but CLI test failed")
                print("💡 This might still work for tunneling")
            
            if save_token(auth_token):
                print("✅ ngrok auth token saved successfully!")
                print("📝 You can now use the service manager to start ngrok tunnels.")
                print("🚀 Run: python scripts/manage_services.py")
                return True
            else:
                print("❌ Failed to save token.")
                return False
        else:
            print(f"❌ Token validation failed: {message}")
            retry = input("Try again? (y/N): ").lower()
            if retry != 'y':
                return False

def main():
    """Main entry point."""
    try:
        success = setup_ngrok_auth_token()
        if success:
            print("\n🎉 Setup complete! You're ready to use ngrok tunnels.")
            print("\n💡 Next steps:")
            print("1. Run: python scripts/manage_services.py")
            print("2. Choose option 2 to start ngrok tunnels")
            print("3. Update your mobile app with the tunnel URLs")
        else:
            print("\n❌ Setup failed. Please try again.")
    except KeyboardInterrupt:
        print("\n\n👋 Setup cancelled.")
    except Exception as e:
        print(f"\n❌ Error during setup: {e}")

if __name__ == "__main__":
    main() 