from langchain_core.messages import AIMessageChunk
#!/usr/bin/env python3
"""
Custom Google Generative AI wrapper for LangChain compatibility.
"""

import os
from typing import Any, Optional, List, Iterator
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.pydantic_v1 import Field, PrivateAttr
from langchain_core.messages import BaseMessage, AIMessage
from langchain_core.outputs.chat_generation import ChatGeneration
from langchain_core.outputs.chat_result import ChatResult
from langchain_core.outputs.chat_generation import ChatGenerationChunk
from langchain_core.callbacks.manager import AsyncCallbackManagerForLLMRun, CallbackManagerForLLMRun
from google.generativeai.generative_models import GenerativeModel
from loguru import logger
from dotenv import load_dotenv
import asyncio

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
    logger.success("Google Generative AI API key loaded successfully.")

class GoogleGenerativeAIWrapper(BaseChatModel):
    @property
    def _llm_type(self) -> str:
        return "google_generative_ai"
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
    def model(self):
        if self._model is None:
            self._model = GenerativeModel(self.model_name)
            logger.debug(f"Google Generative AI model '{self.model_name}' initialized.")
        return self._model
    def _convert_messages_to_prompt(self, messages: List[BaseMessage]) -> str:
        prompt_parts = []
        for message in messages:
            role = "user"
            if message.type == "system":
                prompt_parts.append(f"System Instruction: {message.content}")
            elif message.type == "ai":
                role = "model"
                prompt_parts.append(f"{role}: {message.content}")
            else:
                prompt_parts.append(f"{role}: {message.content}")
        return "\n".join(prompt_parts)
        return "\n".join(prompt_parts)

    def _generate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any
    ) -> ChatResult:
        # Only pass run_manager if it's of correct type
        return asyncio.run(self._agenerate(messages, stop=stop, run_manager=None, **kwargs))

    async def _agenerate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[AsyncCallbackManagerForLLMRun] = None,
        **kwargs: Any
    ) -> ChatResult:
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

    def _stream(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any
    ) -> Iterator[ChatGenerationChunk]:
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
                    # Use content directly for chunk, not AIMessage
                    yield ChatGenerationChunk(message=chunk.text)
        except Exception as e:
            logger.error(f"Error during streaming Google AI generation: {e}")
            # Yield a chunk with error text using AIMessageChunk
            yield ChatGenerationChunk(message=AIMessageChunk(content=f"An error occurred during streaming: {e}"))

    async def direct_inference(self, prompt: str) -> str:
        if not self.model:
            return "Error: Direct inference model not initialized. Check API key."
        try:
            response = await self.model.generate_content_async(prompt)
            return response.text
        except Exception as e:
            logger.error(f"❌ Direct inference failed: {e}")
            return f"Error during direct inference: {e}"
