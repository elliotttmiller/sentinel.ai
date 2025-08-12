"""
LiteLLM Custom Provider Configuration
This module configures LiteLLM to properly handle Google model names
and ensures correct model format mapping for CrewAI integration.
"""

import os
from loguru import logger

def custom_model_name(model):
    """Map Google model names to LiteLLM expected format"""
    logger.debug(f"Mapping model name: {model}")
    
    # Handle the specific case where models/ prefix is added by langchain
    if model.startswith("models/gemini"):
        # Extract just the model name after the last slash
        clean_name = model.split('/')[-1]
        result = f"gemini/{clean_name}"
        logger.debug(f"Mapped models/gemini format: {model} -> {result}")
        return result
    elif model.startswith("models/"):
        # Remove models/ prefix and add gemini/ prefix
        clean_name = model.replace("models/", "")
        result = f"gemini/{clean_name}"
        logger.debug(f"Mapped models/ format: {model} -> {result}")
        return result
    elif not model.startswith("gemini/"):
        # Add gemini/ prefix if not present
        result = f"gemini/{model}"
        logger.debug(f"Added gemini prefix: {model} -> {result}")
        return result
    else:
        # Already in correct format
        logger.debug(f"Model already in correct format: {model}")
        return model


def configure_litellm():
    """Configure LiteLLM with custom model mapping"""
    try:
        # Import litellm here to avoid circular imports
        import litellm
        
        # Override the model mapping function
        original_get_llm_provider = litellm.get_llm_provider
        
        def custom_get_llm_provider(model, *args, **kwargs):
            """Custom provider function that handles model name mapping"""
            # Apply our custom model name mapping
            mapped_model = custom_model_name(model)
            logger.debug(f"LiteLLM provider lookup: {model} mapped to {mapped_model}")
            
            # Call original function with mapped model name
            return original_get_llm_provider(mapped_model, *args, **kwargs)
        
        # Replace the function
        litellm.get_llm_provider = custom_get_llm_provider
        
        # Also set verbose logging if debug is enabled
        if os.getenv("LOG_LEVEL", "INFO") == "DEBUG":
            litellm.set_verbose = True
        
        logger.success("✅ Configured LiteLLM custom model mapping")
        return True
        
    except ImportError:
        logger.warning("⚠️  LiteLLM not available, skipping custom configuration")
        return False
    except Exception as e:
        logger.error(f"❌ Failed to configure LiteLLM: {e}")
        return False


# Apply configuration on import
configure_litellm()
