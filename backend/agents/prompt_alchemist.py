"""
Prompt Alchemist Agent for Project Sentinel.

Specialized AI prompt engineer that transforms vague user requests into
crystal-clear, actionable instructions for AI agents.
"""

from typing import Dict, Any, Optional
import json
from loguru import logger

from core.agent_base import BaseAgent, AgentRole, AgentContext, AgentResult


class PromptAlchemistAgent(BaseAgent):
    """
    Prompt Alchemist - Specialized AI prompt engineer.
    
    Responsibilities:
    - Analyze user prompts for ambiguity and missing context
    - Add necessary technical details and constraints
    - Define specific, measurable success criteria
    - Rewrite prompts with enhanced clarity and precision
    - Document assumptions and constraints
    """
    
    def __init__(
        self,
        role: AgentRole,
        name: str,
        description: str,
        tools: list[str],
        model_name: str,
        llm_client,
        tool_manager
    ):
        super().__init__(role, name, description, tools, model_name)
        self.llm_client = llm_client
        self.tool_manager = tool_manager
        self.logger = logger.bind(agent="prompt_alchemist")
    
    def get_system_prompt(self) -> str:
        """Get the system prompt that defines the Prompt Alchemist's behavior."""
        return """
        You are the Prompt Alchemist, a specialized AI prompt engineer for Project Sentinel.
        Your role is to transform vague or ambiguous user requests into crystal-clear,
        actionable instructions that can be executed by AI agents.
        
        Your expertise includes:
        1. **Ambiguity Detection**: Identify unclear or incomplete requests
        2. **Context Enhancement**: Add missing technical details and constraints
        3. **Success Criteria Definition**: Create specific, measurable objectives
        4. **Prompt Optimization**: Rewrite requests with enhanced clarity and precision
        5. **Assumption Documentation**: Identify and document implicit assumptions
        
        For each user prompt, you must:
        - Analyze the prompt for potential ambiguities
        - Identify missing technical context (programming languages, frameworks, etc.)
        - Define clear, measurable success criteria
        - Rewrite the prompt with enhanced clarity and specificity
        - Document any assumptions about the user's environment or requirements
        - Identify potential constraints or limitations
        
        Your output must be structured and comprehensive, providing a foundation
        for the Grand Architect to create detailed execution plans.
        
        Always maintain the user's original intent while adding necessary precision
        and technical context for successful AI agent execution.
        """
    
    async def execute(self, context: AgentContext) -> AgentResult:
        """
        Execute the Prompt Alchemist's optimization process.
        
        Args:
            context: The execution context containing the user's prompt
            
        Returns:
            AgentResult: The optimized prompt and analysis
        """
        self.logger.info(f"Starting prompt optimization for mission {context.mission_id}")
        self.update_status(AgentStatus.WORKING)
        
        try:
            # Extract the user prompt from context
            user_prompt = context.user_prompt
            
            # Perform prompt analysis and optimization
            optimization_result = await self._optimize_prompt(user_prompt)
            
            # Create the result
            result = AgentResult(
                success=True,
                output=json.dumps(optimization_result, indent=2),
                metadata={
                    "original_prompt": user_prompt,
                    "optimization_type": "prompt_alchemist",
                    "technical_context": optimization_result.get("technical_context", {}),
                    "success_criteria_count": len(optimization_result.get("success_criteria", [])),
                    "constraints_count": len(optimization_result.get("constraints", [])),
                    "assumptions_count": len(optimization_result.get("assumptions", []))
                }
            )
            
            self.logger.info("Prompt optimization completed successfully")
            self.update_status(AgentStatus.COMPLETED)
            return result
            
        except Exception as e:
            self.logger.error(f"Prompt optimization failed: {e}")
            self.update_status(AgentStatus.ERROR)
            return AgentResult(
                success=False,
                output="",
                error=f"Prompt optimization failed: {str(e)}"
            )
    
    async def _optimize_prompt(self, user_prompt: str) -> Dict[str, Any]:
        """
        Optimize and enhance the user's prompt.
        
        Args:
            user_prompt: The original user prompt
            
        Returns:
            Dict[str, Any]: Optimized prompt with analysis
        """
        self.logger.info("Analyzing and optimizing user prompt")
        
        # Create the optimization prompt
        optimization_prompt = f"""
        Original User Prompt: {user_prompt}
        
        Please analyze and optimize this prompt according to your role as the Prompt Alchemist.
        
        Provide your response in the following JSON format:
        {{
            "optimized_prompt": "The enhanced, detailed version of the user's request with clear instructions",
            "technical_context": {{
                "programming_languages": ["list", "of", "relevant", "languages"],
                "frameworks": ["list", "of", "relevant", "frameworks"],
                "file_types": ["list", "of", "relevant", "file", "types"],
                "external_apis": ["list", "of", "apis", "needed"],
                "tools_required": ["list", "of", "tools", "needed"]
            }},
            "success_criteria": [
                "Specific, measurable criteria 1",
                "Specific, measurable criteria 2"
            ],
            "constraints": [
                "Technical or business constraint 1",
                "Technical or business constraint 2"
            ],
            "assumptions": [
                "Assumption about user's environment 1",
                "Assumption about user's environment 2"
            ],
            "ambiguities_resolved": [
                "Ambiguity 1 that was resolved",
                "Ambiguity 2 that was resolved"
            ],
            "enhancements_made": [
                "Enhancement 1 that was added",
                "Enhancement 2 that was added"
            ]
        }}
        
        Focus on:
        1. Making the prompt specific and actionable
        2. Identifying required technical context
        3. Defining clear success criteria
        4. Documenting constraints and assumptions
        5. Resolving any ambiguities
        """
        
        # TODO: Implement actual LLM call
        # For now, return a placeholder optimization
        return {
            "optimized_prompt": f"Enhanced version of: {user_prompt}",
            "technical_context": {
                "programming_languages": ["python", "javascript"],
                "frameworks": ["fastapi", "react"],
                "file_types": ["py", "js", "json", "md"],
                "external_apis": [],
                "tools_required": ["file_io", "shell_access", "code_generation"]
            },
            "success_criteria": [
                "Task is completed successfully",
                "Code is functional and well-structured",
                "Documentation is updated appropriately"
            ],
            "constraints": [
                "Must work on local development environment",
                "Must follow project coding standards",
                "Must be well-documented"
            ],
            "assumptions": [
                "User has Python and Node.js installed",
                "User has Git configured",
                "User has appropriate development tools"
            ],
            "ambiguities_resolved": [
                "Clarified programming language requirements",
                "Specified file structure expectations"
            ],
            "enhancements_made": [
                "Added technical context requirements",
                "Defined clear success criteria",
                "Documented constraints and assumptions"
            ]
        }
    
    async def _analyze_ambiguity(self, prompt: str) -> list[str]:
        """
        Analyze the prompt for potential ambiguities.
        
        Args:
            prompt: The prompt to analyze
            
        Returns:
            List[str]: List of identified ambiguities
        """
        # TODO: Implement ambiguity analysis
        return [
            "Programming language not specified",
            "File structure requirements unclear",
            "Success criteria not defined"
        ]
    
    async def _identify_technical_context(self, prompt: str) -> Dict[str, Any]:
        """
        Identify required technical context from the prompt.
        
        Args:
            prompt: The prompt to analyze
            
        Returns:
            Dict[str, Any]: Technical context requirements
        """
        # TODO: Implement technical context identification
        return {
            "programming_languages": ["python", "javascript"],
            "frameworks": ["fastapi", "react"],
            "file_types": ["py", "js", "json"],
            "external_apis": [],
            "tools_required": ["file_io", "shell_access"]
        }
    
    async def _define_success_criteria(self, prompt: str) -> list[str]:
        """
        Define specific, measurable success criteria.
        
        Args:
            prompt: The prompt to analyze
            
        Returns:
            List[str]: List of success criteria
        """
        # TODO: Implement success criteria definition
        return [
            "Task is completed successfully",
            "Code is functional and well-structured",
            "Documentation is updated appropriately"
        ] 