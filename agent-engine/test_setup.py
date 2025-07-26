"""
Test script for Project Sentinel Agent Engine.

Verifies that all components are properly set up and can be imported.
"""

import sys
from pathlib import Path

# Add the agent-engine directory to the Python path
sys.path.insert(0, str(Path(__file__).parent))

def test_imports():
    """Test that all core modules can be imported."""
    print("Testing imports...")
    
    try:
        from core.agent_base import BaseAgent, AgentRole, AgentStatus
        print("✓ Core agent base imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import core agent base: {e}")
        return False
    
    try:
        from core.mission_planner import MissionPlanner
        print("✓ Mission planner imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import mission planner: {e}")
        return False
    
    try:
        from core.crew_manager import CrewManager
        print("✓ Crew manager imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import crew manager: {e}")
        return False
    
    try:
        from core.memory_manager import MemoryManager
        print("✓ Memory manager imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import memory manager: {e}")
        return False
    
    try:
        from agents.agent_factory import AgentFactory
        print("✓ Agent factory imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import agent factory: {e}")
        return False
    
    try:
        from agents.prompt_alchemist import PromptAlchemistAgent
        print("✓ Prompt Alchemist agent imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import Prompt Alchemist agent: {e}")
        return False
    
    try:
        from agents.grand_architect import GrandArchitectAgent
        print("✓ Grand Architect agent imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import Grand Architect agent: {e}")
        return False
    
    try:
        from agents.senior_developer import SeniorDeveloperAgent
        print("✓ Senior Developer agent imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import Senior Developer agent: {e}")
        return False
    
    try:
        from agents.code_reviewer import CodeReviewerAgent
        print("✓ Code Reviewer agent imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import Code Reviewer agent: {e}")
        return False
    
    try:
        from agents.qa_tester import QATesterAgent
        print("✓ QA Tester agent imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import QA Tester agent: {e}")
        return False
    
    try:
        from agents.debugger import DebuggerAgent
        print("✓ Debugger agent imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import Debugger agent: {e}")
        return False
    
    try:
        from agents.documentation import DocumentationAgent
        print("✓ Documentation agent imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import Documentation agent: {e}")
        return False
    
    try:
        from config import AgentEngineConfig
        print("✓ Configuration imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import configuration: {e}")
        return False
    
    return True


def test_agent_roles():
    """Test that all agent roles are defined."""
    print("\nTesting agent roles...")
    
    try:
        from core.agent_base import AgentRole
        
        expected_roles = [
            "prompt_alchemist",
            "grand_architect", 
            "senior_developer",
            "code_reviewer",
            "qa_tester",
            "debugger",
            "documentation"
        ]
        
        for role_name in expected_roles:
            if hasattr(AgentRole, role_name.upper()):
                print(f"✓ Agent role '{role_name}' found")
            else:
                print(f"✗ Agent role '{role_name}' not found")
                return False
        
        return True
    except Exception as e:
        print(f"✗ Error testing agent roles: {e}")
        return False


def test_agent_factory():
    """Test that the agent factory can be instantiated."""
    print("\nTesting agent factory...")
    
    try:
        from agents.agent_factory import AgentFactory
        
        # Create agent factory with placeholder dependencies
        factory = AgentFactory(llm_client=None, tool_manager=None)
        
        # Test getting available roles
        roles = factory.get_available_roles()
        print(f"✓ Agent factory created with {len(roles)} available roles")
        
        # Test role support
        from core.agent_base import AgentRole
        for role in AgentRole:
            if factory.is_role_supported(role):
                print(f"✓ Role '{role.value}' is supported")
            else:
                print(f"✗ Role '{role.value}' is not supported")
                return False
        
        return True
    except Exception as e:
        print(f"✗ Error testing agent factory: {e}")
        return False


def test_configuration():
    """Test that configuration can be loaded."""
    print("\nTesting configuration...")
    
    try:
        from config import load_config
        
        config = load_config()
        print(f"✓ Configuration loaded successfully")
        print(f"  - Host: {config.host}")
        print(f"  - Port: {config.port}")
        print(f"  - Default Model: {config.default_model}")
        print(f"  - Workspace Path: {config.workspace_path}")
        
        return True
    except Exception as e:
        print(f"✗ Error testing configuration: {e}")
        return False


def main():
    """Run all tests."""
    print("Project Sentinel Agent Engine - Setup Test")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_agent_roles,
        test_agent_factory,
        test_configuration
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Agent Engine is ready to use.")
        return True
    else:
        print("❌ Some tests failed. Please check the errors above.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 