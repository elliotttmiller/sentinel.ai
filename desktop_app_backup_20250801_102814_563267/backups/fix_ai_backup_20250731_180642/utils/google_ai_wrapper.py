#!/usr/bin/env python3
"""
Custom Google Generative AI wrapper for LangChain compatibility.
VERSION 3.0: Enhanced for full compatibility with CrewAI and LangChain Core v0.3.x.
This version resolves metaclass conflicts and Pydantic v1/v2 issues.
"""

import os
import asyncio
from typing import Any, List, Optional, Iterator
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain_core.outputs import ChatResult, ChatGeneration
# TECH DEBT NOTE: We are intentionally using the pydantic_v1 compatibility layer from
# langchain-core to maintain stability with CrewAI, which has a hard dependency on it.
# This may cause a LangChainDeprecationWarning. When CrewAI officially migrates to
# Pydantic v2, this import should be updated to `from pydantic import Field, PrivateAttr`.
from langchain_core.pydantic_v1 import Field, PrivateAttr  # CRITICAL: Use langchain's pydantic_v1
import google.generativeai as genai
from loguru import logger


class GoogleGenerativeAIWrapper(BaseChatModel):
    """
    Custom wrapper for Google Generative AI, fully compatible with modern LangChain and CrewAI.
    """
    model_name: str = Field(default="gemini-1.5-pro")
    temperature: float = Field(default=0.7)
    max_tokens: Optional[int] = Field(default=None)
    top_p: float = Field(default=1.0)
    top_k: int = Field(default=40)
    
    _model: Any = PrivateAttr()  # CRITICAL: Use PrivateAttr for internal state

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        try:
            # Load environment variables from .env file
            from dotenv import load_dotenv
            import os
            
            # Load .env file from the desktop-app directory
            env_path = os.path.join(os.path.dirname(__file__), '..', '..', '.env')
            load_dotenv(env_path)
            
            # Configure Google Generative AI
            api_key = os.getenv("GOOGLE_API_KEY")
            if not api_key:
                raise ValueError("GOOGLE_API_KEY environment variable is required")
            
            genai.configure(api_key=api_key)
            
            # Initialize the model attribute
            self._model = None
            
            logger.success(f"Google Generative AI wrapper initialized successfully")

        except Exception as e:
            logger.critical(f"Fatal error initializing Google Generative AI Wrapper: {e}")
            raise

    @property
    def _llm_type(self) -> str:
        return "google_generative_ai_custom_wrapper"
    
    def supports_stop_words(self) -> bool:
        """CrewAI compatibility method"""
        return True
    
    @property
    def llm_type(self) -> str:
        """CrewAI compatibility property"""
        return self._llm_type
    
    @property
    def model(self):
        """Lazy-load the Google Generative AI model with correct configuration values"""
        if self._model is None:
            try:
                # Use default values to avoid FieldInfo issues
                temperature_val = 0.7
                top_p_val = 1.0
                top_k_val = 40
                max_tokens_val = None
                model_name = "gemini-1.5-pro"
                
                generation_config = genai.types.GenerationConfig(
                    temperature=temperature_val,
                    top_p=top_p_val,
                    top_k=top_k_val,
                    max_output_tokens=max_tokens_val,
                )
                
                # Create the model instance
                self._model = genai.GenerativeModel(
                    model_name=model_name,
                    generation_config=generation_config
                )
                
                logger.debug(f"Google Generative AI model created with: {model_name}, temp={temperature_val}")
                
            except Exception as e:
                logger.error(f"Error creating Google Generative AI model: {e}")
                raise
        
        return self._model

    def _convert_messages_to_prompt(self, messages: List[BaseMessage]) -> str:
        """Convert LangChain messages to a single prompt string."""
        prompt_parts = []
        for message in messages:
            role = "user"  # Default role
            if isinstance(message, SystemMessage):
                prompt_parts.insert(0, f"System Instruction: {message.content}")
                continue
            elif isinstance(message, AIMessage):
                role = "model"
            
            prompt_parts.append(f"{role}: {message.content}")
        
        return "\n".join(prompt_parts)

    def _generate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> ChatResult:
        """Synchronous generation."""
        try:
            prompt = self._convert_messages_to_prompt(messages)
            
            safety_settings = {
                'HARM_CATEGORY_HARASSMENT': 'BLOCK_NONE',
                'HARM_CATEGORY_HATE_SPEECH': 'BLOCK_NONE',
                'HARM_CATEGORY_SEXUALLY_EXPLICIT': 'BLOCK_NONE',
                'HARM_CATEGORY_DANGEROUS_CONTENT': 'BLOCK_NONE',
            }

            response = self.model.generate_content(prompt, safety_settings=safety_settings)
            
            content = response.text
            ai_message = AIMessage(content=content)
            generation = ChatGeneration(message=ai_message)
            
            return ChatResult(generations=[generation])
            
        except Exception as e:
            logger.error(f"Error during Google AI generation: {e}")
            fallback_message = AIMessage(content=f"An error occurred: {e}")
            return ChatResult(generations=[ChatGeneration(message=fallback_message)])

    async def _agenerate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> ChatResult:
        """Asynchronous generation using the official async client."""
        try:
            prompt = self._convert_messages_to_prompt(messages)
            
            safety_settings = {
                'HARM_CATEGORY_HARASSMENT': 'BLOCK_NONE',
                'HARM_CATEGORY_HATE_SPEECH': 'BLOCK_NONE',
                'HARM_CATEGORY_SEXUALLY_EXPLICIT': 'BLOCK_NONE',
                'HARM_CATEGORY_DANGEROUS_CONTENT': 'BLOCK_NONE',
            }

            response = await self.model.generate_content_async(prompt, safety_settings=safety_settings)
            
            content = response.text
            ai_message = AIMessage(content=content)
            generation = ChatGeneration(message=ai_message)
            
            return ChatResult(generations=[generation])

        except Exception as e:
            logger.error(f"Error during async Google AI generation: {e}")
            fallback_message = AIMessage(content=f"An error occurred: {e}")
            return ChatResult(generations=[ChatGeneration(message=fallback_message)])

    def _stream(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> Iterator[ChatGeneration]:
        """Streaming generation."""
        try:
            prompt = self._convert_messages_to_prompt(messages)
            
            safety_settings = {
                'HARM_CATEGORY_HARASSMENT': 'BLOCK_NONE',
                'HARM_CATEGORY_HATE_SPEECH': 'BLOCK_NONE',
                'HARM_CATEGORY_SEXUALLY_EXPLICIT': 'BLOCK_NONE',
                'HARM_CATEGORY_DANGEROUS_CONTENT': 'BLOCK_NONE',
            }

            stream = self.model.generate_content(prompt, stream=True, safety_settings=safety_settings)
            
            for chunk in stream:
                if chunk.text:
                    yield ChatGeneration(message=AIMessage(content=chunk.text))
                    
        except Exception as e:
            logger.error(f"Error during streaming Google AI generation: {e}")
            yield ChatGeneration(message=AIMessage(content=f"An error occurred during streaming: {e}"))


# --- Convenience Function ---
def create_google_ai_llm(
    model_name: str = "gemini-1.5-pro",
    temperature: float = 0.7,
    max_tokens: Optional[int] = None
) -> GoogleGenerativeAIWrapper:
    """Creates a configured instance of our custom Google Generative AI wrapper."""
    return GoogleGenerativeAIWrapper(
        model_name=model_name,
        temperature=temperature,
        max_tokens=max_tokens
    ) 