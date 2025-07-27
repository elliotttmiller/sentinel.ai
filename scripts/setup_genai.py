"""
Google GenAI Setup Script for Project Sentinel.

This script helps configure Google GenAI integration by setting up the API key.
"""

import os
import sys
from pathlib import Path


def setup_genai():
    """Setup Google GenAI integration."""
    print("🔧 Google GenAI Setup for Project Sentinel")
    print("=" * 50)
    
    # Check if API key is already set
    api_key = os.getenv("GOOGLE_API_KEY")
    if api_key:
        print("✅ Google API key is already configured!")
        print(f"   Key: {api_key[:10]}...{api_key[-4:]}")
        return True
    
    print("📝 To use Google GenAI features, you need to:")
    print("1. Get a Google API key from: https://makersuite.google.com/app/apikey")
    print("2. Set the API key in your environment")
    print()
    
    # Ask user for API key
    api_key = input("Enter your Google API key (or press Enter to skip): ").strip()
    
    if not api_key:
        print("⚠️  No API key provided. GenAI features will use fallback mode.")
        return False
    
    # Set the API key
    os.environ["GOOGLE_API_KEY"] = api_key
    
    # Try to save to .env file
    env_file = Path("backend/.env")
    if env_file.exists():
        try:
            with open(env_file, "a") as f:
                f.write(f"\nGOOGLE_API_KEY={api_key}\n")
            print("✅ API key saved to backend/.env")
        except Exception as e:
            print(f"⚠️  Could not save to .env file: {e}")
    else:
        print("⚠️  backend/.env file not found. Please add GOOGLE_API_KEY manually.")
    
    print("✅ Google GenAI setup completed!")
    return True


def test_genai():
    """Test GenAI integration."""
    print("\n🧪 Testing GenAI Integration...")
    
    try:
        # Import and test the client
        sys.path.append("backend")
        from core.genai_client import genai_client
        
        if genai_client.is_available():
            print("✅ GenAI client is available!")
            model_info = genai_client.get_model_info()
            print(f"   Model: {model_info['model_name']}")
            print(f"   Available: {model_info['available']}")
        else:
            print("❌ GenAI client is not available")
            print("   Please check your API key configuration")
            
    except Exception as e:
        print(f"❌ Error testing GenAI: {e}")


def main():
    """Main setup function."""
    print("🚀 Project Sentinel - Google GenAI Setup")
    print("=" * 50)
    
    # Setup GenAI
    success = setup_genai()
    
    if success:
        # Test the setup
        test_genai()
    
    print("\n📚 Next Steps:")
    print("1. Restart your backend server")
    print("2. Test with: curl http://localhost:8080/genai/status")
    print("3. Test agent with: curl http://localhost:8080/agents/test")
    print("\n🎯 Your agents will now use Google GenAI for intelligent responses!")


if __name__ == "__main__":
    main() 