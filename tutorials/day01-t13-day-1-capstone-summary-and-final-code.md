# Day 1 Capstone: Summary & Complete Working Code

**Course:** Build Your Own Coding Agent  
**Day:** 1 Complete  
**Tutorial:** 13 of 60  
**Estimated Time:** 90 minutes (to review + run the final code)

---

## 🎉 Congratulations on Completing Day 1!

You've made it through the foundation. Let's review what you've built before moving to Day 2.

---

## 📚 Day 1 Concepts Summary

| Tutorial | Concept | What You Built |
|----------|---------|----------------|
| **T1** | What is a Coding Agent? | Mental model: autonomous AI that acts, not just suggests |
| **T2** | System Architecture | MVC-like pattern: Controller → LLM → Tools → State |
| **T3** | Component Breakdown | Clear roles: Agent, LLMClient, ToolRegistry, ConversationManager |
| **T4** | Data Flow | Request lifecycle: input → plan → execute → respond → learn |
| **T5** | OOP Refresher | Classes, encapsulation, properties, methods |
| **T6** | SOLID Principles | Single responsibility, open/closed, dependency inversion |
| **T7** | Design Patterns | Strategy (swappable LLMs), Command (tool execution), Observer (events) |
| **T8** | Project Structure | Multi-module Python package layout |
| **T9-11** | Configuration & Setup | Environment variables, `.env`, git, pyproject.toml |
| **T12** | Dependency Injection | Container pattern, factories, singleton lifecycle |

---

## 🏗️ Complete Project Structure

After Day 1, your project should look like this:

```
coding-agent/
├── pyproject.toml
├── README.md
├── .env
├── .env.example
├── .gitignore
├── src/
│   └── coding_agent/
│       ├── __init__.py
│       ├── agent.py                 # Main Agent class
│       ├── config.py                # Configuration (T9-T11)
│       ├── exceptions.py            # Custom exceptions
│       ├── interfaces/
│       │   ├── __init__.py
│       │   ├── llm.py               # LLMClient interface
│       │   ├── tools.py             # Tool interface
│       │   └── events.py            # Event/Observer interfaces
│       ├── llm/
│       │   ├── __init__.py
│       │   ├── client.py            # LLM client implementations
│       │   └── factory.py           # create_llm_client()
│       ├── tools/
│       │   ├── __init__.py
│       │   ├── base.py              # Base tool class
│       │   ├── registry.py          # ToolRegistry
│       │   └── builtins.py          # Built-in tools
│       ├── context/
│       │   ├── __init__.py
│       │   └── manager.py           # ConversationManager
│       ├── di/
│       │   ├── __init__.py
│       │   └── container.py         # DI Container (T12)
│       └── events/
│           ├── __init__.py
│           └── emitter.py           # EventEmitter + Observers (T7)
├── tests/
│   ├── __init__.py
│   └── test_agent.py
└── scripts/
    └── run_agent.py                 # Entry point
```

---

## 💾 Complete Working Code

Below is the consolidated code you should have after completing Day 1. Each file includes inline comments explaining which tutorial it came from.

---

### `pyproject.toml`

```toml
[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "coding-agent"
version = "0.1.0"
description = "Build Your Own Coding Agent - Day 1 Complete"
authors = [{name = "Your Name", email = "you@example.com"}]
readme = "README.md"
requires-python = ">=3.10"
dependencies = [
    "anthropic>=0.25.0",
    "openai>=1.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0",
    "pytest-cov>=4.0",
    "black>=23.0",
    "ruff>=0.1.0",
]

[project.scripts]
coding-agent = "coding_agent.__main__:main"

[tool.setuptools.packages.find]
where = ["src"]

[tool.black]
line-length = 100
target-version = ['py310']

[tool.ruff]
line-length = 100
select = ["E", "F", "W", "I", "N"]
```

---

### `.env.example`

```bash
# LLM Provider Settings
DEFAULT_LLM_PROVIDER=claude
CLAUDE_MODEL=claude-3-5-sonnet-20241022
OPENAI_MODEL=gpt-4o
OLLAMA_MODEL=llama3.2

# API Keys (DO NOT commit .env with real keys!)
ANTHROPIC_API_KEY=your_key_here
OPENAI_API_KEY=your_key_here

# Generation Parameters
TEMPERATURE=0.7
MAX_TOKENS=4096

# Tool Safety
ALLOWED_DIRECTORIES=.
READ_ONLY=false
SHELL_TIMEOUT=30

# Logging
LOG_LEVEL=INFO
VERBOSE_EVENTS=false
DEBUG=false
```

