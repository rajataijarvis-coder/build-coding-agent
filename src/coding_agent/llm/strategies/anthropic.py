"""
Anthropic Claude Strategy Implementation.

Provides the Strategy interface for Anthropic's Claude API.
"""

import os
import logging
import requests
from typing import Optional, List, Dict, Any

from .base import LLMStrategy, ProviderError
from ..client import LLMResponse, Message, APIKeyError, RateLimitError

logger = logging.getLogger(__name__)


class AnthropicStrategy(LLMStrategy):
    """Strategy implementation for Anthropic Claude API."""
    
    DEFAULT_MODEL = "claude-3-haiku-20240307"
    SONNET_MODEL = "claude-3-sonnet-20240229"
    OPUS_MODEL = "claude-3-opus-20240229"
    
    MODEL_LIMITS = {
        "claude-3-haiku-20240307": 4096,
        "claude-3-sonnet-20240229": 4096,
        "claude-3-opus-20240229": 4096,
    }
    
    def __init__(
        self,
        model: str = DEFAULT_MODEL,
        api_key: Optional[str] = None,
        **kwargs
    ):
        super().__init__(model, **kwargs)
        self._api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        
        if not self._api_key:
            raise APIKeyError(
                "Anthropic API key required. Set ANTHROPIC_API_KEY "
                "environment variable or pass api_key to constructor."
            )
        
        if not self._api_key.startswith("sk-ant-"):
            raise APIKeyError(
                "Invalid Anthropic API key format. Expected key starting with 'sk-ant-'"
            )
        
        self._timeout = kwargs.get("timeout", 60)
        self._headers = {
            "x-api-key": self._api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }
    
    @property
    def name(self) -> str:
        return f"Anthropic Claude ({self._model})"
    
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
                "https://api.anthropic.com/v1/messages",
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
        if messages:
            for msg in messages:
                api_messages.append({"role": msg.role, "content": msg.content})
        
        if system_prompt:
            api_messages.append({"role": "user", "content": f"{system_prompt}\n\n{prompt}"})
        else:
            api_messages.append({"role": "user", "content": prompt})
        
        kwargs = self._prepare_kwargs(**kwargs)
        
        return {
            "model": self._model,
            "messages": api_messages,
            "max_tokens": kwargs.get("max_tokens", self.max_tokens),
            "temperature": kwargs.get("temperature", 1.0),
            "top_p": kwargs.get("top_p", 1.0),
        }
    
    def _parse_response(self, response) -> LLMResponse:
        if response.status_code == 200:
            data = response.json()
            content_blocks = data.get("content", [])
            text_content = ""
            for block in content_blocks:
                if block.get("type") == "text":
                    text_content += block.get("text", "")
            
            usage = data.get("usage", {})
            return LLMResponse(
                content=text_content,
                model=data.get("model", self._model),
                usage={
                    "input_tokens": usage.get("input_tokens", 0),
                    "output_tokens": usage.get("output_tokens", 0)
                },
                raw_response=data
            )
        elif response.status_code == 401:
            raise APIKeyError("Authentication failed. Check your API key.")
        elif response.status_code == 429:
            raise RateLimitError("Rate limit exceeded. Try again later.")
        else:
            raise ProviderError(f"API error ({response.status_code}): {response.text}")