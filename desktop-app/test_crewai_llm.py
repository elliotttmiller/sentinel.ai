#!/usr/bin/env python3
"""
Test script to verify CrewAI LLM configuration
Tests the fixed model name formatting for litellm compatibility
"""

import sys
import os
sys.path.append('src')

from loguru import logger
from src.utils.google_ai_wrapper import get_crewai_llm

def test_crewai_llm():
    """Test CrewAI LLM initialization and configuration"""
    logger.info("🧪 Testing CrewAI LLM initialization...")
    
    try:
        # Get the CrewAI LLM instance
        llm = get_crewai_llm()
        
        if llm is None:
            logger.error("❌ Failed: get_crewai_llm() returned None")
            return False
            
        logger.success("✅ CrewAI LLM instance created successfully")
        
        # Check the model name format
        model_name = getattr(llm, 'model', 'Unknown')
        logger.info(f"📋 Model name: {model_name}")
        
        # Check if it has the correct gemini/ prefix for litellm
        if model_name.startswith('gemini/'):
            logger.success(f"✅ Model name correctly formatted for litellm: {model_name}")
        else:
            logger.error(f"❌ Model name incorrectly formatted. Expected 'gemini/...' but got: {model_name}")
            return False
            
        # Try to access other properties
        try:
            temperature = getattr(llm, 'temperature', 'Unknown')
            logger.info(f"🌡️ Temperature: {temperature}")
        except Exception as e:
            logger.warning(f"⚠️ Could not access temperature: {e}")
            
        logger.success("🎉 CrewAI LLM test completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"❌ CrewAI LLM test failed: {e}")
        return False

if __name__ == "__main__":
    logger.info("🚀 Starting CrewAI LLM configuration test...")
    success = test_crewai_llm()
    
    if success:
        logger.success("✅ All tests passed! Real agent execution should work now.")
        exit(0)
    else:
        logger.error("❌ Tests failed. Check the configuration.")
        exit(1)