---

### `src/coding_agent/__init__.py`

```python
"""
Coding Agent - Day 1 Complete

A coding agent built with clean architecture:
- SOLID principles (T6)
- Design patterns: Strategy, Command, Observer (T7)
- Dependency injection (T12)
- Multi-module structure (T8)
"""

__version__ = "0.1.0"

from coding_agent.agent import Agent
from coding_agent.config import AgentConfig, get_config

__all__ = ["Agent", "AgentConfig", "get_config", "__version__"]
```

---

### `src/coding_agent/exceptions.py`

```python
"""Custom exceptions for the coding agent."""


class CodingAgentError(Exception):
    """Base exception for all coding agent errors."""
    
    def __init__(self, message: str, details: dict = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}


class ConfigurationError(CodingAgentError):
    """Raised when there's a configuration issue."""
    pass


class LLMError(CodingAgentError):
    """Raised when the LLM client encounters an error."""
    pass


class ToolError(CodingAgentError):
    """Raised when a tool execution fails."""
    pass


class ToolNotFoundError(ToolError):
    """Raised when a requested tool doesn't exist."""
    pass


class ValidationError(CodingAgentError):
    """Raised when input validation fails."""
    pass
```

---

### `src/coding_agent/config.py`

```python
"""
Configuration management (T9-T11)

Loads settings from environment variables.
Use .env file for local development.
"""

import os
from dataclasses import dataclass, field
from typing import Optional, List


@dataclass
class LLMConfig:
    """LLM provider configuration."""
    
    default_provider: str = "claude"
    claude_model: str = "claude-3-5-sonnet-20241022"
    openai_model: str = "gpt-4o"
    ollama_model: str = "llama3.2"
    temperature: float = 0.7
    max_tokens: int = 4096
    
    @property
    def anthropic_api_key(self) -> Optional[str]:
        return os.environ.get("ANTHROPIC_API_KEY")
    
    @property
    def openai_api_key(self) -> Optional[str]:
        return os.environ.get("OPENAI_API_KEY")
    
    @property
    def has_anthropic_key(self) -> bool:
        return bool(self.anthropic_api_key)
    
    @property
    def has_openai_key(self) -> bool:
        return bool(self.openai_api_key)


@dataclass
class ToolConfig:
    """Tool configuration."""
    
    allowed_directories: List[str] = field(default_factory=lambda: ["."])
    read_only: bool = False
    shell_timeout: int = 30


@dataclass
class LoggingConfig:
    """Logging configuration."""
    
    level: str = "INFO"
    verbose_events: bool = False


@dataclass
class AgentConfig:
    """Main agent configuration."""
    
    llm: LLMConfig = field(default_factory=LLMConfig)
    tools: ToolConfig = field(default_factory=ToolConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    debug: bool = False
    
    @classmethod
    def from_environment(cls) -> "AgentConfig":
        """Load configuration from environment variables."""
        return cls(
            llm=LLMConfig(
                default_provider=os.environ.get("DEFAULT_LLM_PROVIDER", "claude"),
                temperature=float(os.environ.get("TEMPERATURE", "0.7")),
                max_tokens=int(os.environ.get("MAX_TOKENS", "4096")),
            ),
            tools=ToolConfig(
                allowed_directories=os.environ.get("ALLOWED_DIRECTORIES", ".").split(","),
                read_only=os.environ.get("READ_ONLY", "false").lower() == "true",
            ),
            logging=LoggingConfig(
                level=os.environ.get("LOG_LEVEL", "INFO").upper(),
            ),
            debug=os.environ.get("DEBUG", "false").lower() == "true",
        )
    
    def validate(self) -> List[str]:
        """Validate configuration."""
        issues = []
        if self.llm.default_provider == "claude" and not self.llm.has_anthropic_key:
            issues.append("ANTHROPIC_API_KEY not set for Claude provider")
        if self.llm.default_provider == "openai" and not self.llm.has_openai_key:
            issues.append("OPENAI_API_KEY not set for OpenAI provider")
        return issues


# Global config singleton
_config: Optional[AgentConfig] = None


def get_config() -> AgentConfig:
    """Get or create the global config instance."""
    global _config
    if _config is None:
        _config = AgentConfig.from_environment()
    return _config
```

