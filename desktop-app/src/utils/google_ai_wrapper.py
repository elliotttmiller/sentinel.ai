#!/usr/bin/env python3
"""
Custom Google Generative AI wrapper for LangChain compatibility.
"""

import os
import asyncio
from typing import Any, List, Optional, Iterator, Dict
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import BaseMessage, AIMessage, SystemMessage
from langchain_core.outputs import ChatResult, ChatGeneration
from langchain_core.pydantic_v1 import Field, PrivateAttr
import google.generativeai as genai
from loguru import logger
from dotenv import load_dotenv

# Load .env
env_path = os.path.join(os.path.dirname(__file__), '..', '..', '.env')
if os.path.exists(env_path):
    load_dotenv(env_path)
else:
    logger.warning(f".env file not found at {env_path}. Relying on env vars.")

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    logger.error("GOOGLE_API_KEY environment variable not found.")
else:
    try:
        genai.configure(api_key=GOOGLE_API_KEY)
        logger.success("Google Generative AI configured successfully.")
    except Exception as e:
        logger.error(f"Failed to configure Google Generative AI: {e}")

class GoogleGenerativeAIWrapper(BaseChatModel):
    model_name: str = Field(default="gemini-1.5-pro")
    temperature: float = Field(default=0.7)
    max_tokens: Optional[int] = Field(default=None)
    top_p: float = Field(default=1.0)
    top_k: int = Field(default=40)
    _model: Any = PrivateAttr()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._model = None

    @property
    def _llm_type(self) -> str:
        return "google_generative_ai_custom_wrapper"

    @property
    def model(self):
        if self._model is None:
            generation_config = genai.types.GenerationConfig(
                temperature=self.temperature,
                top_p=self.top_p,
                top_k=self.top_k,
                max_output_tokens=self.max_tokens,
            )
            self._model = genai.GenerativeModel(
                model_name=self.model_name,
                generation_config=generation_config
            )
            logger.debug(f"Google Generative AI model '{self.model_name}' initialized.")
        return self._model

    def _convert_messages_to_prompt(self, messages: List[BaseMessage]) -> str:
        prompt_parts = []
        for message in messages:
            role = "user"
            if isinstance(message, SystemMessage):
                prompt_parts.append(f"System Instruction: {message.content}")
            elif isinstance(message, AIMessage):
                role = "model"
                prompt_parts.append(f"{role}: {message.content}")
            else:
                prompt_parts.append(f"{role}: {message.content}")
        return "\n".join(prompt_parts)

    def _generate(self, messages: List[BaseMessage], stop: Optional[List[str]] = None, **kwargs: Any) -> ChatResult:
        return asyncio.run(self._agenerate(messages, stop, **kwargs))

    async def _agenerate(self, messages: List[BaseMessage], stop: Optional[List[str]] = None, **kwargs: Any) -> ChatResult:
        try:
            prompt = self._convert_messages_to_prompt(messages)
            safety_settings = {
                'HARM_CATEGORY_HARASSMENT': 'BLOCK_NONE',
                'HARM_CATEGORY_HATE_SPEECH': 'BLOCK_NONE',
                'HARM_CATEGORY_SEXUALLY_EXPLICIT': 'BLOCK_NONE',
                'HARM_CATEGORY_DANGEROUS_CONTENT': 'BLOCK_NONE',
            }
            response = await self.model.generate_content_async(
                prompt,
                safety_settings=safety_settings
            )
            content = response.text
            ai_message = AIMessage(content=content)
            generation = ChatGeneration(message=ai_message)
            return ChatResult(generations=[generation])
        except Exception as e:
            logger.error(f"Error during async Google AI generation: {e}")
            fallback_message = AIMessage(content=f"An error occurred: {e}")
            return ChatResult(generations=[ChatGeneration(message=fallback_message)])

    def _stream(self, messages: List[BaseMessage], stop: Optional[List[str]] = None, **kwargs: Any) -> Iterator[ChatGeneration]:
        try:
            prompt = self._convert_messages_to_prompt(messages)
            safety_settings = {
                'HARM_CATEGORY_HARASSMENT': 'BLOCK_NONE',
                'HARM_CATEGORY_HATE_SPEECH': 'BLOCK_NONE',
                'HARM_CATEGORY_SEXUALLY_EXPLICIT': 'BLOCK_NONE',
                'HARM_CATEGORY_DANGEROUS_CONTENT': 'BLOCK_NONE',
            }
            stream = self.model.generate_content(
                prompt,
                stream=True,
                safety_settings=safety_settings
            )
            for chunk in stream:
                if chunk.text:
                    yield ChatGeneration(message=AIMessage(content=chunk.text))
        except Exception as e:
            logger.error(f"Error during streaming Google AI generation: {e}")
            yield ChatGeneration(message=AIMessage(content=f"An error occurred during streaming: {e}"))

def create_google_ai_llm(model_name: str = "gemini-1.5-pro", temperature: float = 0.7, max_tokens: Optional[int] = None) -> Optional[GoogleGenerativeAIWrapper]:
    if not GOOGLE_API_KEY:
        logger.error("Cannot create LLM: GOOGLE_API_KEY is not configured.")
        return None
    return GoogleGenerativeAIWrapper(model_name=model_name, temperature=temperature, max_tokens=max_tokens)

class GoogleAIWrapper:
    def __init__(self):
        self.model = None
        if GOOGLE_API_KEY:
            try:
                self.model = genai.GenerativeModel("gemini-1.5-pro")
                logger.info("✅ Direct inference Google AI model initialized.")
            except Exception as e:
                logger.error(f"❌ Failed to initialize direct Google AI model: {e}")
    async def direct_inference(self, prompt: str) -> str:
        if not self.model:
            return "Error: Direct inference model not initialized. Check API key."
        try:
            response = await self.model.generate_content_async(prompt)
            return response.text
        except Exception as e:
            logger.error(f"❌ Direct inference failed: {e}")
            return f"Error during direct inference: {e}"

# CrewAI Integration - Missing Function Fix
def get_crewai_llm():
    """
    Returns a CrewAI-compatible LLM instance.
    This function was missing and causing agent initialization failures.
    """
    try:
        # Import here to avoid circular dependencies
        from langchain_google_genai import ChatGoogleGenerativeAI
        
        model_name = os.getenv("LLM_MODEL", "gemini-1.5-pro")
        temperature = float(os.getenv("LLM_TEMPERATURE", "0.7"))
        
        # Clean model name for proper LiteLLM compatibility
        if model_name.startswith("models/"):
            model_name = model_name.replace("models/", "")
        if model_name.startswith("gemini/"):
            model_name = model_name.replace("gemini/", "")
            
        logger.info(f"Creating CrewAI-compatible LLM with model: {model_name}")
        
        # Create LangChain wrapper
        llm = ChatGoogleGenerativeAI(
            model=model_name,
            google_api_key=GOOGLE_API_KEY,
            temperature=temperature,
            convert_system_message_to_human=True,
            max_tokens=None,
            verbose=True
        )
        
        logger.success(f"✅ CrewAI-compatible LLM initialized: {model_name}")
        return llm
        
    except Exception as e:
        logger.error(f"❌ Failed to create CrewAI-compatible LLM: {e}")
        # Return a fallback custom wrapper if LangChain fails
        try:
            logger.info("Attempting fallback to custom GoogleGenerativeAIWrapper...")
            return create_google_ai_llm()
        except Exception as fallback_error:
            logger.error(f"❌ Fallback also failed: {fallback_error}")
            return None

google_ai_wrapper = GoogleAIWrapper()
direct_inference = google_ai_wrapper.direct_inference