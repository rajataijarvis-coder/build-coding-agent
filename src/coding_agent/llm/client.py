"""
LLM Client Module - Handles communication with LLM providers.

This module provides a unified interface for different LLM backends:
- Anthropic Claude
- OpenAI GPT
- Local Ollama

The client follows the Strategy pattern, allowing easy swapping
of providers without changing the core agent logic.
"""

import os
import json
import logging
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field
from datetime import datetime


logger = logging.getLogger(__name__)


@dataclass
class Message:
    """Represents a single message in the conversation."""
    
    role: str  # "system", "user", or "assistant"
    content: str
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, str]:
        """Convert to dictionary format for API calls."""
        return {
            "role": self.role,
            "content": self.content
        }


@dataclass
class LLMResponse:
    """Structured response from an LLM."""
    
    content: str
    model: str
    usage: Dict[str, int] = field(default_factory=dict)
    raw_response: Optional[Dict[str, Any]] = None
    timestamp: datetime = field(default_factory=datetime.now)
    
    def __str__(self) -> str:
        return self.content


class LLMClientError(Exception):
    """Base exception for LLM client errors."""
    pass


class APIKeyError(LLMClientError):
    """Raised when API key is missing or invalid."""
    pass


class RateLimitError(LLMClientError):
    """Raised when rate limit is exceeded."""
    pass


class APIError(LLMClientError):
    """Raised when API returns an error."""
    
    def __init__(self, message: str, status_code: Optional[int] = None):
        super().__init__(message)
        self.status_code = status_code