---

### `src/coding_agent/interfaces/__init__.py`

```python
"""Abstract interfaces (SOLID: Dependency Inversion Principle)."""

from coding_agent.interfaces.llm import LLMClient, LLMResponse
from coding_agent.interfaces.tools import Tool, ToolResult
from coding_agent.interfaces.events import EventEmitter, AgentObserver

__all__ = [
    "LLMClient", "LLMResponse",
    "Tool", "ToolResult",
    "EventEmitter", "AgentObserver",
]
```

---

### `src/coding_agent/interfaces/llm.py`

```python
"""
LLM Client Interface (T7: Strategy Pattern)

Allows swapping between Claude, OpenAI, and Ollama without changing Agent code.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional


@dataclass
class LLMResponse:
    """Standardized response from any LLM provider."""
    
    content: str
    tokens_used: int = 0
    model: str = ""
    provider: str = ""


class LLMClient(ABC):
    """Abstract base for all LLM providers (Strategy Pattern)."""
    
    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Provider name for display."""
        pass
    
    @abstractmethod
    def complete(self, prompt: str, **kwargs) -> LLMResponse:
        """Generate completion from prompt."""
        pass
```

---

### `src/coding_agent/interfaces/tools.py`

```python
"""
Tool Interface (T7: Command Pattern)

Each tool encapsulates an operation that can be executed, logged, and undone.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class ToolResult:
    """Result of executing a tool."""
    
    success: bool
    output: str
    error: Optional[str] = None
    metadata: Dict[str, Any] = None


class Tool(ABC):
    """Abstract base for all tools (Command Pattern)."""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Tool name for invocation."""
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """Description for LLM to understand when to use this tool."""
        pass
    
    @abstractmethod
    def execute(self, **kwargs) -> ToolResult:
        """Execute the tool with given arguments."""
        pass
    
    def validate(self, **kwargs) -> Optional[str]:
        """Validate arguments before execution. Return error message or None."""
        return None
```

---

### `src/coding_agent/interfaces/events.py`

```python
"""
Event System Interfaces (T7: Observer Pattern)

Allows decoupled event handling: logging, metrics, UI updates.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict


class AgentObserver(ABC):
    """Abstract observer for agent events."""
    
    @abstractmethod
    def on_event(self, event_type: str, data: Dict[str, Any]) -> None:
        """Called when an event occurs."""
        pass


class EventEmitter(ABC):
    """Abstract event emitter."""
    
    @abstractmethod
    def subscribe(self, observer: AgentObserver) -> None:
        """Subscribe an observer to events."""
        pass
    
    @abstractmethod
    def emit(self, event_type: str, data: Dict[str, Any]) -> None:
        """Emit an event to all observers."""
        pass
```

---

### `src/coding_agent/llm/__init__.py`

```python
"""LLM module - Language model clients."""

from coding_agent.llm.client import (
    MockLLMClient,
    AnthropicClient,
    OpenAIClient,
)
from coding_agent.llm.factory import create_llm_client

__all__ = [
    "MockLLMClient",
    "AnthropicClient", 
    "OpenAIClient",
    "create_llm_client",
]
```

---

### `src/coding_agent/llm/client.py`

