from typing import Dict, Any, Optional
from loguru import logger
from agents.senior_developer import SeniorDeveloper
from agents.qa_tester import QATester
from agents.system_administrator import SystemAdministrator
from agents.file_manager import FileManager

class AgentFactory:
    """Factory for creating worker agents in the engine."""
    
    def __init__(self, llm_client=None, tool_manager=None):
        self.llm_client = llm_client
        self.tool_manager = tool_manager
        logger.info("AgentFactory initialized for engine")
    
    def create_agent(self, agent_type: str, **kwargs) -> Optional[Any]:
        """Create a specific agent by type."""
        try:
            if agent_type == "senior_developer":
                return SeniorDeveloper(
                    llm_client=self.llm_client,
                    tool_manager=self.tool_manager,
                    **kwargs
                )
            elif agent_type == "qa_tester":
                return QATester(
                    llm_client=self.llm_client,
                    tool_manager=self.tool_manager,
                    **kwargs
                )
            elif agent_type == "system_administrator":
                return SystemAdministrator(
                    llm_client=self.llm_client,
                    tool_manager=self.tool_manager,
                    **kwargs
                )
            elif agent_type == "file_manager":
                return FileManager(
                    llm_client=self.llm_client,
                    tool_manager=self.tool_manager,
                    **kwargs
                )
            else:
                logger.error(f"Unknown agent type: {agent_type}")
                return None
        except Exception as e:
            logger.error(f"Failed to create agent {agent_type}: {e}")
            return None
    
    def list_agent_types(self) -> list:
        """List all available agent types."""
        return [
            "senior_developer",
            "qa_tester", 
            "system_administrator",
            "file_manager"
        ] 