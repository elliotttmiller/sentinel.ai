#!/usr/bin/env python3
"""
Research script to understand ChatGoogleGenerativeAI model name handling
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from langchain_google_genai import ChatGoogleGenerativeAI

def test_model_name_handling():
    print("🔍 Testing ChatGoogleGenerativeAI model name handling...")
    
    test_cases = [
        "gemini-1.5-pro",
        "gemini/gemini-1.5-pro", 
        "models/gemini-1.5-pro",
        "gemini-1.5-pro-latest"
    ]
    
    for test_model in test_cases:
        try:
            print(f"\n📝 Testing input: '{test_model}'")
            llm = ChatGoogleGenerativeAI(
                model=test_model,
                google_api_key=os.getenv("GOOGLE_API_KEY"),
                temperature=0.7
            )
            print(f"   Result: '{llm.model}'")
            
        except Exception as e:
            print(f"   Error: {e}")

if __name__ == "__main__":
    test_model_name_handling()