```python
"""
LLM Client Implementations (T7: Strategy Pattern)

Each provider implements the LLMClient interface.
"""

import os
from typing import Optional

from coding_agent.interfaces.llm import LLMClient, LLMResponse


class MockLLMClient(LLMClient):
    """Mock LLM for testing (no API key needed)."""
    
    def __init__(self, model: str = "mock-model"):
        self._model = model
        self._call_count = 0
    
    @property
    def provider_name(self) -> str:
        return f"Mock ({self._model})"
    
    def complete(self, prompt: str, **kwargs) -> LLMResponse:
        self._call_count += 1
        return LLMResponse(
            content=f"[Mock Response #{self._call_count}] Received: {prompt[:50]}...",
            tokens_used=len(prompt) // 4,
            model=self._model,
            provider="mock",
        )


class AnthropicClient(LLMClient):
    """Anthropic Claude implementation."""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "claude-3-5-sonnet-20241022"):
        self._api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        self._model = model
    
    @property
    def provider_name(self) -> str:
        return f"Claude ({self._model})"
    
    def complete(self, prompt: str, **kwargs) -> LLMResponse:
        # In Day 2, we'll add actual API calls
        return LLMResponse(
            content=f"[Claude Response] Processing: {prompt[:50]}...",
            tokens_used=len(prompt) // 4,
            model=self._model,
            provider="claude",
        )


class OpenAIClient(LLMClient):
    """OpenAI GPT implementation."""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4o"):
        self._api_key = api_key or os.environ.get("OPENAI_API_KEY")
        self._model = model
    
    @property
    def provider_name(self) -> str:
        return f"GPT ({self._model})"
    
    def complete(self, prompt: str, **kwargs) -> LLMResponse:
        # In Day 2, we'll add actual API calls
        return LLMResponse(
            content=f"[GPT Response] Processing: {prompt[:50]}...",
            tokens_used=len(prompt) // 4,
            model=self._model,
            provider="openai",
        )
```

---

### `src/coding_agent/llm/factory.py`

```python
"""
LLM Factory (T12: Factory Pattern + DI)

Creates the appropriate LLM client based on configuration.
"""

from coding_agent.config import AgentConfig, get_config
from coding_agent.interfaces.llm import LLMClient
from coding_agent.llm.client import MockLLMClient, AnthropicClient, OpenAIClient


def create_llm_client(config: AgentConfig = None) -> LLMClient:
    """
    Factory function to create LLM client (T12).
    
    Reads configuration to determine which provider to instantiate.
    
    Args:
        config: Configuration (uses global if not provided)
        
    Returns:
        Configured LLMClient instance
    """
    config = config or get_config()
    provider = config.llm.default_provider
    
    if provider == "claude":
        return AnthropicClient(
            api_key=config.llm.anthropic_api_key,
            model=config.llm.claude_model,
        )
    
    elif provider == "openai":
        return OpenAIClient(
            api_key=config.llm.openai_api_key,
            model=config.llm.openai_model,
        )
    
    elif provider == "mock":
        return MockLLMClient(model="mock-v1")
    
    else:
        raise ValueError(f"Unknown LLM provider: {provider}")
```

---

### `src/coding_agent/tools/__init__.py`

```python
"""Tools module - Agent capabilities."""

from coding_agent.tools.base import BaseTool
from coding_agent.tools.registry import ToolRegistry
from coding_agent.tools.builtins import HelpTool, TimeTool, CalculatorTool

__all__ = [
    "BaseTool",
    "ToolRegistry",
    "HelpTool",
    "TimeTool",
    "CalculatorTool",
]
```

---

### `src/coding_agent/tools/base.py`

```python
"""Base tool class with common functionality."""

from coding_agent.interfaces.tools import Tool, ToolResult


class BaseTool(Tool):
    """Base class for all tools with common validation."""
    
    def validate(self, **kwargs) -> str:
        """Base validation - can be overridden by subclasses."""
        return None  # No validation errors
```

---

### `src/coding_agent/tools/registry.py`

```python
"""
Tool Registry (T7: Command Pattern + T12: DI)

Manages all available tools and executes them.
"""

from typing import Dict, List, Optional

from coding_agent.interfaces.tools import Tool, ToolResult
from coding_agent.exceptions import ToolNotFoundError


class ToolRegistry:
    """Registry for managing and executing tools."""
    
    def __init__(self):
        self._tools: Dict[str, Tool] = {}
    
    def register(self, tool: Tool) -> None:
        """Register a tool by its name."""
        self._tools[tool.name] = tool
    
    def get(self, name: str) -> Tool:
        """Get a tool by name."""
        if name not in self._tools:
            raise ToolNotFoundError(f"Tool '{name}' not found")
        return self._tools[name]
    
    def list_tools(self) -> List[Tool]:
        """List all registered tools."""
        return list(self._tools.values())
    
    def execute(self, name: str, **kwargs) -> ToolResult:
        """Execute a tool by name with given arguments."""
        tool = self.get(name)
        
        # Validate before executing
        error = tool.validate(**kwargs)
        if error:
            return ToolResult(success=False, output="", error=error)
        
        # Execute the tool
        return tool.execute(**kwargs)
```

---

### `src/coding_agent/tools/builtins.py`

