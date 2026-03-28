#!/usr/bin/env python3
"""
Coding Agent v4 - Using Unified LLM Client.

This version introduces the Strategy Pattern for LLM provider switching.
You can now seamlessly switch between Claude, GPT, and local models.

Usage:
    python agent_v4.py "Your prompt here"
    PROVIDER=openai python agent_v4.py "Using GPT!"
    python agent_v4.py --provider ollama --model codellama "Local model"
"""

import os
import sys
import argparse
import logging
from typing import Optional, List

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from coding_agent.llm import (
    UnifiedLLMClient, 
    Message, 
    LLMResponse,
    LLMClientError,
    ProviderError
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class Agent:
    """
    Coding Agent with unified LLM support.
    
    This version can switch between providers at runtime.
    """
    
    def __init__(
        self,
        provider: str = "anthropic",
        model: Optional[str] = None,
        system_prompt: Optional[str] = None
    ):
        self._client = UnifiedLLMClient(
            provider=provider,
            model=model
        )
        self._system_prompt = system_prompt or self._default_system_prompt()
        self._conversation_history: List[Message] = []
        
        logger.info(f"Agent initialized with {self._client.name}")
    
    def _default_system_prompt(self) -> str:
        return """You are a helpful coding assistant. You can:
- Read and write code files
- Execute shell commands
- Analyze codebases
- Explain programming concepts

Always provide clear, accurate responses."""
    
    @property
    def provider(self) -> str:
        return self._client.provider
    
    @property
    def model(self) -> str:
        return self._client.model
    
    def switch_provider(self, provider: str, model: Optional[str] = None):
        """Switch to a different LLM provider."""
        self._client.set_provider(provider, model=model)
        logger.info(f"Switched to {self._client.name}")
    
    def chat(
        self,
        user_input: str,
        include_history: bool = True
    ) -> LLMResponse:
        """Send a message and get a response."""
        messages = None
        if include_history:
            messages = self._conversation_history.copy()
        
        try:
            response = self._client.complete(
                prompt=user_input,
                system_prompt=self._system_prompt,
                messages=messages
            )
            
            if include_history:
                self._conversation_history.append(
                    Message(role="user", content=user_input)
                )
                self._conversation_history.append(
                    Message(role="assistant", content=response.content)
                )
            
            return response
            
        except (LLMClientError, ProviderError) as e:
            logger.error(f"Error: {e}")
            raise
    
    def reset_conversation(self):
        """Clear conversation history."""
        self._conversation_history.clear()
        logger.info("Conversation history cleared")
    
    def __str__(self) -> str:
        return f"Agent(provider={self.provider}, model={self.model})"


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Coding Agent v4 - with unified LLM support"
    )
    parser.add_argument(
        "prompt",
        nargs="?",
        help="Prompt to send to the agent"
    )
    parser.add_argument(
        "--provider", "-p",
        default=os.environ.get("PROVIDER", "anthropic"),
        choices=["anthropic", "openai", "ollama"],
        help="LLM provider to use"
    )
    parser.add_argument(
        "--model", "-m",
        help="Specific model to use"
    )
    parser.add_argument(
        "--interactive", "-i",
        action="store_true",
        help="Start interactive chat mode"
    )
    parser.add_argument(
        "--switch", "-s",
        help="Switch to a different provider"
    )
    parser.add_argument(
        "--info",
        action="store_true",
        help="Show agent information"
    )
    
    args = parser.parse_args()
    
    provider = args.provider
    if args.switch:
        provider = args.switch
    
    try:
        agent = Agent(provider=provider, model=args.model)
    except Exception as e:
        print(f"Error initializing agent: {e}")
        sys.exit(1)
    
    if args.info:
        print(f"Agent: {agent}")
        print(f"Provider: {agent.provider}")
        print(f"Model: {agent.model}")
        return
    
    if args.interactive:
        print(f"🤖 {agent} - Type 'quit' to exit, 'switch <provider>' to change models")
        print("-" * 50)
        
        while True:
            try:
                user_input = input("\nYou: ").strip()
                
                if not user_input:
                    continue
                
                if user_input.lower() in ["quit", "exit", "q"]:
                    print("Goodbye!")
                    break
                
                if user_input.lower().startswith("switch "):
                    new_provider = user_input.split()[1]
                    try:
                        agent.switch_provider(new_provider)
                        print(f"✅ Switched to {agent}")
                    except Exception as e:
                        print(f"❌ Failed to switch: {e}")
                    continue
                
                if user_input.lower() == "reset":
                    agent.reset_conversation()
                    print("✅ Conversation reset")
                    continue
                
                response = agent.chat(user_input)
                print(f"\n🤖: {response.content}")
                
            except KeyboardInterrupt:
                print("\nGoodbye!")
                break
            except Exception as e:
                print(f"Error: {e}")
    
    elif args.prompt:
        try:
            response = agent.chat(args.prompt)
            print(response.content)
            
            if response.usage:
                print(f"\n📊 Tokens: {response.usage.get('input_tokens', 0)} in, "
                      f"{response.usage.get('output_tokens', 0)} out")
                
        except Exception as e:
            print(f"Error: {e}")
            sys.exit(1)
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()