"""
Tests for error handling and retry logic.
"""

import pytest
import time
from unittest.mock import Mock, patch, MagicMock
import requests

from coding_agent.llm.config import (
    RetryConfig, 
    TimeoutConfig, 
    LLMConfig,
    CircuitBreakerConfig
)
from coding_agent.llm.circuit_breaker import (
    CircuitBreaker, 
    CircuitBreakerOpen,
    CircuitState
)


class TestRetryConfig:
    """Tests for retry configuration."""
    
    def test_exponential_backoff(self):
        """Test that exponential backoff calculates correctly."""
        config = RetryConfig(
            initial_delay=1.0,
            backoff_multiplier=2.0,
            jitter=False
        )
        
        assert config.calculate_delay(0) == 1.0
        assert config.calculate_delay(1) == 2.0
        assert config.calculate_delay(2) == 4.0
    
    def test_max_delay_cap(self):
        """Test that delay is capped at max_delay."""
        config = RetryConfig(
            initial_delay=1.0,
            backoff_multiplier=10.0,
            max_delay=5.0,
            jitter=False
        )
        
        # Should be capped at 5.0
        assert config.calculate_delay(10) == 5.0
    
    def test_jitter_exists(self):
        """Test that jitter is added when enabled."""
        config = RetryConfig(
            initial_delay=1.0,
            backoff_multiplier=2.0,
            jitter=True,
            jitter_max_fraction=0.25
        )
        
        delays = [config.calculate_delay(1) for _ in range(10)]
        # With jitter, delays should vary
        assert len(set(delays)) > 1


class TestCircuitBreaker:
    """Tests for circuit breaker pattern."""
    
    def test_initial_state_closed(self):
        """Test that circuit starts closed."""
        breaker = CircuitBreaker("test", failure_threshold=3)
        assert breaker.state == CircuitState.CLOSED
    
    def test_opens_after_threshold(self):
        """Test circuit opens after failure threshold."""
        breaker = CircuitBreaker("test", failure_threshold=3, timeout=0)
        
        def fail():
            raise Exception("Test failure")
        
        # Trigger failures
        for _ in range(3):
            with pytest.raises(Exception):
                breaker.call(fail)
        
        assert breaker.state == CircuitState.OPEN
    
    def test_rejects_requests_when_open(self):
        """Test that open circuit rejects requests."""
        breaker = CircuitBreaker("test", failure_threshold=1, timeout=0)
        
        def fail():
            raise Exception("Test failure")
        
        # Trigger failure to open circuit
        with pytest.raises(Exception):
            breaker.call(fail)
        
        # Now should reject
        with pytest.raises(CircuitBreakerOpen):
            breaker.call(fail)
    
    def test_half_open_after_timeout(self):
        """Test circuit goes half-open after timeout."""
        breaker = CircuitBreaker("test", failure_threshold=1, timeout=0.1)
        
        def fail():
            raise Exception("Test failure")
        
        # Open the circuit
        with pytest.raises(Exception):
            breaker.call(fail)
        
        assert breaker.state == CircuitState.CLOSED  # Still shows closed until checked
        
        # Wait for timeout
        time.sleep(0.15)
        
        # Should now be half-open
        assert breaker.state == CircuitState.HALF_OPEN
    
    def test_success_closes_circuit_from_half_open(self):
        """Test that successes close circuit from half-open."""
        breaker = CircuitBreaker(
            "test", 
            failure_threshold=1, 
            success_threshold=2,
            timeout=0.1
        )
        
        # Open circuit
        def fail():
            raise Exception("Test failure")
        
        with pytest.raises(Exception):
            breaker.call(fail)
        
        # Wait for half-open
        time.sleep(0.15)
        
        # Now succeed twice
        def succeed():
            return "success"
        
        breaker.call(succeed)
        breaker.call(succeed)
        
        assert breaker.state == CircuitState.CLOSED


class TestAnthropicClientRetry:
    """Tests for AnthropicClient retry behavior."""
    
    @patch('coding_agent.llm.anthropic.requests.post')
    def test_retry_on_rate_limit(self, mock_post):
        """Test that client retries on 429 response."""
        from coding_agent.llm.anthropic import AnthropicClient
        
        # First two calls return 429, third succeeds
        mock_response_429 = Mock()
        mock_response_429.status_code = 429
        mock_response_429.headers = {"retry-after": "1"}
        
        mock_response_200 = Mock()
        mock_response_200.status_code = 200
        mock_response_200.json.return_value = {
            "content": [{"type": "text", "text": "Hello!"}],
            "model": "claude-3-haiku",
            "usage": {"input_tokens": 10, "output_tokens": 5}
        }
        
        mock_post.side_effect = [
            mock_response_429,
            mock_response_429, 
            mock_response_200
        ]
        
        # Use short delays for test
        config = LLMConfig(
            retry=RetryConfig(max_retries=2, initial_delay=0.1)
        )
        
        client = AnthropicClient(
            api_key="sk-ant-test123",
            config=config
        )
        
        response = client.complete("Hi")
        
        assert response.content == "Hello!"
        assert mock_post.call_count == 3
    
    @patch('coding_agent.llm.anthropic.requests.post')
    def test_no_retry_on_auth_error(self, mock_post):
        """Test that client doesn't retry on auth errors."""
        from coding_agent.llm.anthropic import AnthropicClient
        
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.text = "Unauthorized"
        
        mock_post.return_value = mock_response
        
        config = LLMConfig(
            retry=RetryConfig(max_retries=3, initial_delay=0.1)
        )
        
        client = AnthropicClient(
            api_key="sk-ant-test123", 
            config=config
        )
        
        from coding_agent.llm.client import APIKeyError
        with pytest.raises(APIKeyError):
            client.complete("Hi")
        
        # Should only call once - no retries for auth errors
        assert mock_post.call_count == 1


# Run tests with: pytest tests/unit/test_error_handling.py -v