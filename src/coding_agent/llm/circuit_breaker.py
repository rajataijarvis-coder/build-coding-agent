"""
Circuit Breaker Implementation.

Implements the circuit breaker pattern to prevent cascading failures
when an LLM API is experiencing issues.
"""

import time
import logging
from enum import Enum
from threading import Lock
from typing import Optional

logger = logging.getLogger(__name__)


class CircuitState(Enum):
    """Circuit breaker states."""
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Blocking requests
    HALF_OPEN = "half_open"  # Testing recovery


class CircuitBreakerOpen(Exception):
    """Raised when circuit breaker is open and rejecting requests."""
    
    def __init__(self, service_name: str, retry_after: float):
        self.service_name = service_name
        self.retry_after = retry_after
        super().__init__(
            f"Circuit breaker is OPEN for {service_name}. "
            f"Retry after {retry_after:.1f} seconds."
        )


class CircuitBreaker:
    """
    Circuit breaker for LLM API calls.
    
    Prevents cascading failures by stopping requests to a failing service.
    After a threshold of failures, the circuit "opens" and rejects requests
    for a timeout period, then enters "half-open" to test recovery.
    
    Example:
        breaker = CircuitBreaker("anthropic", failure_threshold=5, timeout=30)
        
        try:
            breaker.call(api_function)
        except CircuitBreakerOpen:
            print("Service temporarily unavailable")
    """
    
    def __init__(
        self,
        name: str,
        failure_threshold: int = 5,
        success_threshold: int = 2,
        timeout: float = 30.0
    ):
        """
        Initialize circuit breaker.
        
        Args:
            name: Name of the service (for logging)
            failure_threshold: Number of failures before opening circuit
            success_threshold: Successes needed to close circuit (from half-open)
            timeout: Seconds to wait before trying again
        """
        self.name = name
        self.failure_threshold = failure_threshold
        self.success_threshold = success_threshold
        self.timeout = timeout
        
        # State tracking
        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._success_count = 0
        self._last_failure_time: Optional[float] = None
        self._lock = Lock()
    
    @property
    def state(self) -> CircuitState:
        """Get current circuit state."""
        with self._lock:
            # Check if we should transition from OPEN to HALF_OPEN
            if self._state == CircuitState.OPEN:
                if self._last_failure_time:
                    elapsed = time.time() - self._last_failure_time
                    if elapsed >= self.timeout:
                        self._state = CircuitState.HALF_OPEN
                        self._success_count = 0
                        logger.info(f"Circuit breaker {self.name}: OPEN → HALF_OPEN")
            
            return self._state
    
    def call(self, func, *args, **kwargs):
        """
        Execute a function through the circuit breaker.
        
        Args:
            func: Function to execute
            *args, **kwargs: Arguments to pass to function
        
        Returns:
            Result of function execution
        
        Raises:
            CircuitBreakerOpen: If circuit is open
        """
        current_state = self.state
        
        if current_state == CircuitState.OPEN:
            retry_after = self.timeout
            if self._last_failure_time:
                retry_after = self.timeout - (time.time() - self._last_failure_time)
            raise CircuitBreakerOpen(self.name, max(0, retry_after))
        
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise
    
    def _on_success(self):
        """Handle successful call."""
        with self._lock:
            if self._state == CircuitState.HALF_OPEN:
                self._success_count += 1
                if self._success_count >= self.success_threshold:
                    self._state = CircuitState.CLOSED
                    self._failure_count = 0
                    logger.info(f"Circuit breaker {self.name}: HALF_OPEN → CLOSED")
            elif self._state == CircuitState.CLOSED:
                # Reset failure count on success
                self._failure_count = 0
    
    def _on_failure(self):
        """Handle failed call."""
        with self._lock:
            self._failure_count += 1
            self._last_failure_time = time.time()
            
            if self._state == CircuitState.HALF_OPEN:
                # Any failure in half-open goes back to open
                self._state = CircuitState.OPEN
                logger.warning(f"Circuit breaker {self.name}: HALF_OPEN → OPEN (failure)")
            elif self._state == CircuitState.CLOSED:
                if self._failure_count >= self.failure_threshold:
                    self._state = CircuitState.OPEN
                    logger.warning(
                        f"Circuit breaker {self.name}: CLOSED → OPEN "
                        f"({self._failure_count} failures)"
                    )
    
    def reset(self):
        """Manually reset the circuit breaker."""
        with self._lock:
            self._state = CircuitState.CLOSED
            self._failure_count = 0
            self._success_count = 0
            self._last_failure_time = None
            logger.info(f"Circuit breaker {self.name}: manually reset")
    
    def __str__(self) -> str:
        return f"CircuitBreaker({self.name}, state={self.state.value}, failures={self._failure_count})"