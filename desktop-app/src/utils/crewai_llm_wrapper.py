"""
CrewAI LLM Wrapper with Model Name Normalization
This wrapper fixes the issue where ChatGoogleGenerativeAI model names 
get incorrectly prefixed with "models/", causing LiteLLM to fail.
"""

from langchain_google_genai import ChatGoogleGenerativeAI
from loguru import logger
import os


class CrewAICompatibleLLM(ChatGoogleGenerativeAI):
    """Wrapper that ensures proper model naming for CrewAI/LiteLLM"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Normalize model name after initialization
        self.model_name = self._normalize_model_name(self.model)
        logger.info(f"CrewAI-compatible LLM initialized. Internal model: {self.model}, CrewAI model_name: {self.model_name}")
    
    def __str__(self):
        """Return the normalized model name for CrewAI"""
        return self.model_name
    
    def _normalize_model_name(self, model_name: str) -> str:
        """Ensure LiteLLM-compatible format"""
        if model_name.startswith("models/"):
            model_name = model_name[7:]
        return f"gemini/{model_name}"


def create_crewai_compatible_llm():
    """Create a CrewAI-compatible LLM instance with proper model name formatting"""
    try:
        model_name = os.getenv("LLM_MODEL", "gemini-1.5-pro")
        
        llm = CrewAICompatibleLLM(
            model=model_name,
            google_api_key=os.getenv("GOOGLE_API_KEY"),
            temperature=float(os.getenv("LLM_TEMPERATURE", 0.7)),
            convert_system_message_to_human=True,
            max_tokens=None,
            verbose=True
        )
        
        logger.success(f"✅ Created CrewAI-compatible LLM: {str(llm)}")
        return llm
        
    except Exception as e:
        logger.error(f"❌ Failed to create CrewAI-compatible LLM: {e}")
        return None


# Create the global instance
crewai_llm = create_crewai_compatible_llm()
