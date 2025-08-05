"""
LiteLLM Custom Provider Configuration
This module configures LiteLLM to properly handle Google model names
and ensures correct model format mapping for CrewAI integration.
"""

import litellm
from loguru import logger


def custom_model_name(model):
    """Map Google model names to LiteLLM expected format"""
    if model.startswith("models/"):
        model = model.replace("models/", "gemini/")
    elif not model.startswith("gemini/"):
        model = f"gemini/{model}"
    return model


def configure_litellm():
    """Configure LiteLLM with custom model mapping"""
    try:
        # Register custom provider mapping
        litellm.model_alias_map = {
            "google_ai": custom_model_name
        }
        
        # Enable LiteLLM logging for debugging
        litellm.set_verbose = True
        
        logger.success("✅ Configured LiteLLM custom model mapping")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to configure LiteLLM: {e}")
        return False


# Apply configuration on import
configure_litellm()
