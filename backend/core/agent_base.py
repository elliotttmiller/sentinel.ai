"""
Base Agent class for Project Sentinel.

All specialized agents inherit from this base class to ensure consistent
behavior and tool management across the agent guild.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass
from enum import Enum
import asyncio
from pathlib import Path

from pydantic import BaseModel, Field
from loguru import logger


class AgentRole(str, Enum):
    """Enumeration of available agent roles."""
    PROMPT_ALCHEMIST = "prompt_alchemist"
    GRAND_ARCHITECT = "grand_architect"
    SENIOR_DEVELOPER = "senior_developer"
    CODE_REVIEWER = "code_reviewer"
    QA_TESTER = "qa_tester"
    DEBUGGER = "debugger"
    DOCUMENTATION = "documentation"


class AgentStatus(str, Enum):
    """Enumeration of agent status states."""
    IDLE = "idle"
    WORKING = "working"
    WAITING = "waiting"
    ERROR = "error"
    COMPLETED = "completed"


@dataclass
class AgentContext:
    """Context information passed to agents during execution."""
    mission_id: str
    user_prompt: str
    workspace_path: Path
    tools: Dict[str, Any]
    memory: Optional[Dict[str, Any]] = None


class AgentResult(BaseModel):
    """Result object returned by agents after task completion."""
    success: bool = Field(description="Whether the task was completed successfully")
    output: str = Field(description="The output or result of the agent's work")
    error: Optional[str] = Field(default=None, description="Error message if task failed")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    tools_used: List[str] = Field(default_factory=list, description="List of tools used")


class BaseAgent(ABC):
    """
    Base class for all Project Sentinel agents.
    
    Provides common functionality for tool management, status tracking,
    and result handling.
    """
    
    def __init__(
        self,
        role: AgentRole,
        name: str,
        description: str,
        tools: Optional[List[str]] = None,
        model_name: str = "gemini-1.5-pro"
    ):
        self.role = role
        self.name = name
        self.description = description
        self.tools = tools or []
        self.model_name = model_name
        self.status = AgentStatus.IDLE
        self.context: Optional[AgentContext] = None
        self.logger = logger.bind(agent=name, role=role.value)
        
    @abstractmethod
    async def execute(self, context: AgentContext) -> AgentResult:
        """
        Execute the agent's primary task.
        
        Args:
            context: The execution context containing mission details
            
        Returns:
            AgentResult: The result of the agent's execution
        """
        pass
    
    @abstractmethod
    def get_system_prompt(self) -> str:
        """
        Get the system prompt that defines the agent's behavior.
        
        Returns:
            str: The system prompt for this agent
        """
        pass
    
    def set_context(self, context: AgentContext) -> None:
        """Set the execution context for the agent."""
        self.context = context
        self.logger.info(f"Context set for mission {context.mission_id}")
    
    def update_status(self, status: AgentStatus) -> None:
        """Update the agent's current status."""
        self.status = status
        self.logger.info(f"Status updated to {status.value}")
    
    def get_available_tools(self) -> List[str]:
        """Get list of tools available to this agent."""
        return self.tools.copy()
    
    async def ask_human(self, question: str, options: Optional[List[str]] = None) -> str:
        """
        Ask for human guidance when agent needs input.
        
        Args:
            question: The question to ask the human
            options: Optional list of choices
            
        Returns:
            str: The human's response
        """
        self.update_status(AgentStatus.WAITING)
        self.logger.info(f"Asking human: {question}")
        
        # TODO: Implement human-in-the-loop communication
        # This will be connected to the mobile app via the backend
        
        # For now, return a placeholder
        return "human_response_placeholder"
    
    def log_activity(self, message: str, level: str = "info") -> None:
        """Log agent activity with appropriate level."""
        getattr(self.logger, level)(message)
    
    def validate_result(self, result: AgentResult) -> bool:
        """
        Validate the agent's result.
        
        Args:
            result: The agent result to validate
            
        Returns:
            bool: True if result is valid
        """
        if not isinstance(result, AgentResult):
            self.logger.error("Result is not an AgentResult instance")
            return False
        
        if result.success and not result.output:
            self.logger.warning("Successful result has no output")
            return False
            
        return True
    
    def __str__(self) -> str:
        return f"{self.name} ({self.role.value})"
    
    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(name='{self.name}', role={self.role.value})>" 