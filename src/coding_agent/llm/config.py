"""
LLM Configuration and Error Handling Settings.

This module provides configuration dataclasses for:
- Retry behavior (max attempts, backoff strategies)
- Timeout settings (connect, read)
- Circuit breaker configuration
"""

import time
from dataclasses import dataclass, field
from typing import Optional, Callable


@dataclass
class RetryConfig:
    """
    Configuration for retry behavior.
    
    Controls how many times to retry failed requests and
    what backoff strategy to use between retries.
    """
    
    # Maximum number of retry attempts
    max_retries: int = 3
    
    # Initial wait time in seconds (before exponential backoff)
    initial_delay: float = 1.0
    
    # Maximum delay between retries in seconds
    max_delay: float = 60.0
    
    # Multiplier for exponential backoff (delay = initial_delay * (multiplier ^ attempt))
    backoff_multiplier: float = 2.0
    
    # Add jitter (randomness) to prevent thundering herd
    jitter: bool = True
    
    # Maximum jitter to add (as fraction of delay)
    jitter_max_fraction: float = 0.25
    
    # HTTP status codes that should trigger a retry
    retryable_status_codes: tuple = (429, 500, 502, 503, 504)
    
    # Exception types that should trigger a retry
    retryable_exceptions: tuple = (
        "requests.exceptions.Timeout",
        "requests.exceptions.ConnectionError",
    )
    
    def calculate_delay(self, attempt: int) -> float:
        """
        Calculate delay for a given retry attempt.
        
        Uses exponential backoff with optional jitter:
        delay = initial_delay * (backoff_multiplier ^ attempt)
        
        Args:
            attempt: Zero-indexed attempt number (0, 1, 2, ...)
        
        Returns:
            Delay in seconds before next retry
        
        Example:
            With initial_delay=1, multiplier=2:
            - Attempt 0: delay = 1.0 * (2^0) = 1.0s
            - Attempt 1: delay = 1.0 * (2^1) = 2.0s
            - Attempt 2: delay = 1.0 * (2^2) = 4.0s
        """
        import random
        
        # Exponential backoff
        delay = self.initial_delay * (self.backoff_multiplier ** attempt)
        
        # Cap at max_delay
        delay = min(delay, self.max_delay)
        
        # Add jitter to prevent thundering herd
        if self.jitter:
            jitter_amount = delay * self.jitter_max_fraction
            delay += random.uniform(-jitter_amount, jitter_amount)
        
        # Ensure positive delay
        return max(0.1, delay)


@dataclass
class TimeoutConfig:
    """
    Configuration for timeout behavior.
    
    Controls different timeout types for granular control
    over network operations.
    """
    
    # Timeout for establishing connection (in seconds)
    connect_timeout: float = 10.0
    
    # Timeout for waiting for response (in seconds)
    read_timeout: float = 60.0
    
    # Total timeout for the entire request (optional)
    # Set to 0 or None for no limit
    total_timeout: Optional[float] = 120.0
    
    # Whether to enable timeout for retries (first request vs cumulative)
    timeout_accumulate: bool = False
    
    def get_requests_timeout(self) -> tuple:
        """
        Get timeout tuple for requests library.
        
        Returns:
            Tuple of (connect_timeout, read_timeout)
        """
        return (self.connect_timeout, self.read_timeout)


@dataclass 
class CircuitBreakerConfig:
    """
    Configuration for circuit breaker pattern.
    
    The circuit breaker prevents cascading failures by
    stopping requests to a failing service.
    
    States:
    - CLOSED: Normal operation, requests allowed
    - OPEN: Too many failures, requests blocked
    - HALF_OPEN: Testing if service recovered
    """
    
    # Number of failures before opening circuit
    failure_threshold: int = 5
    
    # Number of successes needed to close circuit (from half-open)
    success_threshold: int = 2
    
    # Time in seconds before trying again (from OPEN to HALF_OPEN)
    timeout: float = 30.0
    
    # Whether circuit breaker is enabled
    enabled: bool = True


@dataclass
class LLMConfig:
    """
    Complete configuration for LLM client.
    
    Combines all configuration options into one place.
    """
    
    # Retry configuration
    retry: RetryConfig = field(default_factory=RetryConfig)
    
    # Timeout configuration
    timeout: TimeoutConfig = field(default_factory=TimeoutConfig)
    
    # Circuit breaker configuration
    circuit_breaker: CircuitBreakerConfig = field(default_factory=CircuitBreakerConfig)
    
    # Whether to log retry attempts
    log_retries: bool = True
    
    # Custom retry callback (called before each retry)
    # Can be used for custom logic like notifying users
    on_retry: Optional[Callable[[Exception, int], None]] = None


# Default configuration
DEFAULT_LLM_CONFIG = LLMConfig()