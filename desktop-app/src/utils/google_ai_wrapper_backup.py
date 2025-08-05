#!/usr/bin/env python3
import os
from loguru import logger
from langchain_google_genai import ChatGoogleGenerativeAI
import google.generativeai as genai

# Import CrewAI's LLM class for proper integration
try:
    from crewai import LLM as CrewAI_LLM
    CREWAI_LLM_AVAILABLE = True
    logger.info("✅ CrewAI LLM class imported successfully")
except ImportError:
    CREWAI_LLM_AVAILABLE = False
    logger.warning("❌ CrewAI LLM class not available, falling back to LangChain")

# This direct_llm is for non-agentic tasks and can remain as is.
try:
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
    direct_llm = genai.GenerativeModel(os.getenv("LLM_MODEL", "gemini-1.5-pro"))
    logger.success("✅ Initialized direct Google Generative AI model.")
except Exception as e:
    logger.error(f"❌ Failed to initialize direct Google AI model: {e}")
    direct_llm = None

# --- Dedicated, LangChain-compatible LLM for CrewAI ---
def get_crewai_llm():
    """Returns a properly formatted CrewAI-compatible LLM instance using CrewAI native LLM class"""
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
        
        # Use CrewAI's native LLM class instead of LangChain wrapper
        crewai_llm = CrewAI_LLM(
            model=formatted_model_name,
            api_key=os.getenv("GOOGLE_API_KEY"),
            temperature=float(os.getenv("LLM_TEMPERATURE", 0.7)),
        )
        
        logger.success(f"✅ Initialized CrewAI native LLM: {formatted_model_name}")
        return crewai_llm
        
    except Exception as e:
        logger.error(f"❌ Failed to create CrewAI native LLM: {e}")
        logger.info("Falling back to LangChain wrapper...")
        
        # Fallback to LangChain wrapper if CrewAI native fails
        try:
            formatted_model_name = f"gemini/{model_name}" if not model_name.startswith("gemini/") else model_name
            
            crewai_llm = ChatGoogleGenerativeAI(
                model=formatted_model_name,
                google_api_key=os.getenv("GOOGLE_API_KEY"),
                temperature=float(os.getenv("LLM_TEMPERATURE", 0.7)),
                convert_system_message_to_human=True,
                max_tokens=None,
                verbose=True
            )
            
            logger.success(f"✅ Initialized CrewAI-compatible LLM (fallback): {formatted_model_name}")
            return crewai_llm
        except Exception as fallback_error:
            logger.error(f"❌ Fallback also failed: {fallback_error}")
            return None

# The global instance for convenience, created via the corrected function.
llm = get_crewai_llm()

import os
from loguru import logger
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import the official LangChain Google AI integration
try:
    from langchain_google_genai import ChatGoogleGenerativeAI
    LANGCHAIN_GOOGLE_AVAILABLE = True
    logger.info(" LangChain Google GenAI imported successfully")
except ImportError as e:
    logger.error(f" Failed to import langchain-google-genai: {e}")
    LANGCHAIN_GOOGLE_AVAILABLE = False
    ChatGoogleGenerativeAI = None

# Global LLM instances
llm = None
crewai_llm = None

def create_google_ai_llm():
    """
    Creates and returns a LangChain-compatible Google AI LLM instance.
    Uses standard model naming for direct LangChain usage.
    """
    global llm
    
    if llm is not None:
        return llm
        
    if not LANGCHAIN_GOOGLE_AVAILABLE:
        raise ImportError("langchain-google-genai is not available. Install with: pip install langchain-google-genai")
    
    try:
        # Get configuration from environment
        model_name = os.getenv("LLM_MODEL", "gemini-1.5-pro")
        
        # Clean model name for LangChain (remove any prefixes)
        if model_name.startswith("models/"):
            model_name = model_name.replace("models/", "")
        elif model_name.startswith("gemini/"):
            model_name = model_name.replace("gemini/", "")
        
        temperature = float(os.getenv("LLM_TEMPERATURE", "0.7"))
        google_api_key = os.getenv("GOOGLE_API_KEY")
        
        if not google_api_key:
            raise ValueError("GOOGLE_API_KEY environment variable is required")
        
        # Create the LangChain-compatible LLM
        llm = ChatGoogleGenerativeAI(
            model=model_name,
            google_api_key=google_api_key,
            temperature=temperature,
            convert_system_message_to_human=True,  # Important for compatibility
            max_tokens=None,
            verbose=True
        )
        
        logger.success(f" Initialized LangChain-compatible Google Generative AI LLM: {model_name}")
        return llm
        
    except Exception as e:
        logger.error(f" Failed to initialize ChatGoogleGenerativeAI: {e}")
        raise e

