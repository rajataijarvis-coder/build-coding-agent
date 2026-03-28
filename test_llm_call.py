"""
Test script to verify our LLM client works.
"""

import os
import sys

# Add src to path
sys.path.insert(0, "/Users/rajatjarvis/.openclaw/workspace/jarvis-learning/courses/build-coding-agent/src")

from coding_agent.llm import (
    create_client, 
    AnthropicClient,
    LLMResponse,
    APIKeyError,
    LLMClientError
)


def test_with_env_key():
    """Test using API key from environment variable."""
    print("=" * 60)
    print("Test 1: Using API key from environment")
    print("=" * 60)
    
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("❌ ANTHROPIC_API_KEY not set in environment")
        print("   Set it with: export ANTHROPIC_API_KEY='sk-ant-...'")
        return False
    
    print(f"✓ API key found: {api_key[:20]}...")
    
    try:
        client = AnthropicClient(api_key=api_key)
        print(f"✓ Client created: {client}")
        
        # Make a simple call
        print("\n📡 Calling Claude...")
        response = client.complete("Say 'Hello, World!' and nothing else.")
        
        print(f"✓ Response received!")
        print(f"  Model: {response.model}")
        print(f"  Content: {response.content}")
        print(f"  Usage: {response.usage}")
        
        return True
        
    except APIKeyError as e:
        print(f"❌ API Key Error: {e}")
        return False
    except LLMClientError as e:
        print(f"❌ Client Error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


def test_with_invalid_key():
    """Test error handling with invalid key."""
    print("\n" + "=" * 60)
    print("Test 2: Error handling with invalid key")
    print("=" * 60)
    
    try:
        client = AnthropicClient(api_key="sk-ant-invalid-key")
        response = client.complete("Test")
        print("❌ Should have raised APIKeyError")
        return False
    except APIKeyError as e:
        print(f"✓ Correctly caught invalid key: {e}")
        return True
    except Exception as e:
        print(f"❌ Wrong exception type: {type(e).__name__}: {e}")
        return False


def test_factory_function():
    """Test the factory function."""
    print("\n" + "=" * 60)
    print("Test 3: Factory function")
    print("=" * 60)
    
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("⚠️  Skipping - no API key")
        return False
    
    client = create_client("anthropic", api_key=api_key)
    print(f"✓ Factory created: {client}")
    
    response = client.complete("What is 2+2? Answer in one word.")
    print(f"✓ Response: {response.content}")
    
    return True


if __name__ == "__main__":
    print("🚀 LLM Client Test Suite")
    print("=" * 60)
    
    results = []
    results.append(test_with_env_key())
    results.append(test_with_invalid_key())
    results.append(test_factory_function())
    
    print("\n" + "=" * 60)
    print("📊 Results")
    print("=" * 60)
    
    passed = sum(results)
    total = len(results)
    
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All tests passed! Your LLM client is working!")
    else:
        print("❌ Some tests failed. Check the errors above.")