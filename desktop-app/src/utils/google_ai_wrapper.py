#!/usr/bin/env python3
import os
from loguru import logger
from langchain_google_genai import ChatGoogleGenerativeAI
import google.generativeai as genai

# This direct_llm is for non-agentic tasks and can remain as is.
try:
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
    llm = genai.GenerativeModel(os.getenv("LLM_MODEL", "gemini-1.5-pro"))
    logger.success("✅ Initialized direct Google Generative AI model.")
except Exception as e:
    logger.error(f"❌ Failed to initialize direct Google AI model: {e}")
    llm = None


class CrewAICompatibleLLM(ChatGoogleGenerativeAI):
    """
    Custom wrapper for ChatGoogleGenerativeAI that ensures the model name
    is formatted correctly for litellm used by CrewAI.
    
    The issue is that ChatGoogleGenerativeAI adds 'models/' prefix internally,
    resulting in 'models/gemini/model-name' being passed to litellm,
    but litellm expects just 'gemini/model-name' format.
    """
    _litellm_model_name: str
    
    def __init__(self, *args, **kwargs):
        # Extract the model name before calling super().__init__
        model_name = kwargs.get('model', 'gemini-1.5-pro')
        
        # Clean the model name - ensure it's just the model name without any prefixes
        if '/' in model_name:
            clean_model_name = model_name.split('/')[-1]
        else:
            clean_model_name = model_name
            
        # Store the correct format that litellm expects
        self._litellm_model_name = f"gemini/{clean_model_name}"
        
        # Pass the clean model name to the parent class
        kwargs['model'] = clean_model_name
        
        super().__init__(*args, **kwargs)
        
        logger.success(f"✅ CrewAI-compatible LLM initialized with litellm format: {self._litellm_model_name}")
    
    @property
    def _llm_type(self) -> str:
        """Override to return the correct model name for litellm"""
        return self._litellm_model_name
    
    def _get_model_name(self) -> str:
        """Override to return the correct model name for litellm"""
        return self._litellm_model_name
    
    def __str__(self) -> str:
        """String representation should show the litellm format"""
        return f"CrewAICompatibleLLM(model='{self._litellm_model_name}')"


# --- Dedicated, LangChain-compatible LLM for CrewAI ---
def get_crewai_llm():
    """
    Returns a CrewAI-compatible ChatGoogleGenerativeAI instance
    configured specifically for use with CrewAI and its underlying litellm library.
    """
    try:
        model_name = os.getenv("LLM_MODEL", "gemini-1.5-pro")

        crew_llm = CrewAICompatibleLLM(
            model=model_name,
            google_api_key=os.getenv("GOOGLE_API_KEY"),
            temperature=float(os.getenv("LLM_TEMPERATURE", 0.7)),
            convert_system_message_to_human=True
        )
        
        logger.success(f"✅ Initialized CrewAI-compatible Google Generative AI LLM with model: {crew_llm._litellm_model_name}")
        return crew_llm
    except Exception as e:
        logger.error(f"❌ Failed to create CrewAI-compatible LLM. Real agent execution will fail. Error: {e}")
        return None

# The global instance for convenience, created via the corrected function.
crewai_llm = get_crewai_llm()

# For backward compatibility with other modules that might be using these
create_google_ai_llm = get_crewai_llm