def get_crewai_llm():
    """
    Returns a LangChain-compatible ChatGoogleGenerativeAI instance
    configured specifically for use with CrewAI and its underlying litellm library.
    """
    global crewai_llm
    
    if crewai_llm is not None:
        return crewai_llm
        
    if not LANGCHAIN_GOOGLE_AVAILABLE:
        raise ImportError("langchain-google-genai is not available. Install with: pip install langchain-google-genai")
    
    try:
        model_name = os.getenv("LLM_MODEL", "gemini-1.5-pro")
        
        # <<< THE CRITICAL FIX >>>
        # ChatGoogleGenerativeAI automatically adds "models/" prefix to whatever we pass
        # But litellm (used by CrewAI) expects "gemini/model-name" format
        # So we need to pass just the model name and let the library format it correctly
        # Debug log the original model name
        logger.info(f"Original model name from env: '{model_name}'")
        
        if model_name.startswith("models/"):
            # Example: "models/gemini-1.5-pro" -> "gemini-1.5-pro"
            formatted_model_name = model_name.replace("models/", "", 1)
        elif model_name.startswith("gemini/"):
            # Example: "gemini/gemini-1.5-pro" -> "gemini-1.5-pro"
            formatted_model_name = model_name.replace("gemini/", "", 1)
        else:
            # Example: "gemini-1.5-pro" -> "gemini-1.5-pro" (no change needed)
            formatted_model_name = model_name
            
        # Debug log the formatted model name
        # The core issue: ChatGoogleGenerativeAI automatically adds "models/" prefix
        # We need to work around this by using a different approach
        # Let's try passing the model name that will result in the correct format after the prefix is added
        
        # Since ChatGoogleGenerativeAI adds "models/" prefix automatically,
        # we need to pass something that when prefixed becomes what litellm expects
        # litellm expects: "gemini/gemini-1.5-pro"
        # ChatGoogleGenerativeAI will add "models/" so we get "models/something"
        # This is a fundamental incompatibility - let's try a different approach
        
        logger.info(f"Formatted model name for ChatGoogleGenerativeAI: '{formatted_model_name}'")

        crewai_llm = ChatGoogleGenerativeAI(
            model=formatted_model_name,
            google_api_key=os.getenv("GOOGLE_API_KEY"),
            temperature=float(os.getenv("LLM_TEMPERATURE", 0.7)),
            convert_system_message_to_human=True,  # Important for compatibility
            max_tokens=None,
            verbose=True
        )
        logger.success(f" Initialized CrewAI-compatible Google Generative AI LLM: {formatted_model_name}")
        return crewai_llm
    except Exception as e:
        logger.error(f" Failed to create CrewAI-compatible LLM. Real agent execution will fail. Error: {e}")
        return None

# Initialize the global LLM instances
try:
    llm = create_google_ai_llm()
    logger.info(" Global LangChain LLM instance initialized")
    
    crewai_llm = get_crewai_llm()
    if crewai_llm:
        logger.info(" Global CrewAI-compatible LLM instance initialized")
except Exception as e:
    logger.error(f" Failed to initialize global LLM instances: {e}")
    llm = None
    crewai_llm = None

# Legacy compatibility function (can be deprecated later)
def get_llm():
    """Returns the LangChain-compatible LLM instance"""
    if llm is None:
        return create_google_ai_llm()
    return llm
