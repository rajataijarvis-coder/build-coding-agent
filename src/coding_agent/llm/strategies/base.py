"""
Base Strategy Interface for LLM Providers.

This defines the contract that all LLM providers must implement.
"""

from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
import logging

from ..client import LLMResponse, Message

logger = logging.getLogger(__name__)


class ProviderError(Exception):
    """Base exception for provider-specific errors."""
    pass


class LLMStrategy(ABC):
    """
    Abstract base class for LLM providers.
    
    This defines the interface that all LLM implementations must follow,
    enabling the Strategy Pattern for provider switching.
    """
    
    def __init__(self, model: str = "default", **kwargs):
        self._model = model
        self._config = kwargs
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Return a human-readable name for this provider."""
        pass
    
    @property
    def model(self) -> str:
        """Get the model identifier."""
        return self._model
    
    @property
    def max_tokens(self) -> int:
        """Maximum tokens the model can handle."""
        return 4096
    
    @abstractmethod
    def complete(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        messages: Optional[List[Message]] = None,
        **kwargs
    ) -> LLMResponse:
        """Generate a completion from the LLM."""
        pass
    
    def _prepare_kwargs(self, **kwargs) -> Dict[str, Any]:
        """Prepare kwargs with sensible defaults."""
        return {
            "temperature": kwargs.get("temperature", 1.0),
            "max_tokens": kwargs.get("max_tokens", self.max_tokens),
            "top_p": kwargs.get("top_p", 1.0),
            "stop": kwargs.get("stop", None),
            **kwargs
        }
    
    def __str__(self) -> str:
        return f"{self.__class__.__name__}(model={self._model})"