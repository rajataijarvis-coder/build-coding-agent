# Day 1, Tutorial 12: Dependency Injection - Wiring Everything Together

**Course:** Build Your Own Coding Agent  
**Day:** 1  
**Tutorial:** 12 of 288  
**Estimated Time:** 60 minutes

---

## 🎯 What You'll Learn

By the end of this tutorial, you'll:
- Understand why dependency injection is critical for testable, maintainable code
- Implement a simple dependency injection container
- Use factory functions for creating components
- Apply constructor injection to wire up our Agent
- Manage configuration across the application
- Enable lazy initialization for expensive resources
- Swap implementations at runtime without code changes

---

## 🧩 Why Dependency Injection Matters

Remember in Tutorials 7-8 when we designed the Strategy and Command patterns? We created abstractions like `LLMStrategy`, `Tool`, and `Command`. But we still need a way to connect actual implementations to these abstractions.

Without dependency injection, we'd have **tight coupling**:

```mermaid
flowchart TB
    subgraph "TIGHTLY COUPLED - BAD"
        A[Agent] -->|creates directly| B[AnthropicClient]
        A -->|creates directly| C[InMemoryToolRegistry]
        A -->|creates directly| D[SimpleConversationManager]
        B -->|hard-coded| E[API Key]
        C -->|hard-coded| F[Tools]
    end
    
    style A fill:#ffcdd2,stroke:#f44336
    style B fill:#ffcdd2,stroke:#f44336
    style C fill:#ffcdd2,stroke:#f44336
    style D fill:#ffcdd2,stroke:#f44336
```

Problems with tight coupling:
- **Hard to test** - Can't replace components with mocks
- **Hard to swap** - Changing LLM requires editing Agent code
- **Hard to configure** - No central place for settings
- **Fragile** - Changes to one component break others

With dependency injection, we get **loose coupling**:

```mermaid
flowchart TB
    subgraph "LOOSELY COUPLED - GOOD"
        subgraph Container["🔧 DI Container"]
            C[Provides]
        end
        
        A2[Agent] -->|depends on| I[LLM Interface]
        A2 -->|depends on| T[ToolRegistry Interface]
        A2 -->|depends on| M[Conversation Interface]
        
        I -.->|injected by| C
        T -.->|injected by| C
        M -.->|injected by| C
        
        C -->|creates| Impl1[Claude Client]
        C -->|creates| Impl2[Tool Registry]
        C -->|creates| Impl3[Conversation]
        
        Config[📋 Config] -.->|feeds| C
    end
    
    style A2 fill:#e8f5e9,stroke:#4caf50
    style Container fill:#fff3e0,stroke:#ff9800,stroke-width:3px
    style Config fill:#e3f2fd,stroke:#2196f3
    style I fill:#f3e5f5,stroke:#9c27b0
    style T fill:#f3e5f5,stroke:#9c27b0
    style M fill:#f3e5f5,stroke:#9c27b0
```

Benefits of dependency injection:
- **Easy testing** - Swap real implementations with mocks
- **Easy swapping** - Change implementations via configuration
- **Centralized config** - One place for all settings
- **Flexible initialization** - Lazy loading of expensive resources
- **Clear dependencies** - Explicit about what each component needs

---

## 🎯 Our Goal: Working DI Container

By the end of this tutorial, we'll have:

1. A **DI Container** that manages component creation
2. **Factory functions** for each component type
3. **Configuration management** from environment variables
4. **Constructor injection** in the Agent class
5. **Lazy initialization** for expensive resources
6. **Runtime switching** between implementations

### DI Container Architecture

Here's how the DI Container fits into our architecture:

```mermaid
classDiagram
    class Container {
        +register(interface, factory, lifecycle)
        +resolve(interface) instance
        +create_scope() Scope
        -_registrations: Dict
        -_singletons: Dict
    }
    
    class Agent {
        +llm: LLMClient
        +tools: ToolRegistry
        +context: ConversationManager
        +run(user_input) response
    }
    
    class LLMClient {
        <<abstract>>
        +complete(prompt) response
    }
    
    class ToolRegistry {
        +register(tool)
        +execute(name, args) result
        +list_tools() List
    }
    
    class ConversationManager {
        +add_user_message(text)
        +add_assistant_message(text)
        +get_messages() List
    }
    
    class AgentConfig {
        +llm: LLMConfig
        +tools: ToolConfig
        +logging: LoggingConfig
        +from_environment() AgentConfig
    }
    
    class FactoryFunctions {
        +create_llm_client(config) LLMClient
        +create_tool_registry(config) ToolRegistry
        +create_conversation_manager(config) ConversationManager
    }
    
    Container --> FactoryFunctions : uses
    FactoryFunctions --> AgentConfig : reads
    Container --> LLMClient : creates
    Container --> ToolRegistry : creates
    Container --> ConversationManager : creates
    Agent --> LLMClient : injected
    Agent --> ToolRegistry : injected
    Agent --> ConversationManager : injected
```

### DI Flow

