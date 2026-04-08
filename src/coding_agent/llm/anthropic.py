"""
Anthropic Claude API Client with Robust Error Handling.

This client extends the base AnthropicClient with:
- Exponential backoff for rate limits
- Configurable timeouts
- Circuit breaker pattern
- Retry logic for transient failures
"""

import os
import time
import logging
import requests
from typing import Optional, Dict, Any, List
from dataclasses import dataclass

from .client import (
    LLMClientError, 
    APIKeyError, 
    RateLimitError, 
    APIError,
    Message, 
    LLMResponse
)
from .config import LLMConfig, DEFAULT_LLM_CONFIG, RetryConfig, TimeoutConfig
from .circuit_breaker import CircuitBreaker, CircuitBreakerOpen

logger = logging.getLogger(__name__)


class AnthropicClient:
    """
    Client for Anthropic Claude API with error handling.
    
    This client provides a robust interface for making completion
    requests to Claude with:
    - Automatic retry with exponential backoff
    - Circuit breaker for cascading failure prevention
    - Configurable timeouts
    - Detailed logging
    
    Example:
        config = LLMConfig(
            retry=RetryConfig(max_retries=3, initial_delay=1.0),
            timeout=TimeoutConfig(connect_timeout=10, read_timeout=60)
        )
        client = AnthropicClient(api_key="sk-ant-...", config=config)
        response = client.complete("Hello, Claude!")
    """
    
    def __init__(
        self, 
        api_key: Optional[str] = None,
        model: str = "claude-3-haiku-20240307",
        max_tokens: int = 1024,
        temperature: float = 1.0,
        timeout: int = 60,
        config: Optional[LLMConfig] = None
    ):
        """
        Initialize the Anthropic client with error handling.
        
        Args:
            api_key: Anthropic API key. Falls back to ANTHROPIC_API_KEY env var.
            model: Model identifier (default: claude-3-haiku)
            max_tokens: Maximum tokens in response
            temperature: Sampling temperature (0.0 to 1.0)
            timeout: Legacy timeout parameter (used if no config provided)
            config: LLMConfig for retry, timeout, and circuit breaker settings
        """
        self._api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        self._model = model
        self._max_tokens = max_tokens
        self._temperature = temperature
        
        # Use provided config or default
        self._config = config or DEFAULT_LLM_CONFIG
        
        # Handle legacy timeout parameter
        if timeout != 60:
            self._config.timeout = TimeoutConfig(
                connect_timeout=min(timeout, 10),
                read_timeout=timeout
            )
        
        # Initialize circuit breaker
        self._circuit_breaker = CircuitBreaker(
            name=f"anthropic-{model}",
            failure_threshold=self._config.circuit_breaker.failure_threshold,
            success_threshold=self._config.circuit_breaker.success_threshold,
            timeout=self._config.circuit_breaker.timeout
        )
        
        # Validate API key
        if not self._api_key:
            raise APIKeyError(
                "Anthropic API key not found. Set ANTHROPIC_API_KEY "
                "environment variable or pass api_key to constructor."
            )
        
        if not self._api_key.startswith("sk-ant-"):
            raise APIKeyError(
                "Invalid Anthropic API key format. Expected key starting with 'sk-ant-'"
            )
        
        self._headers = {
            "x-api-key": self._api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }
    
    @property
    def model(self) -> str:
        """Get the current model."""
        return self._model
    
    @property
    def name(self) -> str:
        """Get display name for this client."""
        return f"Anthropic ({self._model})"
    
    def complete(
        self, 
        prompt: str,
        system_prompt: Optional[str] = None,
        messages: Optional[List[Dict[str, str]]] = None,
        **kwargs
    ) -> LLMResponse:
        """
        Generate a completion with automatic retry and error handling.
        
        This is the main method for interacting with Claude. It handles
        all the complexity of retry logic, timeouts, and circuit breaking.
        
        Args:
            prompt: The user's message/prompt
            system_prompt: Optional system prompt to set context
            messages: Optional list of previous messages for context
            **kwargs: Additional parameters (max_tokens, temperature, etc.)
        
        Returns:
            LLMResponse object with the model's response
            
        Raises:
            APIKeyError: If API key is invalid (not retried)
            RateLimitError: If rate limit persists after retries
            APIError: If API returns an unrecoverable error
            LLMClientError: If all retries exhausted
        
        Example:
            >>> client = AnthropicClient()
            >>> response = client.complete("What is Python?")
            >>> print(response.content)
            Python is a high-level programming language...
        """
        # Build messages array
        request_messages = self._build_messages(prompt, system_prompt, messages)
        
        # Build request payload
        payload = {
            "model": kwargs.get("model", self._model),
            "messages": request_messages,
            "max_tokens": kwargs.get("max_tokens", self._max_tokens),
            "temperature": kwargs.get("temperature", self._temperature),
        }
        
        # Execute with circuit breaker and retry
        return self._execute_with_retry(payload)
    
    def _build_messages(
        self, 
        prompt: str, 
        system_prompt: Optional[str],
        messages: Optional[List[Dict[str, str]]]
    ) -> List[Dict[str, str]]:
        """Build the messages array for the API request."""
        request_messages = []
        
        if system_prompt:
            request_messages.append({
                "role": "user",
                "content": system_prompt + "\n\n" + prompt
            })
        else:
            request_messages.append({
                "role": "user", 
                "content": prompt
            })
        
        if messages:
            request_messages = messages
            if not messages or messages[-1].get("role") != "user":
                request_messages.append({"role": "user", "content": prompt})
        
        return request_messages
    
    def _execute_with_retry(self, payload: Dict[str, Any]) -> LLMResponse:
        """
        Execute API request with retry logic and circuit breaker.
        
        This method implements:
        1. Circuit breaker check
        2. Retry loop with exponential backoff
        3. Proper error handling and classification
        4. Logging of retry attempts
        """
        max_retries = self._config.retry.max_retries
        last_exception = None
        
        for attempt in range(max_retries + 1):
            try:
                # Check circuit breaker first
                if self._config.circuit_breaker.enabled:
                    return self._circuit_breaker.call(self._make_request, payload)
                else:
                    return self._make_request(payload)
                    
            except CircuitBreakerOpen as e:
                # Don't retry if circuit is open
                logger.error(f"Circuit breaker open: {e}")
                raise LLMClientError(str(e)) from e
                
            except RateLimitError as e:
                last_exception = e
                if attempt < max_retries:
                    delay = self._config.retry.calculate_delay(attempt)
                    self._log_retry("Rate limited", attempt, max_retries, delay)
                    time.sleep(delay)
                    continue
                # No more retries
                logger.error(f"Rate limit persisted after {max_retries} retries")
                raise
                
            except (requests.exceptions.Timeout, 
                    requests.exceptions.ConnectionError,
                    APIError) as e:
                last_exception = e
                
                # Check if this error is retryable
                if not self._is_retryable_error(e):
                    logger.error(f"Non-retryable error: {type(e).__name__}: {e}")
                    raise
                
                if attempt < max_retries:
                    delay = self._config.retry.calculate_delay(attempt)
                    self._log_retry(
                        f"{type(e).__name__}: {str(e)[:100]}", 
                        attempt, 
                        max_retries, 
                        delay
                    )
                    time.sleep(delay)
                    continue
                
                # All retries exhausted
                logger.error(f"All {max_retries} retries exhausted")
                raise LLMClientError(
                    f"Failed after {max_retries} retries: {e}"
                ) from e
        
        # Should not reach here, but just in case
        raise LLMClientError(
            f"Unexpected error after {max_retries} retries"
        ) from last_exception
    
    def _is_retryable_error(self, error: Exception) -> bool:
        """Determine if an error should trigger a retry."""
        # Network errors are always retryable
        if isinstance(error, (requests.exceptions.Timeout, 
                              requests.exceptions.ConnectionError)):
            return True
        
        # API errors with retryable status codes
        if isinstance(error, APIError) and error.status_code:
            return error.status_code in self._config.retry.retryable_status_codes
        
        return False
    
    def _log_retry(self, error_msg: str, attempt: int, max_retries: int, delay: float):
        """Log retry attempt details."""
        if self._config.log_retries:
            logger.warning(
                f"Retry {attempt + 1}/{max_retries} after {delay:.2f}s - {error_msg}"
            )
        
        # Call custom retry callback if provided
        if self._config.on_retry:
            try:
                self._config.on_retry(error_msg, attempt)
            except Exception as e:
                logger.debug(f"Retry callback error: {e}")
    
    def _make_request(self, payload: Dict[str, Any]) -> LLMResponse:
        """Make the actual API request."""
        url = "https://api.anthropic.com/v1/messages"
        
        try:
            logger.debug(f"Calling Anthropic API with model: {self._model}")
            
            response = requests.post(
                url,
                headers=self._headers,
                json=payload,
                timeout=self._config.timeout.get_requests_timeout()
            )
            
            # Handle different status codes
            if response.status_code == 200:
                return self._parse_response(response.json())
            
            elif response.status_code == 401:
                raise APIKeyError("Authentication failed. Check your API key.")
            
            elif response.status_code == 429:
                retry_after = response.headers.get("retry-after", "60")
                raise RateLimitError(
                    f"Rate limit exceeded. Retry after {retry_after} seconds."
                )
            
            elif response.status_code >= 500:
                raise APIError(
                    f"Anthropic API error: {response.text}",
                    status_code=response.status_code
                )
            
            else:
                raise APIError(
                    f"API request failed: {response.text}",
                    status_code=response.status_code
                )
                
        except requests.exceptions.Timeout as e:
            raise LLMClientError(
                f"Request timed out after {self._config.timeout.read_timeout} seconds"
            ) from e
        except requests.exceptions.ConnectionError as e:
            raise LLMClientError(
                "Failed to connect to Anthropic API. Check your internet connection."
            ) from e
    
    def _parse_response(self, response_data: Dict[str, Any]) -> LLMResponse:
        """Parse the API response into our LLMResponse format."""
        content_blocks = response_data.get("content", [])
        
        if not content_blocks:
            raise APIError("Empty response from Anthropic API")
        
        text_content = ""
        for block in content_blocks:
            if block.get("type") == "text":
                text_content += block.get("text", "")
        
        if not text_content:
            raise APIError("No text content in API response")
        
        usage = response_data.get("usage", {})
        
        return LLMResponse(
            content=text_content,
            model=response_data.get("model", self._model),
            usage={
                "input_tokens": usage.get("input_tokens", 0),
                "output_tokens": usage.get("output_tokens", 0)
            },
            raw_response=response_data
        )
    
    def __str__(self) -> str:
        return f"AnthropicClient(model={self._model}, config={self._config})"