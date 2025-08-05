#!/usr/bin/env python3
import os
from loguru import logger
from langchain_google_genai import ChatGoogleGenerativeAI
import google.generativeai as genai

# Initialize a direct Google Generative AI model (non-agentic tasks)
try:
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
    direct_llm = genai.GenerativeModel(os.getenv("LLM_MODEL", "gemini-1.5-pro"))
    logger.success("✅ Initialized direct Google Generative AI model.")
except Exception as e:
    logger.error(f"❌ Failed to initialize direct Google AI model: {e}")
    direct_llm = None

# --- Dedicated, LangChain-compatible LLM for CrewAI ---
def get_crewai_llm():
    """Returns a properly formatted CrewAI-compatible LLM instance"""
    try:
        model_name = os.getenv("LLM_MODEL", "gemini-1.5-pro")
        
        # Normalize model name for LiteLLM compatibility
        # CrewAI expects: gemini/gemini-1.5-pro
        # Remove any existing prefixes
        if model_name.startswith("models/"):
            model_name = model_name[7:]
        if model_name.startswith("gemini/"):
            model_name = model_name[7:]
        
        # Format for LiteLLM
        formatted_model_name = f"gemini/{model_name}"
        
        crewai_llm = ChatGoogleGenerativeAI(
            model=model_name,  # Pass the clean name to Google API
            google_api_key=os.getenv("GOOGLE_API_KEY"),
            temperature=float(os.getenv("LLM_TEMPERATURE", 0.7)),
            convert_system_message_to_human=True,
            max_tokens=None,
            verbose=True
        )
        
        # Force-set model_name attribute to the formatted version
        crewai_llm.model_name = formatted_model_name
        
        logger.success(f"✅ Initialized CrewAI-compatible LLM: {formatted_model_name}")
        return crewai_llm
        
    except Exception as e:
        logger.error(f"❌ Failed to create CrewAI-compatible LLM: {e}")
        return None

# Create the global instance for convenience
crewai_llm = get_crewai_llm()

# Legacy compatibility function
def get_llm():
    """Returns the CrewAI-compatible LLM instance"""
    return crewai_llm if crewai_llm else get_crewai_llm()