```mermaid
sequenceDiagram
    participant User
    participant Agent
    participant Container
    participant Config
    
    User->>Agent: new Agent()
    Agent->>Container: request LLMClient
    Container->>Config: get provider settings
    Config-->>Container: "claude"
    Container->>Container: create AnthropicClient
    Container-->>Agent: LLMClient instance
    
    Agent->>Container: request ToolRegistry
    Container->>Container: create ToolRegistry with tools
    Container-->>Agent: ToolRegistry instance
    
    Agent->>Container: request ConversationManager
    Container->>Container: create ConversationManager
    Container-->>Agent: ConversationManager instance
    
    Agent-->>User: Agent ready!
```

---

## 🛠️ Let's Build It

### Step 1: Create the Container Module

The DI container is the heart of our wiring system. It knows how to create each component and manages their lifecycles.

```python
# src/coding_agent/di/container.py
"""
Dependency Injection Container - Wires up all components.

This module provides a DI container that:
- Registers component factories
- Manages component lifecycles (singleton, transient)
- Handles configuration
- Enables lazy initialization

Why use a container?
- Centralizes component creation
- Makes testing easy (swap with mocks)
- Enables runtime configuration
- Manages complex dependencies
"""

from typing import (
    Type, TypeVar, Callable, Dict, Any, Optional, 
    get_type_hints, get_origin, get_args
)
from dataclasses import dataclass, field
from enum import Enum
import logging
import os

logger = logging.getLogger(__name__)

# Type variable for generic factory functions
T = TypeVar('T')


class Lifecycle(Enum):
    """Component lifecycle options."""
    TRANSIENT = "transient"  # New instance every time
    SINGLETON = "singleton"  # One instance, shared


@dataclass
class Registration:
    """
    A component registration in the container.
    
    Attributes:
        factory: Function that creates the component
        lifecycle: How the component is instantiated
        instance: Cached singleton instance
    """
    factory: Callable[..., Any]
    lifecycle: Lifecycle = Lifecycle.TRANSIENT
    instance: Optional[Any] = None


class Container:
    """
    Dependency Injection Container.
    
    The container manages all component creation. You register
    factories, then resolve instances when needed.
    
    Example:
        container = Container()
        
        # Register components
        container.register(LLMClient, lambda: AnthropicClient(), Lifecycle.SINGLETON)
        container.register(ToolRegistry, lambda: ToolRegistry(), Lifecycle.SINGLETON)
        
        # Resolve when needed
        llm = container.resolve(LLMClient)
    
    Architecture:
    ┌─────────────────────────────────────────────────────────┐
    │                        Container                        │
    │  ┌─────────────────────────────────────────────────────┐│
    │  │              registrations: Dict                   ││
    │  │  {LLMClient → Registration(factory, singleton)}    ││
    │  │  {ToolRegistry → Registration(...)}                 ││
    │  │  {ConversationManager → Registration(...)}         ││
    │  └─────────────────────────────────────────────────────┘│
    │  ┌─────────────────────────────────────────────────────┐│
    │  │                 resolve(type) → instance            ││
    │  └─────────────────────────────────────────────────────┘│
    └─────────────────────────────────────────────────────────┘
    """
    
    def __init__(self):
        """Initialize an empty container."""
        self._registrations: Dict[Type, Registration] = {}
        self._config: Dict[str, Any] = {}
        
        logger.info("Container created")
    
    def register(
        self, 
        interface: Type[T], 
        factory: Callable[..., T],
        lifecycle: Lifecycle = Lifecycle.TRANSIENT
    ) -> None:
        """
        Register a component with the container.
        
        Args:
            interface: The abstract type (interface class)
            factory: Function that creates the instance
            lifecycle: TRANSIENT (new each time) or SINGLETON (shared)
            
        Example:
            # Singleton - one instance shared
            container.register(
                LLMClient, 
                lambda: AnthropicClient(api_key="xxx"),
                Lifecycle.SINGLETON
            )
            
            # Transient - new instance each time
            container.register(
                ConversationManager,
                lambda: ConversationManager(max_tokens=100000),
                Lifecycle.TRANSIENT
            )
        """
        self._registrations[interface] = Registration(
            factory=factory,
            lifecycle=lifecycle
        )
        logger.debug(f"Registered {interface.__name__} as {lifecycle.value}")
    
    def register_instance(self, interface: Type[T], instance: T) -> None:
        """
        Register an already-created instance.
        
        This is useful for registering mocks during testing or
        pre-configured components.
        
        Args:
            interface: The interface type
            instance: The instance to register
            
        Example:
            # Register a mock for testing
            mock_client = MockLLMClient()
            container.register_instance(LLMClient, mock_client)
        """
        self._registrations[interface] = Registration(
            factory=lambda: instance,
            lifecycle=Lifecycle.SINGLETON,
            instance=instance
        )
        logger.debug(f"Registered instance for {interface.__name__}")
    
    def register_factory(
        self, 
        interface: Type[T], 
        factory: Callable[..., T]
    ) -> None:
        """
        Register a factory function (shorthand for TRANSIENT).
        
        Args:
            interface: The interface type
            factory: Function that creates the instance
        """
        self.register(interface, factory, Lifecycle.TRANSIENT)
    
    def resolve(self, interface: Type[T]) -> T:
        """
        Resolve an instance of the given type.
        
        This is where the magic happens - the container creates
        the instance (or returns cached singleton) for you.
        
        Args:
            interface: The interface type to resolve
            
        Returns:
            An instance of the requested type
            
        Raises:
            KeyError: If the type isn't registered
            Exception: If the factory fails
            
        Example:
            llm_client = container.resolve(LLMClient)
            tool_registry = container.resolve(ToolRegistry)
        """
        if interface not in self._registrations:
            raise KeyError(
                f"{interface.__name__} is not registered. "
                f"Available: {list(self._registrations.keys())}"
            )
        
        registration = self._registrations[interface]
        
        # For singletons, return cached instance
        if registration.lifecycle == Lifecycle.SINGLETON:
            if registration.instance is None:
                logger.debug(f"Creating singleton for {interface.__name__}")
                registration.instance = registration.factory()
            return registration.instance
        
        # For transient, create new instance each time
        logger.debug(f"Creating new {interface.__name__}")
        return registration.factory()
    
    def resolve_with_kwargs(
        self, 
        interface: Type[T], 
        **kwargs: Any
    ) -> T:
        """
        Resolve with additional keyword arguments.
        
        This allows passing context-specific parameters when
        resolving, useful for per-request customization.
        
        Args:
            interface: The interface type
            **kwargs: Additional arguments for the factory
            
        Returns:
            An instance with the given kwargs
        """
        if interface not in self._registrations:
            raise KeyError(f"{interface.__name__} is not registered")
        
        registration = self._registrations[interface]
        
        # Create with kwargs (always transient when using kwargs)
        logger.debug(f"Creating {interface.__name__} with kwargs: {list(kwargs.keys())}")
        return registration.factory(**kwargs)
    
    def is_registered(self, interface: Type[T]) -> bool:
        """
        Check if a type is registered.
        
        Args:
            interface: The interface type to check
            
        Returns:
            True if registered, False otherwise
        """
        return interface in self._registrations
    
    def clear(self) -> None:
        """Clear all registrations and cached instances."""
        self._registrations.clear()
        self._config.clear()
        logger.info("Container cleared")
    
    def clear_singletons(self) -> None:
        """Clear only singleton instances (keep registrations)."""
        for reg in self._registrations.values():
            reg.instance = None
        logger.debug("Singleton instances cleared")
    
    def __repr__(self) -> str:
        return (
            f"Container("
            f"registrations={len(self._registrations)}, "
            f"config={len(self._config)})"
        )


# Global container instance
_global_container: Optional[Container] = None


def get_global_container() -> Container:
    """
    Get the global container instance.
    
    This provides a convenient way to access the container
    from anywhere in the application.
    
    Returns:
        The global Container instance
    """
    global _global_container
    if _global_container is None:
        _global_container = Container()
    return _global_container


def set_global_container(container: Container) -> None:
    """
    Set the global container instance.
    
    This is useful for testing where you want to replace
    the entire container with a mock.
    
    Args:
        container: The Container to use as global
    """
    global _global_container
    _global_container = container
    logger.info(f"Global container set to: {container}")
```

