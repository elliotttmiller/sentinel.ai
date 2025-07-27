"""
Google GenAI Client for Project Sentinel.

This module provides a centralized interface for interacting with Google's Gemini API.
It handles authentication, model selection, and provides a clean interface for agents.
"""

import os
import json
from typing import Optional, Dict, Any, List
from loguru import logger
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
from config import settings


class GenAIClient:
    """
    Google GenAI client for Project Sentinel.
    
    Provides a centralized interface for interacting with Google's Gemini API.
    Handles authentication, model selection, and provides a clean interface for agents.
    """
    
    def __init__(self):
        self.logger = logger.bind(component="genai_client")
        self.model_name = settings.DEFAULT_MODEL
        self.client = None
        self.model = None
        
        # Initialize the client
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize the Google GenAI client with proper authentication."""
        try:
            # Set up API key
            api_key = self._get_api_key()
            if not api_key:
                self.logger.warning("No Google API key found. GenAI features will be limited.")
                return
            
            genai.configure(api_key=api_key)
            
            # Initialize the model
            self.model = genai.GenerativeModel(
                model_name=self.model_name,
                generation_config=self._get_generation_config(),
                safety_settings=self._get_safety_settings()
            )
            
            self.logger.info(f"GenAI client initialized with model: {self.model_name}")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize GenAI client: {e}")
            raise
    
    def _get_api_key(self) -> Optional[str]:
        """Get the Google API key from environment or settings."""
        # Try environment variable first
        api_key = os.getenv("GOOGLE_API_KEY")
        if api_key:
            return api_key
        
        # Try settings
        if settings.GOOGLE_API_KEY:
            return settings.GOOGLE_API_KEY
        
        # Try service account credentials
        if settings.GOOGLE_APPLICATION_CREDENTIALS_JSON:
            try:
                creds_data = json.loads(settings.GOOGLE_APPLICATION_CREDENTIALS_JSON)
                # For now, we'll use the API key approach
                # In the future, we can implement service account authentication
                return None
            except json.JSONDecodeError:
                self.logger.error("Invalid GOOGLE_APPLICATION_CREDENTIALS_JSON format")
                return None
        
        return None
    
    def _get_generation_config(self) -> Dict[str, Any]:
        """Get the generation configuration for the model."""
        return {
            "temperature": 0.7,
            "top_p": 0.9,
            "top_k": 40,
            "max_output_tokens": 8192,
        }
    
    def _get_safety_settings(self) -> List[Dict[str, Any]]:
        """Get safety settings for the model."""
        return [
            {
                "category": HarmCategory.HARM_CATEGORY_HARASSMENT,
                "threshold": HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            },
            {
                "category": HarmCategory.HARM_CATEGORY_HATE_SPEECH,
                "threshold": HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            },
            {
                "category": HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
                "threshold": HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            },
            {
                "category": HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
                "threshold": HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            },
        ]
    
    async def generate_response(
        self, 
        prompt: str, 
        system_prompt: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Generate a response using the Gemini model.
        
        Args:
            prompt: The user prompt
            system_prompt: Optional system prompt to define behavior
            context: Optional context information
            
        Returns:
            str: The generated response
        """
        try:
            if not self.model:
                return self._fallback_response(prompt)
            
            # Prepare the full prompt
            full_prompt = self._prepare_prompt(prompt, system_prompt, context)
            
            # Generate response
            response = self.model.generate_content(full_prompt)
            
            if response.text:
                self.logger.info(f"Generated response for prompt: {prompt[:100]}...")
                return response.text
            else:
                self.logger.warning("Empty response from GenAI model")
                return self._fallback_response(prompt)
                
        except Exception as e:
            self.logger.error(f"Error generating response: {e}")
            return self._fallback_response(prompt)
    
    def _prepare_prompt(
        self, 
        prompt: str, 
        system_prompt: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Prepare the full prompt with system prompt and context."""
        parts = []
        
        # Add system prompt if provided
        if system_prompt:
            parts.append(f"System: {system_prompt}")
        
        # Add context if provided
        if context:
            context_str = json.dumps(context, indent=2)
            parts.append(f"Context: {context_str}")
        
        # Add user prompt
        parts.append(f"User: {prompt}")
        
        return "\n\n".join(parts)
    
    def _fallback_response(self, prompt: str) -> str:
        """Provide a fallback response when GenAI is not available."""
        prompt_lower = prompt.lower()
        
        if "hello" in prompt_lower or "hi" in prompt_lower:
            return "Hello! I'm an AI assistant. I'm currently running in fallback mode without advanced language model capabilities."
        
        elif "help" in prompt_lower:
            return "I'm here to help! I'm currently running in fallback mode. For full AI capabilities, please ensure Google GenAI is properly configured."
        
        elif "status" in prompt_lower:
            return "Status: Running in fallback mode. Google GenAI integration is not fully configured."
        
        else:
            return f"I received your message: '{prompt}'\n\nI'm currently running in fallback mode. For enhanced AI responses, please configure Google GenAI integration."
    
    def is_available(self) -> bool:
        """Check if GenAI is properly configured and available."""
        return self.model is not None and self._get_api_key() is not None
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the current model configuration."""
        return {
            "model_name": self.model_name,
            "available": self.is_available(),
            "api_key_configured": self._get_api_key() is not None,
            "client_initialized": self.model is not None
        }


# Global instance
genai_client = GenAIClient() 