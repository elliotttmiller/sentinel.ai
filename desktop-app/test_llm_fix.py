"""
Test the LLM configuration fix
"""
import sys
import os
sys.path.append('src')

from utils.google_ai_wrapper import get_crewai_llm

def test_llm_configuration():
    print("Testing CrewAI LLM configuration...")
    
    # Get the LLM instance
    llm = get_crewai_llm()
    
    if llm is None:
        print("❌ Failed to create LLM instance")
        return False
        
    print(f"✅ LLM instance created successfully")
    print(f"Model name: {getattr(llm, 'model', 'Unknown')}")
    print(f"LLM string representation: {str(llm)}")
    
    # Check if the model name has the correct format
    model_str = str(llm)
    if model_str.startswith("gemini/"):
        print("✅ Model name has correct format for LiteLLM")
        return True
    else:
        print(f"❌ Model name format incorrect: {model_str}")
        return False

if __name__ == "__main__":
    success = test_llm_configuration()
    if success:
        print("\n🎉 LLM configuration test PASSED!")
    else:
        print("\n💥 LLM configuration test FAILED!")