### Step 2: Ensure Configuration is Available

Tutorial 9 already created the configuration system. In Tutorial 12, we ensure the DI container can access it:

```python
# src/coding_agent/config.py
# (This already exists from Tutorial 9 - no changes needed)

# The DI container will use get_config() internally
# Factory functions call get_config() to get settings
```

**No changes needed to config** - T9 config works as-is with DI!

### Step 3: Create Factory Functions

Now let's create the factory functions that the container will use to create components.

```python
# src/coding_agent/factories.py
"""
Factory Functions - Create component instances.

These factories are registered with the DI container to create
components when needed. Each factory knows how to instantiate
its component with the right configuration.

Why factories?
- Encapsulate creation logic
- Handle dependencies between components
- Apply configuration
- Enable dependency injection
"""

from typing import Optional
import logging
import os

from coding_agent.config import AgentConfig, get_config
from coding_agent.llm import LLMClient, AnthropicClient, OpenAIClient, OllamaClient
from coding_agent.tools import ToolRegistry
from coding_agent.tools.builtins import HelpTool, TimeTool, HistoryTool, ClearTool
from coding_agent.context import ConversationManager
from coding_agent.events import EventEmitter, LoggingObserver
from coding_agent.di.container import Container, Lifecycle

logger = logging.getLogger(__name__)


def create_llm_client(config: Optional[AgentConfig] = None) -> LLMClient:
    """
    Create an LLM client based on configuration (from Tutorial 9).
    
    This factory reads the config to determine which LLM
    provider to use, then creates the appropriate client.
    
    Args:
        config: Configuration (uses global if not provided)
        
    Returns:
        LLMClient implementation
        
    Example:
        client = create_llm_client()
        client.complete("Hello")
    """
    config = config or get_config()
    provider = config.llm.default_provider  # Tutorial 9 uses default_provider
    model = config.llm.claude_model if provider == "claude" else config.llm.openai_model
    api_key = config.llm.anthropic_api_key if provider == "claude" else config.llm.openai_api_key
    
    logger.info(f"Creating LLM client: provider={provider}, model={model}")
    
    if provider == "claude":
        return AnthropicClient(
            model=model,
            api_key=api_key,
            temperature=config.llm.temperature,
            max_tokens=config.llm.max_tokens,
        )
    
    elif provider == "openai":
        return OpenAIClient(
            model=model,
            api_key=api_key,
            temperature=config.llm.temperature,
            max_tokens=config.llm.max_tokens,
        )
    
    elif provider == "ollama":
        return OllamaClient(
            model=config.llm.ollama_model,
            base_url="http://localhost:11434",
            temperature=config.llm.temperature,
            max_tokens=config.llm.max_tokens,
        )
    
    else:
        raise ValueError(f"Unknown LLM provider: {provider}")


def create_tool_registry(config: Optional[AgentConfig] = None):
    """
    Create a tool registry with built-in tools (from Tutorial 9).
    
    This factory creates the registry and registers all
    the tools from coding_agent.tools.builtins.
    
    Args:
        config: Configuration (uses global if not provided)
        
    Returns:
        ToolRegistry with registered tools
    """
    config = config or get_config()
    
    registry = ToolRegistry()
    
    # Register Tutorial 9's built-in tools
    registry.register(HelpTool(registry))
    registry.register(TimeTool())
    registry.register(HistoryTool(registry))
    registry.register(ClearTool(registry))
    
    logger.info(f"Tool registry created with {len(registry.list_tools())} tools")
    
    return registry


def create_conversation_manager(config: Optional[AgentConfig] = None):
    """
    Create a conversation manager (from Tutorial 9's Context/Conversation).
    
    Args:
        config: Configuration (uses global if not provided)
        
    Returns:
        ConversationManager implementation
    """
    config = config or get_config()
    
    return ConversationManager(
        max_tokens=config.llm.max_tokens,  # Tutorial 9 uses llm.max_tokens
        debug=config.debug,
    )


def create_event_emitter(config: Optional[AgentConfig] = None):
    """
    Create an event emitter with observers (from Tutorial 9).
    
    This creates the event system and attaches observers
    for logging, debugging, and metrics.
    
    Args:
        config: Configuration (uses global if not provided)
        
    Returns:
        EventEmitter with attached observers
    """
    config = config or get_config()
    
    emitter = EventEmitter()
    
    # Add logging observer
    logging_observer = LoggingObserver(
        level=config.logging.level,  # Tutorial 9 uses logging.level
        verbose=config.logging.verbose_events
    )
    emitter.subscribe(logging_observer)
    
    logger.debug("Event emitter created with logging observer")
    
    return emitter


def create_container(config: Optional[AgentConfig] = None) -> Container:
    """
    Create and configure a DI container.
    
    This is a convenience function that sets up the entire
    container with all component factories.
    
    Args:
        config: Configuration (uses global if not provided)
        
    Returns:
        Fully configured Container
        
    Example:
        # Quick setup
        container = create_container()
        agent = Agent(container=container)
        
        # Or with custom config
        config = load_config(llm={"provider": "ollama"})
        container = create_container(config)
    """
    config = config or get_config()
    container = Container()
    
    # Register factories
    container.register(LLMClient, lambda: create_llm_client(config), Lifecycle.SINGLETON)
    container.register(ToolRegistry, lambda: create_tool_registry(config), Lifecycle.SINGLETON)
    container.register(ConversationManager, lambda: create_conversation_manager(config), Lifecycle.SINGLETON)
    container.register(EventEmitter, lambda: create_event_emitter(config), Lifecycle.SINGLETON)
    
    logger.info(f"Container configured with {len(container._registrations)} registrations")
    
    return container
```