```python
"""Built-in tools available to every agent."""

import time
from datetime import datetime

from coding_agent.tools.base import BaseTool
from coding_agent.interfaces.tools import ToolResult


class HelpTool(BaseTool):
    """Shows available tools and their descriptions."""
    
    def __init__(self, registry=None):
        self._registry = registry
    
    @property
    def name(self) -> str:
        return "help"
    
    @property
    def description(self) -> str:
        return "List all available tools with descriptions"
    
    def execute(self, **kwargs) -> ToolResult:
        if not self._registry:
            return ToolResult(success=True, output="No tools registered")
        
        tools = self._registry.list_tools()
        lines = ["Available Tools:", "-" * 40]
        for tool in tools:
            lines.append(f"  {tool.name}: {tool.description}")
        
        return ToolResult(success=True, output="\n".join(lines))


class TimeTool(BaseTool):
    """Returns current time."""
    
    @property
    def name(self) -> str:
        return "time"
    
    @property
    def description(self) -> str:
        return "Get current date and time"
    
    def execute(self, **kwargs) -> ToolResult:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return ToolResult(success=True, output=f"Current time: {now}")


class CalculatorTool(BaseTool):
    """Simple calculator for math operations."""
    
    @property
    def name(self) -> str:
        return "calculate"
    
    @property
    def description(self) -> str:
        return "Calculate mathematical expressions (use: expression='2+2')"
    
    def execute(self, expression: str = "", **kwargs) -> ToolResult:
        try:
            # Security: Only allow safe operations
            allowed = {"__builtins__": {}}
            result = eval(expression, allowed, {})
            return ToolResult(success=True, output=f"Result: {result}")
        except Exception as e:
            return ToolResult(success=False, output="", error=str(e))
    
    def validate(self, expression: str = "", **kwargs) -> str:
        """Validate the expression."""
        if not expression:
            return "Expression is required"
        # Basic security check
        dangerous = ["__", "import", "open", "exec", "eval"]
        for d in dangerous:
            if d in expression.lower():
                return f"Dangerous keyword not allowed: {d}"
        return None
```

---

### `src/coding_agent/context/__init__.py`

```python
"""Context module - Conversation state management."""

from coding_agent.context.manager import ConversationManager

__all__ = ["ConversationManager"]
```

---

### `src/coding_agent/context/manager.py`

```python
"""
Conversation Manager

Manages conversation history and context for the agent.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any


@dataclass
class Message:
    """A single message in the conversation."""
    role: str  # "user", "assistant", "system"
    content: str
    timestamp: float = field(default_factory=lambda: __import__('time').time())


class ConversationManager:
    """Manages conversation history and context."""
    
    def __init__(self, max_messages: int = 100):
        self._messages: List[Message] = []
        self._max_messages = max_messages
    
    def add_message(self, role: str, content: str) -> None:
        """Add a message to the conversation."""
        self._messages.append(Message(role=role, content=content))
        
        # Trim if too long
        if len(self._messages) > self._max_messages:
            self._messages = self._messages[-self._max_messages:]
    
    def get_messages(self) -> List[Dict[str, Any]]:
        """Get all messages as dictionaries."""
        return [
            {"role": m.role, "content": m.content}
            for m in self._messages
        ]
    
    def clear(self) -> None:
        """Clear all messages."""
        self._messages = []
    
    def get_last_n(self, n: int) -> List[Message]:
        """Get last n messages."""
        return self._messages[-n:]
```

---

### `src/coding_agent/events/__init__.py`

```python
"""Events module - Observer pattern implementation (T7)."""

from coding_agent.events.emitter import EventEmitter, LoggingObserver

__all__ = ["EventEmitter", "LoggingObserver"]
```

---

### `src/coding_agent/events/emitter.py`

