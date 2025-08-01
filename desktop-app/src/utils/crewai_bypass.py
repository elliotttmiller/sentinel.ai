#!/usr/bin/env python3
"""
Complete CrewAI Bypass System
Eliminates LiteLLM dependency and uses Google AI wrapper directly
"""

import os
import json
from typing import Any, Dict, List, Optional
from loguru import logger
from pathlib import Path


class DirectAIAgent:
    """Direct AI agent that bypasses CrewAI/LiteLLM entirely"""
    
    def __init__(self, llm, role: str, goal: str, backstory: str):
        if llm is None:
            raise ValueError(f"LLM cannot be None for DirectAIAgent with role: {role}")
        
        logger.info(f"Creating DirectAIAgent with role: {role}, LLM type: {type(llm)}")
        
        self.llm = llm
        self.role = role
        self.goal = goal
        self.backstory = backstory
    
    def get(self, key: str, default=None):
        """Compatibility method for crewai library"""
        if hasattr(self, key):
            return getattr(self, key)
        return default
        
    def execute_task(self, task_description: str, expected_output: str = "") -> str:
        """Execute a task directly using our Google AI wrapper"""
        try:
            # Create a comprehensive prompt
            prompt = f"""You are {self.role}.

GOAL: {self.goal}

BACKSTORY: {self.backstory}

TASK: {task_description}

{expected_output if expected_output else "Provide a clear, actionable response."}

RESPONSE:"""
            
            # Convert to LangChain message format
            from langchain_core.messages import HumanMessage
            messages = [HumanMessage(content=prompt)]
            
            # Use our Google AI wrapper directly with proper message format
            response = self.llm.invoke(messages)
            return response.content if hasattr(response, 'content') else str(response)
            
        except Exception as e:
            logger.error(f"Direct AI execution failed: {e}")
            return f"Fallback response: {task_description[:100]}..."


class DirectAICrew:
    """Direct AI crew that bypasses CrewAI entirely"""
    
    def __init__(self, llm):
        self.llm = llm
        self.agents = []
        self.tasks = []
        
    def add_agent(self, role: str, goal: str, backstory: str) -> DirectAIAgent:
        """Add an agent to the crew"""
        agent = DirectAIAgent(self.llm, role, goal, backstory)
        self.agents.append(agent)
        return agent
        
    def add_task(self, description: str, agent: DirectAIAgent, expected_output: str = "") -> Dict:
        """Add a task to the crew"""
        task = {
            "description": description,
            "agent": agent,
            "expected_output": expected_output
        }
        self.tasks.append(task)
        return task
        
    def execute(self) -> str:
        """Execute all tasks sequentially"""
        results = []
        
        for i, task in enumerate(self.tasks):
            logger.info(f"Executing task {i+1}/{len(self.tasks)}")
            result = task["agent"].execute_task(
                task["description"], 
                task["expected_output"]
            )
            results.append(result)
            
        return results[-1] if results else "No tasks executed"


def create_direct_ai_crew(llm) -> DirectAICrew:
    """Create a direct AI crew that bypasses CrewAI/LiteLLM"""
    return DirectAICrew(llm)


# Environment configuration to prevent any LiteLLM interference
def configure_direct_ai_environment():
    """Configure environment to prevent LiteLLM interference"""
    # Disable LiteLLM completely
    os.environ["LITELLM_DISABLE"] = "1"
    os.environ["LITELLM_MODEL"] = ""
    os.environ["LITELLM_PROVIDER"] = ""
    
    # Force direct Google AI usage
    os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY", "")
    os.environ["GOOGLE_AI_API_URL"] = "https://generativelanguage.googleapis.com"
    
    # Disable any fallback routing
    os.environ["LITELLM_FALLBACK_MODELS"] = ""
    os.environ["LITELLM_MODEL_ALIASES"] = ""
    
    logger.info("Direct AI environment configured - LiteLLM disabled") 