#!/usr/bin/env python3
"""
Debug test to understand how ChatGoogleGenerativeAI handles different model name formats
"""

import os
import sys
sys.path.append('src')

from loguru import logger
from langchain_google_genai import ChatGoogleGenerativeAI

def test_model_name_formats():
    """Test different model name formats to see what ChatGoogleGenerativeAI does with them"""
    
    test_formats = [
        "gemini-1.5-pro",
        "gemini/gemini-1.5-pro", 
        "models/gemini-1.5-pro",
        "models/gemini/gemini-1.5-pro"
    ]
    
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        logger.error("GOOGLE_API_KEY not found in environment")
        return
    
    for model_format in test_formats:
        logger.info(f"🧪 Testing model format: '{model_format}'")
        try:
            llm = ChatGoogleGenerativeAI(
                model=model_format,
                google_api_key=api_key,
                temperature=0.7,
                convert_system_message_to_human=True
            )
            
            # Check what the model attribute contains
            actual_model = getattr(llm, 'model', 'unknown')
            logger.info(f"   📝 Internal model attribute: '{actual_model}'")
            
            # Check string representation
            str_repr = str(llm)
            logger.info(f"   🔤 String representation: '{str_repr}'")
            
            # Try to extract model from string representation
            if 'model=' in str_repr:
                model_part = str_repr.split('model=')[1].split(',')[0].strip("'\"")
                logger.info(f"   🎯 Extracted model from str(): '{model_part}'")
            
            logger.success(f"✅ Model format '{model_format}' accepted")
            
        except Exception as e:
            logger.error(f"❌ Model format '{model_format}' failed: {e}")
        
        logger.info("   " + "-" * 50)

if __name__ == "__main__":
    logger.info("🚀 Starting model name format debug test...")
    test_model_name_formats()
    logger.info("🏁 Debug test completed")
