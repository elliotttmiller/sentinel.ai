"""Base Agent and Action classes for CopilotKit integration"""

import re
from typing import Optional, List, TypedDict, Any
from abc import ABC, abstractmethod

class AgentDict(TypedDict):
    name: str
    description: Optional[str]

class BaseAgent(ABC):
    def __init__(self, *, name: str, description: Optional[str] = None):
        self.name = name
        self.description = description
        if not re.match(r"^[a-zA-Z0-9_-]+$", name):
            raise ValueError(f"Invalid agent name '{name}': must consist of alphanumeric characters, underscores, and hyphens only")

    @abstractmethod
    def execute(self, *, state: dict, config: Optional[dict], messages: List[Any], thread_id: str, actions: Optional[List[Any]] = None, meta_events: Optional[List[Any]] = None, **kwargs):
        """Execute the agent"""
        pass

    @abstractmethod
    async def get_state(self, *, thread_id: str):
        """Get agent state"""
        return {
            "threadId": thread_id or "",
            "threadExists": False,
            "state": {},
            "messages": []
        }

class ActionDict(TypedDict):
    name: str
    description: str
    parameters: List[Any]

class BaseAction:
    def __init__(self, *, name: str, handler, description: Optional[str] = None, parameters: Optional[List[Any]] = None):
        self.name = name
        self.description = description
        self.parameters = parameters
        self.handler = handler
        if not re.match(r"^[a-zA-Z0-9_-]+$", name):
            raise ValueError(f"Invalid action name '{name}': must consist of alphanumeric characters, underscores, and hyphens only")

    async def execute(self, *, arguments: dict):
        result = self.handler(**arguments)
        if hasattr(result, '__await__'):
            result = await result
        return {"result": result}

    def dict_repr(self) -> ActionDict:
        return {
            'name': self.name,
            'description': self.description or '',
            'parameters': self.parameters or [],
        }