### Step 4: Evolve the Agent to Support DI

Now let's **evolve** the T9-11 Agent to use dependency injection. The DI container becomes the primary way to wire components, with direct creation as fallback.

```python
# src/coding_agent/agent.py
"""Main Agent - evolved with DI from Tutorial 12."""

from typing import Optional, List
import logging

from coding_agent.config import get_config
from coding_agent.llm import LLMClient, ClaudeStrategy, OpenAIStrategy, OllamaStrategy, LLMStrategy
from coding_agent.tools import (
    ToolRegistry,
    ToolCommand,
    CommandResult,
    CommandHistory
)
from coding_agent.tools.builtins import HelpTool, ConfigTool, TimeTool, HistoryTool, ClearTool
from coding_agent.context import ConversationManager
from coding_agent.events import EventEmitter, EventType, LoggingObserver
from coding_agent.factories import (
    create_llm_client,
    create_tool_registry,
    create_conversation_manager,
    create_event_emitter
)
from coding_agent.di.container import Container, Lifecycle, get_global_container

logger = logging.getLogger(__name__)


class Agent:
    """
    Main Agent class - evolved from Tutorial 9-11 with DI.

    In Tutorial 12, we add DI container support:
    - Agent() uses DI container by default (NEW)
    - Agent(container=None) uses direct creation (fallback)
    """

    def __init__(self, container: Optional[Container] = None):
        """
        Initialize the agent - DI mode by default, direct mode as fallback!
        
        Args:
            container: Optional DI container. If None, uses direct creation (T9-11 style).
            
        Example:
            # NEW T12: DI mode (default)
            agent = Agent()
            
            # NEW T12: DI mode (explicit container)
            custom_container = create_container()
            agent = Agent(container=custom_container)
            
            # T9-11 style still possible via direct creation mode
            # (set container=None and it falls back to direct creation)
        """
        self._config = get_config()
        
        if container is None:
            # FALLBACK: Direct creation mode (T9-11 style)
            self._init_direct()
        else:
            # DI mode: Resolve from container
            self._init_with_di(container)
    
    def _init_direct(self):
        """T9-11 style initialization - direct component creation (fallback)."""
        logger.info("Initializing Agent (direct mode - T9-11 style)...")
        
        # LLM with Strategy pattern (from config)
        llm_strategy = self._create_strategy_from_config()
        self._llm = LLMClient(llm_strategy)
        
        # Observer pattern for events
        self._events = EventEmitter()
        verbose = self._config.logging.verbose_events
        self._events.subscribe(LoggingObserver(verbose=verbose))
        
        # Conversation management
        self._conversation = ConversationManager()
        
        # Tools with registry
        self._tools = ToolRegistry()
        self._setup_tools()
        
        # Command history (Command pattern)
        self._command_history: List[CommandResult] = []
        
        # Log startup
        self._events.emit(EventType.LLM_CALL, {
            "provider": self._llm.provider_name,
            "model": self._config.llm.default_provider
        })
        
        logger.info(f"Agent initialized: LLM={self._llm.provider_name}")
    
    def _init_with_di(self, container: Container):
        """NEW: DI mode - resolve components from container."""
        logger.info("Initializing Agent (DI mode)...")
        
        # Ensure container has our factories registered
        self._ensure_container_configured(container)
        
        # Resolve dependencies from container (the DI magic!)
        self._llm = container.resolve(LLMClient)
        self._tools = container.resolve(ToolRegistry)
        self._conversation = container.resolve(ConversationManager)
        self._events = container.resolve(EventEmitter)
        
        # Command history (still created directly - no need for DI)
        self._command_history: List[CommandResult] = []
        
        logger.info(f"Agent initialized via DI: LLM={self._llm.provider_name}")
    
    def _ensure_container_configured(self, container: Container):
        """Register factories if not already in container."""
        if not container.is_registered(LLMClient):
            container.register(
                LLMClient,
                lambda: create_llm_client(self._config),
                Lifecycle.SINGLETON
            )
        if not container.is_registered(ToolRegistry):
            container.register(
                ToolRegistry,
                lambda: create_tool_registry(self._config),
                Lifecycle.SINGLETON
            )
        if not container.is_registered(ConversationManager):
            container.register(
                ConversationManager,
                lambda: create_conversation_manager(self._config),
                Lifecycle.SINGLETON
            )
        if not container.is_registered(EventEmitter):
            container.register(
                EventEmitter,
                lambda: create_event_emitter(self._config),
                Lifecycle.SINGLETON
            )
    
    def _create_strategy_from_config(self) -> LLMStrategy:
        """Original T9-11 method - creates LLM strategy from config."""
        provider = self._config.llm.default_provider.lower()
        
        if provider == "claude" and self._config.llm.has_anthropic_key:
            return ClaudeStrategy(
                api_key=self._config.llm.anthropic_api_key,
                model=self._config.llm.claude_model
            )
        elif provider == "openai" and self._config.llm.has_openai_key:
            return OpenAIStrategy(
                api_key=self._config.llm.openai_api_key,
                model=self._config.llm.openai_model
            )
        else:
            return OllamaStrategy(model=self._config.llm.ollama_model)
    
    def _setup_tools(self) -> None:
        """Original T9-11 method - registers built-in tools."""
        self._tools.register(HelpTool(self._tools))
        self._tools.register(ConfigTool())
        self._tools.register(TimeTool())
        self._tools.register(HistoryTool(self._conversation))
        self._tools.register(ClearTool(self._conversation))

    # === Methods from T9-11 (complete implementation) ===

    @property
    def llm_provider(self) -> str:
        """Get current LLM provider name."""
        return self._llm.provider_name

    def subscribe(self, observer) -> None:
        """Add an event observer."""
        self._events.subscribe(observer)

    def run(self, user_input: str) -> str:
        """Process user input and return response."""
        # Store user message
        self._conversation.add_message("user", user_input)
        self._events.emit(EventType.USER_MESSAGE, {"content": user_input})

        # Handle commands vs LLM
        if user_input.startswith("/"):
            response = self._handle_command(user_input)
        else:
            response = self._handle_llm(user_input)

        # Store and emit response
        self._conversation.add_message("assistant", response)
        self._events.emit(EventType.AGENT_RESPONSE, {"response": response[:100]})

        return response

    def _handle_command(self, command: str) -> str:
        """Handle slash commands using Command pattern."""
        parts = command.split(maxsplit=1)
        cmd_name = parts[0][1:]  # Remove /
        args = parts[1] if len(parts) > 1 else ""

        tool = self._tools.get(cmd_name)
        if not tool:
            return f"Unknown command: /{cmd_name}"

        # Command pattern: Wrap tool in command
        tool_cmd = ToolCommand(tool, args)

        if not tool_cmd.can_execute():
            return f"Cannot execute: /{cmd_name}"

        self._events.emit(EventType.TOOL_START, {"tool": cmd_name})

        try:
            result = tool_cmd.execute()

            # Track in CommandHistory
            self._command_history.append(CommandResult(
                command_name=tool_cmd.name,
                success=True,
                output=result,
                execution_time_ms=tool_cmd.execution_time
            ))

            self._events.emit(EventType.TOOL_COMPLETE, {"tool": cmd_name})
            return result

        except Exception as e:
            # Track failed command
            self._command_history.append(CommandResult(
                command_name=tool_cmd.name,
                success=False,
                error=str(e),
                execution_time_ms=tool_cmd.execution_time
            ))

            self._events.emit(EventType.TOOL_ERROR, {"tool": cmd_name, "error": str(e)})
            return f"Error: {e}"

    def _handle_llm(self, prompt: str) -> str:
        """Use LLM to generate response."""
        self._events.emit(EventType.LLM_CALL, {"prompt": prompt[:100]})

        # Build context from recent messages
        history = self._conversation.get_history()
        context = "\n".join([f"{m.role}: {m.content}" for m in history[-5:]])

        full_prompt = f"Conversation:\n{context}\n\nUser: {prompt}\nAssistant:"
        response = self._llm.complete(full_prompt)

        self._events.emit(EventType.LLM_RESPONSE, {"response": response[:100]})
        return response


def main():
    """Entry point for CLI usage."""
    config = get_config()

    print("=" * 60)
    print("Coding Agent - Tutorial 12 (with DI)")
    print("=" * 60)
    print(f"\nProvider: {config.llm.default_provider}")
    print("Commands: /help, /config, /time, /history, /clear")
    print("Type 'quit' to exit.\n")

    # Use DI by default (Tutorial 12 style)
    agent = Agent()

    while True:
        try:
            user_input = input("You: ").strip()

            if user_input.lower() in ['quit', 'exit', 'q']:
                print("\nGoodbye!")
                break

            if not user_input:
                continue

            response = agent.run(user_input)
            print(f"Agent: {response}\n")

        except KeyboardInterrupt:
            print("\n\nInterrupted. Goodbye!")
            break


if __name__ == "__main__":
    main()
```

