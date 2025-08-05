#!/usr/bin/env python3
"""
Test script to verify CrewAI LLM fix
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.utils.google_ai_wrapper import get_crewai_llm

def test_crewai_llm():
    print("🧪 Testing CrewAI LLM configuration...")
    
    try:
        llm = get_crewai_llm()
        if llm is None:
            print("❌ Failed to create CrewAI LLM")
            return False
            
        print(f"✅ CrewAI LLM created successfully")
        
        # Check available attributes
        print(f"📝 Available attributes: {[attr for attr in dir(llm) if not attr.startswith('_')]}")
        
        # Try to get model name from different possible attributes
        model_name = None
        for attr in ['model_name', 'model', 'model_id']:
            if hasattr(llm, attr):
                model_name = getattr(llm, attr)
                print(f"📝 {attr}: {model_name}")
                break
        
        if model_name:
            # Check if the model name is in the correct format for litellm
            if model_name.startswith("models/"):
                print(f"⚠️  Model name still has 'models/' prefix: {model_name}")
                print("This may cause litellm compatibility issues")
            else:
                print(f"✅ Model name format looks correct for litellm: {model_name}")
        else:
            print("⚠️  Could not find model name attribute")
            
        return True
        
    except Exception as e:
        print(f"❌ Error testing CrewAI LLM: {e}")
        return False

if __name__ == "__main__":
    success = test_crewai_llm()
    if success:
        print("🚀 Test completed successfully!")
    else:
        print("💥 Test failed!")
