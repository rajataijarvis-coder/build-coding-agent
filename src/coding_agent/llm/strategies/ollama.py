"""
Ollama Local LLM Strategy Implementation.

Provides the Strategy interface for local Ollama models.
"""

import logging
import requests
from typing import Optional, List, Dict, Any

from .base import LLMStrategy, ProviderError
from ..client import LLMResponse, Message

logger = logging.getLogger(__name__)


class OllamaStrategy(LLMStrategy):
    """Strategy implementation for local Ollama models."""
    
    DEFAULT_MODEL = "llama2"
    
    MODEL_LIMITS = {
        "llama2": 4096,
        "codellama": 4096,
        "mistral": 4096,
        "mixtral": 4096,
        "phi": 2048,
    }
    
    def __init__(
        self,
        model: str = DEFAULT_MODEL,
        base_url: str = "http://localhost:11434",
        **kwargs
    ):
        super().__init__(model, **kwargs)
        self._base_url = base_url.rstrip("/")
        self._timeout = kwargs.get("timeout", 120)
        self._headers = {"Content-Type": "application/json"}
        self._verify_connection()
    
    def _verify_connection(self):
        try:
            response = requests.get(f"{self._base_url}/api/tags", timeout=5)
            if response.status_code != 200:
                logger.warning(f"Ollama server returned {response.status_code}")
        except Exception as e:
            logger.warning(f"Could not connect to Ollama: {e}")
    
    @property
    def name(self) -> str:
        return f"Ollama ({self._model})"
    
    @property
    def max_tokens(self) -> int:
        return self.MODEL_LIMITS.get(self._model, 2048)
    
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
                f"{self._base_url}/api/generate",
                headers=self._headers,
                json=payload,
                timeout=self._timeout
            )
            return self._parse_response(response)
        except requests.exceptions.Timeout as e:
            raise ProviderError(f"Request timed out: {e}") from e
        except requests.exceptions.ConnectionError as e:
            raise ProviderError(f"Could not connect to Ollama: {e}") from e
        except Exception as e:
            raise ProviderError(f"Unexpected error: {e}") from e
    
    def _build_payload(self, prompt, system_prompt, messages, **kwargs):
        full_prompt = ""
        if system_prompt:
            full_prompt += f"System: {system_prompt}\n\n"
        if messages:
            for msg in messages:
                full_prompt += f"{msg.role.capitalize()}: {msg.content}\n"
        full_prompt += f"User: {prompt}\n"
        
        kwargs = self._prepare_kwargs(**kwargs)
        
        return {
            "model": self._model,
            "prompt": full_prompt,
            "stream": False,
            "options": {
                "temperature": kwargs.get("temperature", 1.0),
                "num_predict": kwargs.get("max_tokens", self.max_tokens),
                "top_p": kwargs.get("top_p", 1.0),
            }
        }
    
    def _parse_response(self, response) -> LLMResponse:
        if response.status_code == 200:
            data = response.json()
            content = data.get("response", "")
            prompt_tokens = data.get("prompt_eval_count", 0)
            output_tokens = data.get("eval_count", 0)
            
            return LLMResponse(
                content=content,
                model=self._model,
                usage={"input_tokens": prompt_tokens, "output_tokens": output_tokens},
                raw_response=data
            )
        else:
            raise ProviderError(f"Ollama error ({response.status_code}): {response.text}")