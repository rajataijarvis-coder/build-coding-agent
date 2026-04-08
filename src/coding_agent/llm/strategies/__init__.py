"""
LLM Strategy Pattern Implementation.

This module provides a unified interface for different LLM providers
using the Strategy Pattern, allowing runtime switching between:
- Anthropic Claude
- OpenAI GPT
- Local Ollama
"""

from .base import LLMStrategy, ProviderError
from .anthropic import AnthropicStrategy
from .openai import OpenAIStrategy
from .ollama import OllamaStrategy

__all__ = [
    "LLMStrategy",
    "ProviderError", 
    "AnthropicStrategy",
    "OpenAIStrategy", 
    "OllamaStrategy",
]