"""
Unified LLM Client - The Main Entry Point.

This is the primary interface users will interact with.
It uses the Strategy Pattern to support multiple LLM providers.
"""

import os
import logging
from typing import Optional, List, Type, Dict, Any

from .strategies.base import LLMStrategy, ProviderError
from .strategies.anthropic import AnthropicStrategy
from .strategies.openai import OpenAIStrategy
from .strategies.ollama import OllamaStrategy
from .client import LLMResponse, Message, LLMClientError

logger = logging.getLogger(__name__)


# Registry of available providers
PROVIDER_REGISTRY: Dict[str, Type[LLMStrategy]] = {
    "anthropic": AnthropicStrategy,
    "openai": OpenAIStrategy,
    "ollama": OllamaStrategy,
}


class UnifiedLLMClient:
    """
    Unified LLM Client with provider switching.
    
    This is the main entry point for interacting with LLMs.
    It uses the Strategy Pattern to support multiple providers.
    """
    
    def __init__(
        self,
        provider: str = "anthropic",
        model: Optional[str] = None,
        **provider_kwargs
    ):
        self._provider_name = provider.lower()
        
        if self._provider_name not in PROVIDER_REGISTRY:
            raise ValueError(
                f"Unknown provider: {provider}. "
                f"Available: {list(PROVIDER_REGISTRY.keys())}"
            )
        
        strategy_class = PROVIDER_REGISTRY[self._provider_name]
        
        try:
            self._strategy = strategy_class(model=model, **provider_kwargs)
        except Exception as e:
            raise ProviderError(f"Failed to initialize {provider} provider: {e}") from e
        
        logger.info(f"Initialized LLM client with provider: {self._strategy.name}")
    
    @classmethod
    def from_env(cls, preferred_provider: str = "anthropic") -> "UnifiedLLMClient":
        """Create client auto-detecting from available API keys."""
        if os.environ.get("ANTHROPIC_API_KEY"):
            logger.info("Auto-detected Anthropic API key")
            return cls(provider="anthropic")
        
        if os.environ.get("OPENAI_API_KEY"):
            logger.info("Auto-detected OpenAI API key")
            return cls(provider="openai")
        
        logger.info(f"No API keys found, using: {preferred_provider}")
        return cls(provider=preferred_provider)
    
    @property
    def provider(self) -> str:
        return self._provider_name
    
    @property
    def model(self) -> str:
        return self._strategy.model
    
    @property
    def name(self) -> str:
        return self._strategy.name
    
    def set_provider(self, provider: str, model: Optional[str] = None, **provider_kwargs):
        """Switch to a different provider at runtime."""
        logger.info(f"Switching provider from {self.provider} to {provider}")
        
        self._provider_name = provider.lower()
        
        if self._provider_name not in PROVIDER_REGISTRY:
            raise ValueError(f"Unknown provider: {provider}")
        
        strategy_class = PROVIDER_REGISTRY[self._provider_name]
        
        try:
            self._strategy = strategy_class(model=model, **provider_kwargs)
            logger.info(f"Switched to: {self._strategy.name}")
        except Exception as e:
            raise ProviderError(f"Failed to switch to {provider}: {e}") from e
    
    def complete(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        messages: Optional[List[Message]] = None,
        **kwargs
    ) -> LLMResponse:
        """Generate completion from the LLM."""
        logger.debug(f"Calling {self._strategy.name} with prompt: {prompt[:50]}...")
        
        try:
            response = self._strategy.complete(
                prompt=prompt,
                system_prompt=system_prompt,
                messages=messages,
                **kwargs
            )
            
            logger.debug(f"Received response ({len(response.content)} chars)")
            return response
            
        except ProviderError as e:
            logger.error(f"Provider error: {e}")
            raise LLMClientError(str(e)) from e
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            raise LLMClientError(f"LLM call failed: {e}") from e
    
    def __str__(self) -> str:
        return f"UnifiedLLMClient(provider={self.provider}, model={self.model})"