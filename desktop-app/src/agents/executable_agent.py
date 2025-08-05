"""
Tool-Enabled Executable Agents for Real Task Execution
These agents use CrewAI's native tool support to perform actual work
"""

from typing import List, Any
from loguru import logger

# Import CrewAI with fallback
try:
    from crewai import Agent
    CREWAI_AVAILABLE = True
    logger.info("CrewAI Agent imported successfully")
except Exception as e:
    logger.warning(f"CrewAI import failed: {e}. Using fallback Agent.")
    CREWAI_AVAILABLE = False
    
    # Simple fallback Agent class
    class Agent:
        def __init__(self, role, goal, backstory, llm=None, verbose=True, allow_delegation=False, tools=None):
            self.role = role
            self.goal = goal
            self.backstory = backstory
            self.llm = llm
            self.verbose = verbose
            self.allow_delegation = allow_delegation
            self.tools = tools or []
            if verbose:
                logger.info(f"Fallback Agent created: {role}")

# Import LLM
try:
    from ..utils.google_ai_wrapper import create_google_ai_llm
except ImportError:
    from utils.google_ai_wrapper import create_google_ai_llm

# Import tools
try:
    from ..tools.file_system_tools import ALL_TOOLS
except ImportError:
    from tools.file_system_tools import ALL_TOOLS

class ExecutableAgents:
    """
    Contains the definitions for agents that can perform real, executable tasks.
    """
    
    def __init__(self):
        self.llm = create_google_ai_llm()
        self.crewai_available = CREWAI_AVAILABLE
        logger.info(f"ExecutableAgents initialized with Google AI LLM (CrewAI available: {self.crewai_available})")
    
    def planner_agent(self) -> Agent:
        """Agent that creates detailed execution plans"""
        return Agent(
            role="AI Software Architect and Planner",
            goal="Break down a user's request into a clear, step-by-step, executable plan. Each step must correspond to a single, available tool.",
            backstory=(
                "You are a meticulous planner, an expert in software development workflows. "
                "Your strength lies in analyzing complex requests and decomposing them into a sequence of simple, "
                "atomic actions. You do not execute tasks yourself; you only create the plan for others to follow. "
                "You understand the available tools: Create File, Execute Python File, List Directory, Read File, "
                "Install Python Package, and Create Directory. Each step in your plan must use one of these tools."
            ),
            llm=self.llm,
            verbose=True,
            allow_delegation=False,
        )

    def executor_agent(self) -> Agent:
        """Agent that executes tasks using available tools"""
        return Agent(
            role="Senior Software Engineer and Executor",
            goal="Execute the step-by-step plan provided by the planner. Use the available tools to perform each action and report the results.",
            backstory=(
                "You are a hands-on engineer who gets things done. You follow instructions precisely, "
                "executing one step at a time using your available tools. After each step, you carefully review the outcome "
                "to ensure it was successful before proceeding to the next. You have access to file system tools "
                "that allow you to create files, execute Python code, manage directories, and install packages safely."
            ),
            llm=self.llm,
            verbose=True,
            allow_delegation=False,
            tools=ALL_TOOLS if self.crewai_available else []
        )
    
    def supervisor_agent(self) -> Agent:
        """Agent that oversees and validates the entire process"""
        read_only_tools = [tool for tool in ALL_TOOLS if tool.name in ["List Directory", "Read File"]] if self.crewai_available else []
        
        return Agent(
            role="Technical Project Supervisor",
            goal="Oversee the planning and execution process, ensuring quality and completeness of the final deliverable.",
            backstory=(
                "You are an experienced technical lead who ensures that projects are completed to specification. "
                "You review plans for completeness, monitor execution for success, and verify that the final "
                "deliverable meets the user's requirements. You provide guidance and make final assessments."
            ),
            llm=self.llm,
            verbose=True,
            allow_delegation=False,
            tools=read_only_tools  # Read-only tools for validation
        )