```python
"""
Event Emitter (T7: Observer Pattern)

Decouples event sources from handlers.
"""

import logging
from typing import List, Dict, Any

from coding_agent.interfaces.events import EventEmitter as EventEmitterInterface
from coding_agent.interfaces.events import AgentObserver

logger = logging.getLogger(__name__)


class EventEmitter(EventEmitterInterface):
    """Concrete event emitter that notifies observers."""
    
    def __init__(self):
        self._observers: List[AgentObserver] = []
    
    def subscribe(self, observer: AgentObserver) -> None:
        """Add an observer."""
        self._observers.append(observer)
    
    def emit(self, event_type: str, data: Dict[str, Any]) -> None:
        """Notify all observers of an event."""
        for observer in self._observers:
            try:
                observer.on_event(event_type, data)
            except Exception as e:
                logger.error(f"Observer failed: {e}")


class LoggingObserver(AgentObserver):
    """Observer that logs all events (T7)."""
    
    def __init__(self, level: str = "INFO"):
        self._level = getattr(logging, level.upper(), logging.INFO)
    
    def on_event(self, event_type: str, data: Dict[str, Any]) -> None:
        """Log the event."""
        logger.log(self._level, f"Event[{event_type}]: {data}")
```

---

### `src/coding_agent/di/__init__.py`

```python
"""Dependency Injection module (T12)."""

from coding_agent.di.container import Container, Lifecycle

__all__ = ["Container", "Lifecycle"]
```

---

### `src/coding_agent/di/container.py`

```python
"""
Dependency Injection Container (T12)

Manages component creation and lifecycle.
"""

from typing import Type, TypeVar, Callable, Dict, Any, Optional
from enum import Enum

T = TypeVar('T')


class Lifecycle(Enum):
    """Component lifecycle options."""
    TRANSIENT = "transient"  # New instance every time
    SINGLETON = "singleton"  # One instance, shared


class Container:
    """
    DI Container for managing component dependencies.
    
    Example:
        container = Container()
        container.register(LLMClient, lambda: MockLLMClient(), Lifecycle.SINGLETON)
        llm = container.resolve(LLMClient)
    """
    
    def __init__(self):
        self._registrations: Dict[Type, tuple] = {}
        self._singletons: Dict[Type, Any] = {}
    
    def register(
        self,
        interface: Type[T],
        factory: Callable[..., T],
        lifecycle: Lifecycle = Lifecycle.TRANSIENT
    ) -> None:
        """Register a component factory."""
        self._registrations[interface] = (factory, lifecycle)
    
    def resolve(self, interface: Type[T]) -> T:
        """Resolve an instance of the given interface."""
        if interface not in self._registrations:
            raise KeyError(f"{interface.__name__} not registered")
        
        factory, lifecycle = self._registrations[interface]
        
        if lifecycle == Lifecycle.SINGLETON:
            if interface not in self._singletons:
                self._singletons[interface] = factory()
            return self._singletons[interface]
        
        return factory()
    
    def is_registered(self, interface: Type) -> bool:
        """Check if interface is registered."""
        return interface in self._registrations


# Global container
_global_container: Optional[Container] = None


def get_global_container() -> Container:
    """Get or create global container."""
    global _global_container
    if _global_container is None:
        _global_container = Container()
    return _global_container
```

---

### `src/coding_agent/agent.py`

