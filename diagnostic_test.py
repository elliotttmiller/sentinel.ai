#!/usr/bin/env python
"""
Diagnostic test for Google AI LLM wrapper with CrewAI
This will test the model name formatting and LLM creation directly
"""

import os
import sys
from pathlib import Path

# Add the src directory to the path so we can import from there
sys.path.append(os.path.join(os.path.dirname(__file__), 'desktop-app'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'desktop-app/src'))

from loguru import logger

# Import our wrapper
try:
    from src.utils.google_ai_wrapper import get_crewai_llm
    print("✅ Successfully imported get_crewai_llm")
except ImportError as e:
    print(f"❌ Failed to import get_crewai_llm: {e}")
    sys.exit(1)

# Try to create a file directly using the sandbox
try:
    from src.core.sandbox_executor import SandboxExecutor
    print("✅ Successfully imported SandboxExecutor")
    
    # Create a sandbox executor
    sandbox = SandboxExecutor()
    print(f"✅ Successfully created SandboxExecutor with workspace: {sandbox.workspace_dir}")
    
    # Create a test file
    test_file = "direct_test.txt"
    test_content = "This file was created directly by the SandboxExecutor"
    result = sandbox.create_file(test_file, test_content)
    print(f"File creation result: {result}")
    
    # List workspace contents
    contents = sandbox.list_workspace_contents()
    print(f"Workspace contents:\n{contents}")
except Exception as e:
    print(f"❌ Failed to test sandbox: {e}")

print("\nTesting LLM wrapper...")

# Detect environment variables
print(f"LLM_MODEL env: {os.getenv('LLM_MODEL', '(not set)')}")

# Create the LLM
llm = get_crewai_llm()
if llm is not None:
    print("✅ Successfully created CrewAI-compatible LLM")
    print(f"Model used: {llm.model}")
else:
    print("❌ Failed to create CrewAI-compatible LLM")

print("\nDiagnostic test complete.")
