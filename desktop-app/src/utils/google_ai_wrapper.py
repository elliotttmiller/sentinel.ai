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

# --- Dedicated, LangChain-compatible LLM for CrewAI ---
def get_crewai_llm():
    """
    Returns a LangChain-compatible ChatGoogleGenerativeAI instance
    configured specifically for use with CrewAI and its underlying litellm library.
    """
    try:
        model_name = os.getenv("LLM_MODEL", "gemini-1.5-pro")

        # <<< THE DEFINITIVE FIX >>>
        # litellm expects the format "provider/model-name".
        # We will intelligently format the string from our .env to be compatible.
        
        # 1. Strip any existing incorrect prefixes to get a clean model name.
        clean_model_name = model_name.split('/')[-1]
        
        # 2. Add the correct 'gemini/' prefix that litellm requires.
        formatted_model_name = f"gemini/{clean_model_name}"

        crew_llm = ChatGoogleGenerativeAI(
            model=formatted_model_name,
            google_api_key=os.getenv("GOOGLE_API_KEY"),
            temperature=float(os.getenv("LLM_TEMPERATURE", 0.7)),
            convert_system_message_to_human=True
        )
        logger.success(f"✅ Initialized CrewAI-compatible Google Generative AI LLM with model: {formatted_model_name}")
        return crew_llm
    except Exception as e:
        logger.error(f"❌ Failed to create CrewAI-compatible LLM. Real agent execution will fail. Error: {e}")
        return None

# The global instance for convenience, created via the corrected function.
crewai_llm = get_crewai_llm()

# For backward compatibility with other modules that might be using these
create_google_ai_llm = get_crewai_llm