```python
"""
Main Agent Class - Brings Everything Together

Architecture (T2-T4):
- Controller: Agent coordinates components
- LLM: Strategy pattern for providers
- Tools: Command pattern for execution
- Events: Observer pattern for notifications
- DI: Container for dependency injection (T12)
"""

import logging
from typing import Optional, List, Dict, Any

from coding_agent.config import AgentConfig, get_config
from coding_agent.interfaces.llm import LLMClient
from coding_agent.interfaces.tools import ToolResult
from coding_agent.interfaces.events import AgentObserver
from coding_agent.llm import create_llm_client
from coding_agent.tools import ToolRegistry, HelpTool, TimeTool, CalculatorTool
from coding_agent.context import ConversationManager
from coding_agent.events import EventEmitter, LoggingObserver
from coding_agent.di import Container, get_global_container

logger = logging.getLogger(__name__)


class Agent:
    """
    Coding Agent - Main orchestrator.
    
    Built with clean architecture from Day 1:
    - SOLID principles
    - Strategy, Command, Observer patterns
    - Dependency injection
    """
    
    def __init__(
        self,
        config: Optional[AgentConfig] = None,
        container: Optional[Container] = None,
    ):
        """
        Initialize the agent with dependency injection.
        
        Args:
            config: Configuration (loads from env if None)
            container: DI container (creates default if None)
        """
        # Configuration (T9-T11)
        self._config = config or get_config()
        
        # Dependency Injection Container (T12)
        self._container = container or get_global_container()
        self._setup_container()
        
        # Core components (resolved from container)
        self._llm: LLMClient = self._container.resolve(LLMClient)
        self._tools = ToolRegistry()
        self._register_builtin_tools()
        
        self._conversation = ConversationManager()
        self._events = EventEmitter()
        self._setup_observers()
        
        logger.info(f"Agent initialized with {self._llm.provider_name}")
    
    def _setup_container(self) -> None:
        """Register components with DI container."""
        from coding_agent.di import Lifecycle
        
        if not self._container.is_registered(LLMClient):
            self._container.register(
                LLMClient,
                lambda: create_llm_client(self._config),
                Lifecycle.SINGLETON,
            )
    
    def _register_builtin_tools(self) -> None:
        """Register built-in tools."""
        self._tools.register(HelpTool(self._tools))
        self._tools.register(TimeTool())
        self._tools.register(CalculatorTool())
    
    def _setup_observers(self) -> None:
        """Set up event observers (T7)."""
        # Add logging observer
        logging_observer = LoggingObserver(self._config.logging.level)
        self._events.subscribe(logging_observer)
    
    def run(self, user_input: str) -> str:
        """
        Main entry point - process user input and return response.
        
        Args:
            user_input: The user's request
            
        Returns:
            Agent's response
        """
        # Emit event
        self._events.emit("user_input", {"input": user_input})
        
        # Add to conversation history
        self._conversation.add_message("user", user_input)
        
        # Handle special commands
        if user_input.startswith("/"):
            return self._handle_command(user_input)
        
        # Process through LLM (Strategy Pattern from T7)
        response = self._llm.complete(user_input)
        
        # Add to history
        self._conversation.add_message("assistant", response.content)
        
        # Emit completion event
        self._events.emit("llm_response", {
            "content": response.content,
            "tokens": response.tokens_used,
        })
        
        return response.content
    
    def _handle_command(self, command: str) -> str:
        """Handle slash commands."""
        parts = command.strip().split()
        cmd = parts[0].lower()
        args = parts[1:] if len(parts) > 1 else []
        
        if cmd == "/help":
            return self._show_help()
        
        elif cmd == "/tools":
            result = self._tools.execute("help")
            return result.output if result.success else result.error
        
        elif cmd == "/clear":
            self._conversation.clear()
            return "Conversation history cleared."
        
        elif cmd == "/status":
            return self._show_status()
        
        elif cmd == "/time":
            result = self._tools.execute("time")
            return result.output if result.success else result.error
        
        else:
            return f"Unknown command: {cmd}. Try /help"
    
    def _show_help(self) -> str:
        """Show help message."""
        return """Available Commands:
  /help     - Show this help
  /tools    - List available tools
  /clear    - Clear conversation history
  /status   - Show agent status
  /time     - Show current time

Or just type naturally to chat with the agent!"""
    
    def _show_status(self) -> str:
        """Show agent status."""
        return f"""Agent Status:
  Provider: {self._llm.provider_name}
  Tools: {len(self._tools.list_tools())} registered
  Messages: {len(self._conversation.get_messages())} in history"""
    
    @property
    def llm_provider(self) -> str:
        """Get current LLM provider name."""
        return self._llm.provider_name
    
    def subscribe(self, observer: AgentObserver) -> None:
        """Subscribe an observer to events."""
        self._events.subscribe(observer)
```

---

### `scripts/run_agent.py`

```python
#!/usr/bin/env python3
"""
Entry point - Run the coding agent interactively.

Usage:
    python scripts/run_agent.py
    
Environment:
    Set DEFAULT_LLM_PROVIDER=mock for testing (no API key needed)
    Set DEFAULT_LLM_PROVIDER=claude and ANTHROPIC_API_KEY for Claude
"""

import os
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from coding_agent import Agent


def main():
    """Run the agent in interactive mode."""
    print("=" * 60)
    print("🤖 Coding Agent - Day 1 Complete")
    print("=" * 60)
    print("\nInitializing...")
    
    try:
        agent = Agent()
        print(f"✓ Agent ready (Provider: {agent.llm_provider})")
        print("\nType /help for commands, or chat naturally!")
        print("Type 'exit' or 'quit' to stop.\n")
        
        while True:
            try:
                user_input = input("> ").strip()
                
                if not user_input:
                    continue
                
                if user_input.lower() in ("exit", "quit", "q"):
                    print("Goodbye!")
                    break
                
                response = agent.run(user_input)
                print(f"\n{response}\n")
                
            except KeyboardInterrupt:
                print("\nGoodbye!")
                break
            except Exception as e:
                print(f"Error: {e}")
    
    except Exception as e:
        print(f"Failed to initialize: {e}")
        print("\nMake sure you've set up your .env file:")
        print("  cp .env.example .env")
        print("  # Edit .env with your API keys")
        sys.exit(1)


if __name__ == "__main__":
    main()
```

