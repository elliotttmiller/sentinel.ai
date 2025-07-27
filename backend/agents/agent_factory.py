"""
Agent Factory for Project Sentinel.

Dynamically creates specialized agents based on their roles.
Provides a centralized way to instantiate and configure agents.
"""

from typing import Dict, Type, Optional
from loguru import logger

from core.agent_base import BaseAgent, AgentRole
from .prompt_alchemist import PromptAlchemistAgent
from .grand_architect import GrandArchitectAgent
from .senior_developer import SeniorDeveloperAgent
from .code_reviewer import CodeReviewerAgent
from .qa_tester import QATesterAgent
from .debugger import DebuggerAgent
from .documentation import DocumentationAgent
from .simple_test_agent import SimpleTestAgent


class AgentFactory:
    """
    Factory for creating specialized agents.
    
    Maintains a registry of available agent types and their configurations.
    Provides a unified interface for agent instantiation.
    """
    
    def __init__(self, llm_client, tool_manager):
        self.llm_client = llm_client
        self.tool_manager = tool_manager
        self.logger = logger.bind(component="agent_factory")
        
        # Registry of available agent types
        self.agent_registry: Dict[AgentRole, Type[BaseAgent]] = {
            AgentRole.PROMPT_ALCHEMIST: PromptAlchemistAgent,
            AgentRole.GRAND_ARCHITECT: GrandArchitectAgent,
            AgentRole.SENIOR_DEVELOPER: SeniorDeveloperAgent,
            AgentRole.CODE_REVIEWER: CodeReviewerAgent,
            AgentRole.QA_TESTER: QATesterAgent,
            AgentRole.DEBUGGER: DebuggerAgent,
            AgentRole.DOCUMENTATION: DocumentationAgent,
        }
        
        # Add simple test agent to registry (using CODE_REVIEWER role for now)
        self.simple_test_agent = SimpleTestAgent
        
        # Agent configurations
        self.agent_configs = {
            AgentRole.PROMPT_ALCHEMIST: {
                "name": "Prompt Alchemist",
                "description": "Specialized AI prompt engineer that optimizes and clarifies user requests",
                "tools": ["text_analysis", "prompt_optimization"],
                "model_name": "gemini-1.5-pro"
            },
            AgentRole.GRAND_ARCHITECT: {
                "name": "Grand Architect", 
                "description": "AI project manager that creates detailed execution plans",
                "tools": ["planning", "task_breakdown"],
                "model_name": "gemini-1.5-pro"
            },
            AgentRole.SENIOR_DEVELOPER: {
                "name": "Senior Developer",
                "description": "Primary code builder and implementer with expertise in multiple languages",
                "tools": ["file_io", "shell_access", "web_search", "code_generation"],
                "model_name": "gemini-1.5-pro"
            },
            AgentRole.CODE_REVIEWER: {
                "name": "Code Reviewer",
                "description": "Quality gatekeeper that analyzes code for issues and best practices",
                "tools": ["file_io", "code_analysis", "static_analysis"],
                "model_name": "gemini-1.5-pro"
            },
            AgentRole.QA_TESTER: {
                "name": "QA Tester",
                "description": "Test creation and validation specialist",
                "tools": ["file_io", "shell_access", "test_generation", "test_execution"],
                "model_name": "gemini-1.5-pro"
            },
            AgentRole.DEBUGGER: {
                "name": "Debugger",
                "description": "Crisis manager for error resolution and problem-solving",
                "tools": ["file_io", "shell_access", "error_analysis", "code_generation"],
                "model_name": "gemini-1.5-pro"
            },
            AgentRole.DOCUMENTATION: {
                "name": "Documentation Agent",
                "description": "Technical writer and historian for project documentation",
                "tools": ["file_io", "code_analysis", "documentation_generation"],
                "model_name": "gemini-1.5-pro"
            }
        }
    
    async def create_agent(self, role: AgentRole) -> BaseAgent:
        """
        Create an agent instance for the specified role.
        
        Args:
            role: The agent role to create
            
        Returns:
            BaseAgent: The instantiated agent
            
        Raises:
            ValueError: If the role is not supported
        """
        if role not in self.agent_registry:
            raise ValueError(f"Unsupported agent role: {role}")
        
        agent_class = self.agent_registry[role]
        config = self.agent_configs[role]
        
        self.logger.info(f"Creating agent: {config['name']} ({role.value})")
        
        try:
            agent = agent_class(
                role=role,
                name=config["name"],
                description=config["description"],
                tools=config["tools"],
                model_name=config["model_name"],
                llm_client=self.llm_client,
                tool_manager=self.tool_manager
            )
            
            self.logger.info(f"Successfully created agent: {agent.name}")
            return agent
            
        except Exception as e:
            self.logger.error(f"Failed to create agent {role.value}: {e}")
            raise
    
    def get_available_roles(self) -> list[AgentRole]:
        """Get list of available agent roles."""
        return list(self.agent_registry.keys())
    
    def get_agent_config(self, role: AgentRole) -> Optional[Dict]:
        """Get configuration for a specific agent role."""
        return self.agent_configs.get(role)
    
    def register_agent_type(self, role: AgentRole, agent_class: Type[BaseAgent], config: Dict) -> None:
        """
        Register a new agent type.
        
        Args:
            role: The agent role
            agent_class: The agent class
            config: Configuration for the agent
        """
        self.agent_registry[role] = agent_class
        self.agent_configs[role] = config
        self.logger.info(f"Registered new agent type: {role.value}")
    
    def is_role_supported(self, role: AgentRole) -> bool:
        """Check if a role is supported."""
        return role in self.agent_registry 