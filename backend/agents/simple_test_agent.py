"""
Simple Test Agent for Project Sentinel.

This is a basic agent implementation for testing the agent deployment system.
It provides a simple interface for testing agent execution without complex dependencies.
"""

from typing import Any, Dict, List, Optional
from core.agent_base import BaseAgent, AgentRole, AgentContext, AgentResult, AgentStatus
from core.genai_client import genai_client
from loguru import logger


class SimpleTestAgent(BaseAgent):
    """
    A simple test agent for validating the agent deployment system.
    
    This agent can:
    - Respond to basic text requests
    - Log its activities
    - Return structured responses
    - Simulate different execution states
    """
    
    def __init__(self, **kwargs):
        super().__init__(
            role=AgentRole.CODE_REVIEWER,  # Using existing role for now
            name="Simple Test Agent",
            description="A basic test agent for validating the deployment system",
            tools=["text_processing", "logging"],
            model_name="gemini-1.5-pro",
            **kwargs
        )
        self.logger = logger.bind(agent="SimpleTestAgent")
    
    def get_system_prompt(self) -> str:
        """Get the system prompt for this agent."""
        return """
        You are a Simple Test Agent for Project Sentinel.
        
        Your role is to:
        1. Process user requests and provide helpful responses
        2. Log your activities for debugging
        3. Return structured results that can be used by the system
        4. Demonstrate basic agent functionality
        
        Always be helpful, clear, and professional in your responses.
        """
    
    async def execute(self, context: AgentContext) -> AgentResult:
        """
        Execute the agent's primary task.
        
        Args:
            context: The execution context containing mission details
            
        Returns:
            AgentResult: The result of the agent's execution
        """
        try:
            self.update_status(AgentStatus.WORKING)
            self.logger.info(f"Starting execution for mission {context.mission_id}")
            
            # Process the user prompt
            user_prompt = context.user_prompt
            self.logger.info(f"Processing user prompt: {user_prompt[:100]}...")
            
            # Generate response using GenAI
            response = await self._generate_response(user_prompt)
            
            # Create result
            result = AgentResult(
                success=True,
                output=response,
                metadata={
                    "mission_id": context.mission_id,
                    "agent_name": self.name,
                    "processing_time": "0.1s",
                    "tools_used": ["text_processing"]
                },
                tools_used=["text_processing"]
            )
            
            self.update_status(AgentStatus.COMPLETED)
            self.logger.info(f"Successfully completed mission {context.mission_id}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error during execution: {e}")
            self.update_status(AgentStatus.ERROR)
            
            return AgentResult(
                success=False,
                output="",
                error=str(e),
                metadata={"mission_id": context.mission_id},
                tools_used=[]
            )
    
    async def _generate_response(self, user_prompt: str) -> str:
        """
        Generate a response to the user prompt using Google GenAI.
        
        This uses the Gemini model for intelligent responses.
        Falls back to simple responses if GenAI is not available.
        """
        try:
            # Get the system prompt for this agent
            system_prompt = self.get_system_prompt()
            
            # Prepare context for the AI
            context = {
                "agent_name": self.name,
                "agent_role": self.role.value,
                "agent_status": self.status.value,
                "agent_capabilities": self.get_capabilities()
            }
            
            # Generate response using GenAI
            response = await genai_client.generate_response(
                prompt=user_prompt,
                system_prompt=system_prompt,
                context=context
            )
            
            return response
            
        except Exception as e:
            self.logger.error(f"Error generating AI response: {e}")
            # Fallback to simple responses
            return self._fallback_response(user_prompt)
    
    def _fallback_response(self, user_prompt: str) -> str:
        """Provide a fallback response when GenAI is not available."""
        prompt_lower = user_prompt.lower()
        
        # Simple keyword-based responses for testing
        if "hello" in prompt_lower or "hi" in prompt_lower:
            return "Hello! I'm the Simple Test Agent. I'm here to help you test the agent deployment system."
        
        elif "test" in prompt_lower:
            return "This is a test response from the Simple Test Agent. The agent system is working correctly!"
        
        elif "status" in prompt_lower:
            return f"Agent Status: {self.status.value}\nAgent Name: {self.name}\nRole: {self.role.value}"
        
        elif "help" in prompt_lower:
            return """I'm a Simple Test Agent. I can help you with:
            - Basic text processing
            - Status information
            - Test responses
            - Logging activities
            
            Try asking me about my status or capabilities!"""
        
        else:
            return f"I received your message: '{user_prompt}'\n\nThis is a test response from the Simple Test Agent. I'm processing your request and will provide more sophisticated responses as the system evolves."
    
    def get_capabilities(self) -> List[str]:
        """Get the agent's capabilities."""
        return [
            "text_processing",
            "basic_response_generation",
            "status_reporting",
            "activity_logging"
        ]
    
    def get_status_info(self) -> Dict[str, Any]:
        """Get detailed status information about the agent."""
        return {
            "name": self.name,
            "role": self.role.value,
            "status": self.status.value,
            "capabilities": self.get_capabilities(),
            "description": self.description,
            "model_name": self.model_name
        } 