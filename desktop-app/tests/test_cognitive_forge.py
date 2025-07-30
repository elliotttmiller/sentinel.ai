"""
Comprehensive Tests for Cognitive Forge System
Tests all major components and integrations
"""

from src.agents.advanced_agents import PlannerAgents, WorkerAgents
from src.tools.advanced_tools import FileTools, ShellTools, SystemTools
from src.models.advanced_database import db_manager
from src.core.cognitive_forge_engine import cognitive_forge_engine
import pytest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


class TestCognitiveForgeEngine:
    """Test the main Cognitive Forge Engine"""

    def test_engine_initialization(self):
        """Test that the engine initializes correctly"""
        assert cognitive_forge_engine is not None
        assert hasattr(cognitive_forge_engine, "llm")
        assert hasattr(cognitive_forge_engine, "db_manager")

    def test_engine_components(self):
        """Test that all engine components are available"""
        engine = cognitive_forge_engine
        assert hasattr(engine, "planner_agents")
        assert hasattr(engine, "worker_agents")
        assert hasattr(engine, "memory_agents")

    def test_system_info(self):
        """Test system info retrieval"""
        info = cognitive_forge_engine.get_system_info()
        assert isinstance(info, dict)
        assert "engine_status" in info


class TestDatabaseManager:
    """Test the database management system"""

    def test_db_manager_initialization(self):
        """Test database manager initialization"""
        assert db_manager is not None
        assert hasattr(db_manager, "create_mission")
        assert hasattr(db_manager, "update_mission_status")

    def test_memory_operations(self):
        """Test memory storage and retrieval"""
        # Test memory storage
        success = db_manager.store_memory("test_mission_123", "Test prompt", "Test result", True)
        assert success is True

        # Test memory search
        memories = db_manager.search_memory("test", limit=1)
        assert isinstance(memories, list)

    def test_system_stats(self):
        """Test system statistics"""
        stats = db_manager.get_system_stats()
        assert isinstance(stats, dict)
        assert "total_missions" in stats
        assert "memory_entries" in stats


class TestAdvancedTools:
    """Test the advanced tools system"""

    def test_file_tools(self):
        """Test file operations"""
        # Test file writing
        test_content = "Test content for file tools"
        result = FileTools.write_file("test_file.txt", test_content)
        assert "successfully" in result.lower()

        # Test file reading
        read_result = FileTools.read_file("test_file.txt")
        assert test_content in read_result

        # Test file listing
        list_result = FileTools.list_files(".")
        assert isinstance(list_result, str)
        assert "test_file.txt" in list_result

        # Cleanup
        import os

        if os.path.exists("test_file.txt"):
            os.remove("test_file.txt")

    def test_shell_tools(self):
        """Test shell command execution"""
        # Test allowed command
        result = ShellTools.execute_shell_command("echo test")
        assert "test" in result

        # Test disallowed command
        result = ShellTools.execute_shell_command("rm -rf /")
        assert "not permitted" in result

    def test_system_tools(self):
        """Test system information tools"""
        info = SystemTools.get_system_info()
        assert isinstance(info, str)
        assert "CPU" in info or "System Information" in info


class TestAdvancedAgents:
    """Test the advanced agents system"""

    def test_planner_agents(self):
        """Test planner agent creation"""
        planners = PlannerAgents()
        assert hasattr(planners, "lead_architect")
        assert hasattr(planners, "plan_validator")

    def test_worker_agents(self):
        """Test worker agent creation"""
        workers = WorkerAgents()
        assert hasattr(workers, "senior_developer")
        assert hasattr(workers, "qa_tester")
        assert hasattr(workers, "code_analyzer")
        assert hasattr(workers, "system_integrator")


class TestConfiguration:
    """Test configuration system"""

    def test_settings_import(self):
        """Test that settings can be imported"""
        try:
            from config.settings import settings

            assert settings is not None
        except ImportError:
            pytest.skip("Settings not available")

    def test_environment_validation(self):
        """Test environment validation"""
        from config.settings import validate_environment

        # This will fail without proper .env file, which is expected
        # We're just testing that the function exists and runs
        result = validate_environment()
        assert isinstance(result, bool)


def test_integration():
    """Integration test for the complete system"""
    # Test that all major components can be imported and initialized
    components = [
        cognitive_forge_engine,
        db_manager,
        FileTools,
        ShellTools,
        SystemTools,
        PlannerAgents,
        WorkerAgents,
    ]

    for component in components:
        assert component is not None


if __name__ == "__main__":
    # Run basic tests
    print("🧪 Running Cognitive Forge Tests...")

    # Test engine
    test_engine = TestCognitiveForgeEngine()
    test_engine.test_engine_initialization()
    print("✅ Engine tests passed")

    # Test database
    test_db = TestDatabaseManager()
    test_db.test_db_manager_initialization()
    print("✅ Database tests passed")

    # Test tools
    test_tools = TestAdvancedTools()
    test_tools.test_file_tools()
    print("✅ Tools tests passed")

    # Test agents
    test_agents = TestAdvancedAgents()
    test_agents.test_planner_agents()
    test_agents.test_worker_agents()
    print("✅ Agent tests passed")

    print("🎉 All tests passed!")
