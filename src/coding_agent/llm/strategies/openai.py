"""
OpenAI GPT Strategy Implementation.

Provides the Strategy interface for OpenAI's GPT API.
"""

import os
import logging
import requests
from typing import Optional, List, Dict, Any

from .base import LLMStrategy, ProviderError
from ..client import LLMResponse, Message, APIKeyError, RateLimitError

logger = logging.getLogger(__name__)


class OpenAIStrategy(LLMStrategy):
    """Strategy implementation for OpenAI GPT API."""
    
    DEFAULT_MODEL = "gpt-3.5-turbo"
    GPT4_MODEL = "gpt-4"
    GPT4_TURBO = "gpt-4-turbo"
    GPT4O = "gpt-4o"
    
    MODEL_LIMITS = {
        "gpt-3.5-turbo": 16385,
        "gpt-4": 8192,
        "gpt-4-turbo": 128000,
        "gpt-4o": 128000,
    }
    
    def __init__(
        self,
        model: str = DEFAULT_MODEL,
        api_key: Optional[str] = None,
        base_url: str = "https://api.openai.com/v1",
        **kwargs
    ):
        super().__init__(model, **kwargs)
        self._api_key = api_key or os.environ.get("OPENAI_API_KEY")
        self._base_url = base_url.rstrip("/")
        
        if not self._api_key:
            raise APIKeyError(
                "OpenAI API key required. Set OPENAI_API_KEY "
                "environment variable or pass api_key to constructor."
            )
        
        if not self._api_key.startswith("sk-"):
            raise APIKeyError(
                "Invalid OpenAI API key format. Expected key starting with 'sk-'"
            )
        
        self._timeout = kwargs.get("timeout", 60)
        self._headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json"
        }
    
    @property
    def name(self) -> str:
        return f"OpenAI ({self._model})"
    
    @property
    def max_tokens(self) -> int:
        return self.MODEL_LIMITS.get(self._model, 4096)
    
    def complete(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        messages: Optional[List[Message]] = None,
        **kwargs
    ) -> LLMResponse:
        payload = self._build_payload(prompt, system_prompt, messages, **kwargs)
        
        try:
            response = requests.post(
                f"{self._base_url}/chat/completions",
                headers=self._headers,
                json=payload,
                timeout=self._timeout
            )
            return self._parse_response(response)
        except requests.exceptions.Timeout as e:
            raise ProviderError(f"Request timed out: {e}") from e
        except requests.exceptions.ConnectionError as e:
            raise ProviderError(f"Connection failed: {e}") from e
        except Exception as e:
            raise ProviderError(f"Unexpected error: {e}") from e
    
    def _build_payload(self, prompt, system_prompt, messages, **kwargs):
        api_messages = []
        if system_prompt:
            api_messages.append({"role": "system", "content": system_prompt})
        if messages:
            for msg in messages:
                api_messages.append({"role": msg.role, "content": msg.content})
        api_messages.append({"role": "user", "content": prompt})
        
        kwargs = self._prepare_kwargs(**kwargs)
        
        payload = {
            "model": self._model,
            "messages": api_messages,
            "temperature": kwargs.get("temperature", 1.0),
            "max_tokens": kwargs.get("max_tokens", self.max_tokens),
            "top_p": kwargs.get("top_p", 1.0),
        }
        
        if kwargs.get("stop"):
            payload["stop"] = kwargs["stop"]
        
        return payload
    
    def _parse_response(self, response) -> LLMResponse:
        if response.status_code == 200:
            data = response.json()
            choices = data.get("choices", [])
            if not choices:
                raise ProviderError("No choices in response")
            
            message = choices[0].get("message", {})
            content = message.get("content", "")
            usage = data.get("usage", {})
            
            return LLMResponse(
                content=content,
                model=data.get("model", self._model),
                usage={
                    "input_tokens": usage.get("prompt_tokens", 0),
                    "output_tokens": usage.get("completion_tokens", 0)
                },
                raw_response=data
            )
        elif response.status_code == 401:
            raise APIKeyError("Authentication failed. Check your API key.")
        elif response.status_code == 429:
            raise RateLimitError("Rate limit exceeded. Try again later.")
        else:
            raise ProviderError(f"API error ({response.status_code}): {response.text}")