**Summary:** Tutorial 12 adds DI while keeping ALL T9-11:
- Same imports
- Same methods
- Same behavior
- Just adds `container` parameter

### Step 5: Add Lazy Initialization Support

def lazy_init_example(
    """
    Initialize the Agent with dependency injection.
    
    This uses constructor injection - all dependencies are
    provided via the constructor, making the Agent easy to
    test and configure.
    
    Args:
        container: DI Container (creates default if None)
        config: Configuration (uses global if None)
        
    Example:
        # Default - uses global container and config
        agent = Agent()
        
        # Custom container
        container = create_container()
        agent = Agent(container=container)
        
        # With custom config
        config = load_config(llm={"model": "claude-3-5-haiku"})
        agent = Agent(config=config)
    """
    # Use provided or create defaults
    self._config = config or get_config()
    self._container = container or get_global_container()
    
    # Ensure container has factories registered
    self._ensure_container_configured()
    
    # Resolve dependencies from container (this is the DI magic!)
    logger.info("Resolving dependencies from container...")
    
    self._llm: LLMClient = self._container.resolve(LLMClient)
    self._tools: ToolRegistry = self._container.resolve(ToolRegistry)
    self._conversation: ConversationManager = self._container.resolve(ConversationManager)
    self._events: EventEmitter = self._container.resolve(EventEmitter)
    
    # Command history
    self._command_history: List[CommandResult] = []
    
    logger.info(f"Agent initialized: LLM={self._llm.provider_name}, tools={len(self._tools.list_tools())}")
    self._events.emit("agent_initialized", {
        "provider": self.llm_provider,
        "tools_count": len(self._tools.list_tools())
    })

def _ensure_container_configured(self):
    """Ensure the container has all necessary registrations."""
    from coding_agent.di.container import Lifecycle
    
    # Register if not already registered
    if not self._container.is_registered(LLMClient):
        self._container.register(
            LLMClient, 
            lambda: create_llm_client(self._config),
            Lifecycle.SINGLETON
        )
    
    if not self._container.is_registered(ToolRegistry):
        self._container.register(
            ToolRegistry,
            lambda: create_tool_registry(self._config),
            Lifecycle.SINGLETON
        )
    
    if not self._container.is_registered(ConversationManager):
        self._container.register(
            ConversationManager,
            lambda: create_conversation_manager(self._config),
            Lifecycle.SINGLETON
        )
    
    if not self._container.is_registered(EventEmitter):
        self._container.register(
            EventEmitter,
            lambda: create_event_emitter(self._config),
            Lifecycle.SINGLETON
        )
```

### Step 5: Add Lazy Initialization Support

Let's add lazy initialization for components that are expensive to create.

```python
# Add to src/coding_agent/container.py

class Lazy:
    """
    Lazy wrapper for deferred initialization.
    
    Use this when you want to defer creation of expensive
    resources until they're actually needed.
    
    Example:
        # This won't create the LLM client until first use
        lazy_llm = Lazy(lambda: create_llm_client())
        
        # First access - creates the instance
        client = lazy_llm.value
        
        # Second access - returns cached instance
        client2 = lazy_llm.value
        # client is same as client2
    """
    
    def __init__(self, factory: Callable[[], T]):
        """
        Initialize with a factory function.
        
        Args:
            factory: Function that creates the instance
        """
        self._factory = factory
        self._instance: Optional[T] = None
    
    @property
    def value(self) -> T:
        """Get the value, creating if necessary."""
        if self._instance is None:
            self._instance = self._factory()
        return self._instance
    
    def reset(self) -> None:
        """Reset the cached instance."""
        self._instance = None


# Add lazy resolution to Container
def resolve_lazy(self, interface: Type[T]) -> Lazy[T]:
    """
    Resolve lazily - create instance on first access.
    
    Args:
        interface: The interface type
        
    Returns:
        Lazy wrapper that creates instance on first access
        
    Example:
        # Won't create LLM until actually used
        lazy_llm = container.resolve_lazy(LLMClient)
        
        # Later...
        client = lazy_llm.value  # Now it creates the instance
    """
    return Lazy(lambda: self.resolve(interface))
```

---

## 🧪 Test It

### Test 1: Basic Container Usage

```python
# Test the container
from coding_agent.di.container import Container, Lifecycle, get_global_container
from coding_agent.config import load_config

# Create container
container = Container()

# Register a simple factory
class MyService:
    def __init__(self, name: str):
        self.name = name
    
    def greet(self):
        return f"Hello from {self.name}"

container.register(
    MyService,
    lambda: MyService("Test Service"),
    Lifecycle.SINGLETON
)

# Resolve twice - should get same instance (singleton)
service1 = container.resolve(MyService)
service2 = container.resolve(MyService)

print(f"Same instance: {service1 is service2}")  # True
print(f"Service says: {service1.greet()}")  # "Hello from Test Service"
```

### Test 2: Configuration Loading

```python
# Test configuration
from coding_agent.config import load_config, LLMProvider

# Load default config
config = load_config()
print(f"Provider: {config.llm.provider}")
print(f"Model: {config.llm.model}")
print(f"Log level: {config.agent.log_level}")

# Override via code
config2 = load_config()
config2.llm.model = "claude-3-5-haiku-20240307"
print(f"Overridden model: {config2.llm.model}")
```

### Test 3: Full Container Setup

```python
# Test complete container with factories
from coding_agent.factories import create_container
from coding_agent.config import load_config

# Create with default config
container = create_container()

# Verify registrations
print(f"LLM registered: {container.is_registered(LLMClient)}")
print(f"Tools registered: {container.is_registered(ToolRegistry)}")
print(f"Conversation registered: {container.is_registered(ConversationManager)}")
print(f"Events registered: {container.is_registered(EventEmitter)}")
```

### Test 4: Agent with DI

```python
# Test the Agent with DI
from coding_agent.agent import Agent

# Create agent - should use DI container
agent = Agent()

print(f"LLM provider: {agent.llm_provider}")
print(f"Tools available: {len(agent._tools.list_tools())}")

# Test a command
response = agent.run("/help")
print(f"Help output: {response[:100]}...")
```

### Test 5: Runtime Provider Switching

```python
# Test switching LLM providers at runtime
import os

# Set to mock for testing
os.environ["LLM_PROVIDER"] = "mock"
os.environ["LLM_MODEL"] = "test-model"

# Create new container with mock
from coding_agent.factories import create_container
container = create_container()

# Create agent with mock
agent = Agent(container=container)
print(f"Provider: {agent.llm_provider}")  # Should be "mock"

# Now switch to another provider (simulated)
class MockProviderSwitch:
    @property
    def provider_name(self) -> str:
        return "switched"
    
    def complete(self, prompt, **kwargs):
        return "Switched provider response!"

# At runtime, you can swap the LLM
agent._llm = MockProviderSwitch()
response = agent.run("Hello")
print(f"After switch: {response}")
```

---

## 🎯 Exercise: Add a New Component with DI

**Task:** Add a new `MetricsCollector` component to track agent usage metrics.

**Requirements:**
1. Create an interface in `interfaces/metrics.py`
2. Create an implementation in `metrics/collector.py`
3. Register it with the container
4. Inject it into the Agent

**Solution:**

```python
# Step 1: Create interface (src/coding_agent/interfaces/metrics.py)
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class Metrics:
    total_requests: int = 0
    total_tokens: int = 0
    total_tool_calls: int = 0

class MetricsCollector(ABC):
    @abstractmethod
    def record_request(self, tokens: int):
        pass
    
    @abstractmethod
    def record_tool_call(self, tool_name: str):
        pass
    
    @abstractmethod
    def get_metrics(self) -> Metrics:
        pass

# Step 2: Create implementation (src/coding_agent/metrics/collector.py)
from coding_agent.interfaces.metrics import MetricsCollector, Metrics

class InMemoryMetricsCollector(MetricsCollector):
    def __init__(self):
        self._metrics = Metrics()
    
    def record_request(self, tokens: int):
        self._metrics.total_requests += 1
        self._metrics.total_tokens += tokens
    
    def record_tool_call(self, tool_name: str):
        self._metrics.total_tool_calls += 1
    
    def get_metrics(self) -> Metrics:
        return self._metrics

# Step 3: Register with container
from coding_agent.factories import create_container

container = create_container()
container.register(
    MetricsCollector,
    lambda: InMemoryMetricsCollector()
)

# Step 4: Inject into Agent
class Agent:
    def __init__(self, metrics: MetricsCollector = None):
        self._metrics = metrics or container.resolve(MetricsCollector)
    
    def run(self, user_input: str) -> str:
        # Record the request
        self._metrics.record_request(len(user_input))
        # ... rest of run method
```

---

## 🐛 Common Pitfalls

### 1. Circular Dependencies

**Problem:** Component A needs B, B needs A - infinite loop!

**Solution:** Use lazy resolution or dependency injection:
```python
# Bad - creates circular dependency
class A:
    def __init__(self):
        self.b = B()  # B might need A!

# Good - inject dependencies
class A:
    def __init__(self, b: B):
        self.b = b  # B is passed in, not created

# Or use lazy resolution
class A:
    def __init__(self):
        self._b = None
    
    @property
    def b(self):
        if self._b is None:
            self._b = create_b()  # Create on demand
        return self._b
```

### 2. Forgetting to Register

**Problem:** "Type is not registered" error

**Solution:** Ensure all dependencies are registered:
```python
# Always register before resolving
container.register(LLMClient, factory, Lifecycle.SINGLETON)
client = container.resolve(LLMClient)  # Works now
```

### 3. Singleton vs Transient Confusion

**Problem:** Getting same instance when you want new ones (or vice versa)

**Solution:** Choose the right lifecycle:
```python
# Use TRANSIENT for components with state you don't want to share
container.register(
    ConversationManager,
    lambda: ConversationManager(),
    Lifecycle.TRANSIENT  # New conversation each time
)

# Use SINGLETON for stateless or shared resources
container.register(
    LLMClient,
    lambda: AnthropicClient(),
    Lifecycle.SINGLETON  # Same client shared
)
```

### 4. Not Using the Container

**Problem:** Creating components directly instead of via container

**Solution:** Always use the container:
```python
# Bad - creates tight coupling
agent = Agent()
agent._llm = AnthropicClient()  # Directly creates!

# Good - uses container
container = create_container()
agent = Agent(container=container)  # Container provides components
```

---

## 📝 Key Takeaways

- ✅ **DI Container** centralizes component creation and management
- ✅ **Constructor injection** passes dependencies via constructor parameters
- ✅ **Factory functions** encapsulate creation logic for each component
- ✅ **Configuration management** loads settings from environment variables
- ✅ **Singleton lifecycle** shares one instance across the application
- ✅ **Transient lifecycle** creates new instance each time
- ✅ **Lazy initialization** defers expensive creation until needed
- ✅ **Runtime swapping** allows changing implementations without code changes
- ✅ **Easy testing** - swap real implementations with mocks
- ✅ **Clear dependencies** - explicit about what each component needs

---

## 🎯 Next Tutorial

In **Tutorial 13**, we'll continue with hands-on implementation. We'll build out:

- The full Agent implementation using all our interfaces
- Connect the LLM client to actual APIs (Anthropic, OpenAI)
- Wire up all components through the container
- Test the complete system end-to-end

This ties together everything we've learned - interfaces, DI, configuration - into a working agent!

---

## ✅ Commit Your Work

```bash
# Stage the new files
git add src/coding_agent/container.py
git add src/coding_agent/config.py
git add src/coding_agent/factories.py
git add src/coding_agent/agent.py  # Updated with DI

# Commit with descriptive message
git commit -m "Tutorial 12: Implement Dependency Injection

- Create Container class for DI management
  - Register factories for component creation
  - Singleton and transient lifecycle support
  - Lazy initialization with Lazy wrapper
  - Global container for app-wide access

- Create Configuration module (AppConfig)
  - Load from environment variables
  - LLM, Agent, and Security config sections
  - Type coercion and validation

- Create factory functions
  - create_llm_client() - provider-specific
  - create_tool_registry() - all built-in tools
  - create_conversation_manager()
  - create_event_emitter()
  - create_container() - full setup

- Update Agent to use constructor injection
  - Resolve dependencies from container
  - _ensure_container_configured() method

Enables:
- Testable components with mocks
- Swappable LLM providers at runtime
- Centralized configuration
- Lazy loading of expensive resources

Following SOLID:
- DIP: Dependencies injected, not created
- OCP: New components via registration, not code changes

Tutorial 12/24 for Day 1 - Foundation complete!"

git push origin main
```

**Your dependency injection system is now complete!** 🎉

You now have a fully wired application where:
- All components are created by the container
- Configuration comes from environment variables
- Components can be swapped at runtime
- Testing is easy with mocks

---

*This is tutorial 12/24 for Day 1. We're building the foundation for our coding agent!*

---

## 📚 Additional Resources

- [Dependency Injection Wikipedia](https://en.wikipedia.org/wiki/Dependency_injection)
- [Python typing module](https://docs.python.org/3/library/typing.html)
- [Martin Fowler on DI](https://martinfowler.com/articles/injection.html)
- [Python dataclasses](https://docs.python.org/3/library/dataclasses.html)
- [Environment variables in Python](https://docs.python.org/3/library/os.html#os.environ)