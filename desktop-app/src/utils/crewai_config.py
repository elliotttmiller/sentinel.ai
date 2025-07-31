#!/usr/bin/env python3
"""
Custom CrewAI Configuration
Forces CrewAI to use our Google AI wrapper instead of LiteLLM's Vertex AI routing
"""

import os
from typing import Any, Dict, List
from crewai import Agent, Task, Crew, Process
from loguru import logger


class CustomCrewAI:
    """Custom CrewAI wrapper that forces use of our Google AI wrapper"""
    
    def __init__(self, llm):
        self.llm = llm
        # Force environment variables to prevent LiteLLM routing
        os.environ["LITELLM_MODEL"] = "gemini-1.5-pro"
        os.environ["LITELLM_PROVIDER"] = "google"
        os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY", "")
        
    def create_agent(self, role: str, goal: str, backstory: str, **kwargs) -> Agent:
        """Create an agent with forced LLM configuration"""
        return Agent(
            role=role,
            goal=goal,
            backstory=backstory,
            llm=self.llm,
            allow_delegation=False,
            verbose=True,
            **kwargs
        )
    
    def create_task(self, description: str, agent: Agent, **kwargs) -> Task:
        """Create a task with proper configuration"""
        return Task(
            description=description,
            agent=agent,
            **kwargs
        )
    
    def create_crew(self, agents: List[Agent], tasks: List[Task], **kwargs) -> Crew:
        """Create a crew with forced LLM configuration"""
        return Crew(
            agents=agents,
            tasks=tasks,
            process=Process.sequential,
            verbose=True,
            **kwargs
        )
    
    def run_crew(self, agents: List[Agent], tasks: List[Task], **kwargs) -> str:
        """Run a crew with proper error handling"""
        try:
            crew = self.create_crew(agents, tasks, **kwargs)
            return crew.kickoff()
        except Exception as e:
            logger.error(f"CrewAI execution failed: {e}")
            # Fallback to simple response
            return "Fallback response due to LLM configuration issue"


def create_custom_crewai(llm) -> CustomCrewAI:
    """Create a custom CrewAI instance with forced LLM configuration"""
    return CustomCrewAI(llm) 