---

### `tests/test_agent.py`

```python
"""Tests for the coding agent."""

import pytest
from coding_agent import Agent, AgentConfig
from coding_agent.llm import MockLLMClient
from coding_agent.di import Container, Lifecycle


def test_agent_initialization():
    """Test that agent initializes correctly."""
    # Use mock LLM to avoid needing API keys
    config = AgentConfig()
    config.llm.default_provider = "mock"
    
    # Create container with mock
    container = Container()
    container.register(
        MockLLMClient,
        lambda: MockLLMClient(),
        Lifecycle.SINGLETON
    )
    
    agent = Agent(config=config, container=container)
    assert agent.llm_provider == "Mock (mock-model)"


def test_agent_handles_commands():
    """Test that agent handles slash commands."""
    config = AgentConfig()
    config.llm.default_provider = "mock"
    
    agent = Agent(config=config)
    
    # Test /help
    response = agent.run("/help")
    assert "Available Commands" in response
    
    # Test /clear
    response = agent.run("/clear")
    assert "cleared" in response.lower()


def test_agent_conversation():
    """Test that agent maintains conversation."""
    config = AgentConfig()
    config.llm.default_provider = "mock"
    
    agent = Agent(config=config)
    
    # Send a message
    response1 = agent.run("Hello")
    assert "Mock Response" in response1
    
    # Send another message
    response2 = agent.run("How are you?")
    assert "Mock Response" in response2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
```

---

## 🚀 Running Your Agent

### Step 1: Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -e .

# Copy environment template
cp .env.example .env
# Edit .env with your API keys (or use DEFAULT_LLM_PROVIDER=mock for testing)
```

### Step 2: Run

```bash
# Interactive mode
python scripts/run_agent.py
```

### Step 3: Test

```bash
# Run tests
pytest tests/ -v
```

---

## 🎯 What You Built Today

### Architecture Principles Applied

| Principle | Where It's Used |
|-----------|-----------------|
| **Single Responsibility** | Each module has one job: Agent, LLM, Tools, Context |
| **Open/Closed** | New LLM providers via Strategy, new Tools via registry |
| **Dependency Inversion** | Interfaces in `interfaces/`, implementations separate |
| **Strategy Pattern** | Swappable LLM clients |
| **Command Pattern** | Tool execution with validation |
| **Observer Pattern** | Event system for logging |
| **Dependency Injection** | Container manages component creation |

### Key Features Working

- ✅ **Multi-provider LLM** - Mock, Claude, OpenAI (Day 2: real APIs)
- ✅ **Tool system** - Registry with built-in tools
- ✅ **Conversation history** - Context across messages
- ✅ **Event system** - Observer pattern for extensibility
- ✅ **Configuration** - Environment-based settings
- ✅ **Error handling** - Custom exceptions
- ✅ **Slash commands** - /help, /tools, /clear, /status, /time

---

## 📦 Day 2 Preview

Tomorrow we'll add:

- **Real LLM API integration** - Actual calls to Claude/OpenAI
- **File operations** - Read, write, edit files
- **Shell execution** - Run commands safely
- **Code understanding** - Parse and analyze codebases
- **Agent loop** - Plan → Execute → Verify cycle

---

## ✅ Commit Your Day 1 Work

```bash
git add .
git commit -m "Day 1 Complete: Foundation Architecture

- SOLID principles applied
- Strategy, Command, Observer patterns
- Dependency injection container
- Multi-module project structure
- Working agent with mock LLM
- Tool registry with built-ins
- Event system with observers
- Configuration from environment
- Tests and entry point

Ready for Day 2: File Operations & Real LLMs"

git push origin main
```

---

**Day 1 Complete!** 🎉 You now have a solid foundation with clean architecture. See you in Day 2!
