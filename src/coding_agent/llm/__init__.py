"""
LLM Module - Unified interface for multiple LLM providers.

This module provides a consistent API for interacting with:
- Anthropic Claude
- OpenAI GPT  
- Local Ollama

Usage:
    from coding_agent.llm import UnifiedLLMClient
    
    # Auto-detect provider from environment
    client = UnifiedLLMClient.from_env()
    
    # Or specify explicitly
    client = UnifiedLLMClient(provider="anthropic", model="claude-3-haiku")
    
    # Make requests
    response = client.complete("Hello, world!")
    print(response.content)
"""

from typing import Optional

from .client import (
    Message,
    LLMResponse,
    LLMClientError,
    APIKeyError,
    RateLimitError,
    APIError
)
from .unified import UnifiedLLMClient, PROVIDER_REGISTRY
from .strategies.base import LLMStrategy, ProviderError


def create_client(
    provider: str = "anthropic",
    api_key: Optional[str] = None,
    model: Optional[str] = None,
    **kwargs
) -> UnifiedLLMClient:
    """
    Factory function to create an LLM client.
    
    Args:
        provider: "anthropic", "openai", or "ollama"
        api_key: API key for the provider
        model: Optional model override
        **kwargs: Additional provider-specific arguments
    
    Returns:
        Configured LLM client instance
    
    Example:
        # Create Anthropic client
        client = create_client("anthropic", model="claude-3-sonnet")
        
        # Get completion
        response = client.complete("Hello!")
        
        # Switch providers
        client.set_provider("openai", model="gpt-4")
    """
    return UnifiedLLMClient(
        provider=provider,
        model=model,
        api_key=api_key,
        **kwargs
    )


__all__ = [
    # Main client
    "UnifiedLLMClient",
    "create_client",
    
    # Core types
    "Message",
    "LLMResponse", 
    "LLMClientError",
    "APIKeyError",
    "RateLimitError",
    "APIError",
    
    # Strategy interface
    "LLMStrategy",
    "ProviderError",
    
    # Registry
    "PROVIDER_REGISTRY",
]