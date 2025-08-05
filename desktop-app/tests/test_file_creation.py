#!/usr/bin/env python3
"""
Test Real File Creation with CrewAI Integration
This script tests if the system can actually create files using the SandboxExecutor
and verifies that the CrewAI LLM is properly formatted.
"""

import os
import sys
from loguru import logger
from src.core.sandbox_executor import SandboxExecutor
from src.utils.google_ai_wrapper import get_crewai_llm

def test_file_creation():
    logger.info("="*60)
    logger.info(" 📁 REAL FILE CREATION TEST ".center(60, "="))
    logger.info("="*60)
    
    # Create a test sandbox executor
    sandbox = SandboxExecutor()
    
    # Get the workspace path
    workspace_dir = sandbox.get_workspace_path()
    logger.info(f"Workspace directory: {workspace_dir}")
    
    # Check if workspace exists
    if os.path.exists(workspace_dir):
        logger.info(f"✅ Workspace directory exists")
    else:
        logger.error(f"❌ Workspace directory does not exist")
        return
    
    # List current contents
    logger.info("\nCurrent workspace contents:")
    contents = os.listdir(workspace_dir)
    if contents:
        for item in contents:
            path = os.path.join(workspace_dir, item)
            if os.path.isdir(path):
                logger.info(f" - 📁 {item}/")
            else:
                logger.info(f" - 📄 {item} ({os.path.getsize(path)} bytes)")
    else:
        logger.info(" - (empty)")
    
    # Create a test file for litellm fix
    test_file = "litellm_fix_test.txt"
    test_content = """
This is a test file created by the SandboxExecutor on August 5, 2025.
This confirms that our file creation capability is working correctly
and validates that the model name formatting fix has been applied.
    """
    
    logger.info(f"\nAttempting to create file: {test_file}")
    result = sandbox.create_file(test_file, test_content)
    logger.info(f"Result: {result}")
    
    # Verify the file was created
    expected_path = os.path.join(workspace_dir, test_file)
    if os.path.exists(expected_path):
        logger.success(f"✅ File exists at: {expected_path}")
        with open(expected_path, 'r') as f:
            content = f.read()
        logger.info(f"Content: {content}")
        if test_content in content:
            logger.success("✅ Content matches expected")
        else:
            logger.error("❌ Content does not match expected")
    else:
        logger.error(f"❌ File does not exist at: {expected_path}")

def test_crewai_llm_format():
    """Test that the CrewAI LLM is properly formatted"""
    logger.info("="*60)
    logger.info(" 🤖 CREWAI LLM FORMAT TEST ".center(60, "="))
    logger.info("="*60)
    
    try:
        # Get the CrewAI LLM
        llm = get_crewai_llm()
        
        if llm is not None:
            logger.success("✅ Successfully created CrewAI LLM")
            # CrewAI LLM should have a model name that starts with "gemini/"
            model_name = llm.model
            logger.info(f"Model name: {model_name}")
            
            if model_name.startswith("gemini/"):
                logger.success(f"✅ Model name is correctly formatted: {model_name}")
            else:
                logger.error(f"❌ Model name is incorrectly formatted: {model_name}")
        else:
            logger.error("❌ Failed to create CrewAI LLM")
    except Exception as e:
        logger.error(f"❌ Error testing CrewAI LLM: {e}")

if __name__ == "__main__":
    # Run both tests
    test_file_creation()
    test_crewai_llm_format()
    
    logger.info("✨ Test completed")
