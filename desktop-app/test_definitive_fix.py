"""
Test the definitive fix for CrewAI LLM model name formatting
"""
import sys
import os
sys.path.append('src')

from utils.google_ai_wrapper import get_crewai_llm

def test_crewai_llm_fix():
    print("🧪 Testing the definitive CrewAI LLM fix...")
    
    try:
        # Create the LLM instance
        llm = get_crewai_llm()
        if llm is None:
            print("❌ Failed to create LLM instance")
            return False
            
        print(f"✅ LLM created successfully")
        print(f"📋 LLM type: {type(llm)}")
        
        # Check the model attribute
        if hasattr(llm, 'model'):
            print(f"📋 Internal model attribute: {llm.model}")
        
        # Check string representation (this is what CrewAI uses)
        llm_str = str(llm)
        print(f"📋 String representation: {llm_str}")
        
        # Verify it has the correct format for litellm
        if "gemini/" in llm_str and not llm_str.startswith("models/"):
            print("✅ Model name is correctly formatted for litellm!")
            return True
        else:
            print(f"❌ Model name still has incorrect format: {llm_str}")
            return False
            
    except Exception as e:
        print(f"❌ Error during test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_crewai_llm_fix()
    print(f"\n🎯 Test result: {'SUCCESS' if success else 'FAILED'}")
