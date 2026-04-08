# Day 1, Tutorial 6: SOLID Principles Applied to Agents

**Course:** Build Your Own Coding Agent  
**Day:** 1  
**Tutorial:** 6 of 288  
**Estimated Time:** 35 minutes

---

## 🎯 What You'll Learn

By the end of this tutorial, you'll:
- Understand the 5 SOLID principles with practical examples
- Apply each principle to improve our agent code
- Build a more maintainable, testable, and extensible architecture

---

## 📚 What is SOLID?

SOLID is an acronym for 5 design principles that make software:
- **S**ingle Responsibility Principle
- **O**pen/Closed Principle  
- **L**iskov Substitution Principle
- **I**nterface Segregation Principle
- **D**ependency Inversion Principle

These aren't just theory - they solve real problems you'll hit when building agents.

---

## 1️⃣ Single Responsibility Principle (SRP)

**Definition:** A class should have only one reason to change.

### The Problem

In Tutorial 4's `agent_v0.py`, the `SimpleAgent` class did everything:
- Managed conversation history
- Handled all commands
- Formatted output
- Ran the main loop

If we wanted to change how history works, we'd modify `SimpleAgent`.  
If we wanted to add a new command, we'd modify `SimpleAgent`.  
**Multiple reasons to change = SRP violation.**

### The Solution (from Tutorial 5)

We already fixed this! Look at `agent_v1.py`:

```python
class Agent:
    """Only coordinates - doesn't implement details."""
    def run(self, user_input: str) -> str:
        self._conversation.add_message("user", user_input)
        response = self._process_input(user_input)
        self._conversation.add_message("agent", response)
        return response

class ConversationManager:
    """Only manages history - one reason to change."""
    def add_message(self, role: str, content: str) -> None: ...
    def get_history(self) -> tuple[Message, ...]: ...

class ToolRegistry:
    """Only manages tools - one reason to change."""
    def register(self, tool: Tool) -> None: ...
    def get(self, name: str) -> Optional[Tool]: ...
```

Each class has **one job**. Beautiful.

---

## 2️⃣ Open/Closed Principle (OCP)

**Definition:** Open for extension, closed for modification.

### The Problem

Imagine we want to add a new `/weather` command to `agent_v0.py`:

```python
# BAD: Have to modify Agent class
class SimpleAgent:
    def _handle_command(self, command: str) -> str:
        if command == "/help": ...
        elif command == "/time": ...
        elif command == "/weather":  # <-- MODIFYING EXISTING CODE!
            return self._get_weather()
```

Every new tool requires changing the `Agent` class. Risky.

### The Solution

In `agent_v1.py`, we use the `Tool` interface:

```python
# GOOD: Just create a new class, register it. Done.
class WeatherTool(Tool):
    @property
    def name(self) -> str:
        return "weather"
    
    def execute(self, args: str = "") -> str:
        return "Weather: Sunny, 22°C (mock)"

# In Agent._setup_tools():
self._tools.register(WeatherTool())  # One line, no existing code touched!
```

**We extended functionality without modifying existing code.**

---

## 3️⃣ Liskov Substitution Principle (LSP)

**Definition:** Subtypes must be substitutable for their base types.

### The Problem

If `Tool` subclasses don't behave like `Tool`, the registry breaks:

```python
# BAD: Violates LSP
class BrokenTool(Tool):
    def execute(self, args: str = "") -> str:
        raise Exception("Not implemented!")  # Breaks contract!
```

### The Solution

All our tools follow the contract:

```python
class HelpTool(Tool):
    @property
    def name(self) -> str: return "help"
    
    def execute(self, args: str = "") -> str:
        return "Available commands: ..."  # Always returns str

class TimeTool(Tool):
    @property  
    def name(self) -> str: return "time"
    
    def execute(self, args: str = "") -> str:
        return f"Current time: ..."  # Always returns str

# Any Tool can be substituted for any other Tool:
tool: Tool = HelpTool()  # Works
tool = TimeTool()        # Also works!
result = tool.execute("")  # Always returns str, never breaks
```

**All tools are interchangeable.** The `ToolRegistry` doesn't care which specific tool it gets.

---

## 4️⃣ Interface Segregation Principle (ISP)

**Definition:** Clients shouldn't depend on interfaces they don't use.

### The Problem

Imagine a bloated `Tool` interface:

```python
# BAD: Forces all tools to implement everything
class BloatedTool(ABC):
    @abstractmethod
    def execute(self, args: str) -> str: ...
    
    @abstractmethod
    def validate_args(self, args: str) -> bool: ...  # Not all tools need this!
    
    @abstractmethod
    def get_examples(self) -> list[str]: ...  # Not all tools need this!
    
    @abstractmethod
    def rollback(self) -> None: ...  # Not all tools need this!
```

Simple tools like `/time` are forced to implement `rollback()` even though they don't need it.

### The Solution

Keep interfaces minimal and focused:

```python
# GOOD: Only what every tool needs
class Tool(ABC):
    @property
    @abstractmethod
    def name(self) -> str: ...
    
    @property
    @abstractmethod
    def description(self) -> str: ...
    
    @abstractmethod
    def execute(self, args: str = "") -> str: ...

# Optional: Extended interface for complex tools
class ReversibleTool(Tool, ABC):
    @abstractmethod
    def rollback(self) -> None: ...

class FileTool(ReversibleTool):  # Only file tools implement rollback
    def execute(self, args: str) -> str: ...
    def rollback(self) -> None: ...  # Actually needed here
```

**Simple tools stay simple. Complex tools can extend.**

---

## 5️⃣ Dependency Inversion Principle (DIP)

**Definition:** Depend on abstractions, not concretions.

### The Problem

```python
# BAD: Agent depends on concrete classes
class Agent:
    def __init__(self):
        self._conversation = ConversationManager()  # Concrete!
        self._tools = ToolRegistry()  # Concrete!
        self._tools.register(HelpTool())  # Concrete!
        self._tools.register(TimeTool())  # Concrete!
```

Hard to test (can't mock), hard to swap implementations.

### The Solution

Depend on abstractions, inject dependencies:

```python
# GOOD: Depends on abstractions
class Agent:
    def __init__(
        self,
        conversation_manager: ConversationManager,
        tool_registry: ToolRegistry
    ):
        self._conversation = conversation_manager
        self._tools = tool_registry

# Can inject mocks for testing:
mock_conversation = MockConversationManager()
mock_tools = MockToolRegistry()
agent = Agent(mock_conversation, mock_tools)  # Testable!

# Can inject real implementations:
real_agent = Agent(ConversationManager(), ToolRegistry())  # Production!
```

**The agent doesn't care about specific implementations - only that they follow the interface.**

---

## 🛠️ Let's Apply SOLID to Our Agent

Create a new file: `agent_v2.py`

```python
#!/usr/bin/env python3
"""
Coding Agent v2.0 - SOLID Principles Applied
Refactored for better testability, extensibility, and maintainability.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Protocol
import datetime


# ============================================================================
# SRP: Each class has one reason to change
# ============================================================================

@dataclass(frozen=True)
class Message:
    """Immutable message. SRP: Just represent a message."""
    role: str
    content: str
    timestamp: datetime.datetime = field(default_factory=datetime.datetime.now)


class ConversationManager:
    """SRP: Only manage conversation history."""
    
    def __init__(self, max_history: int = 100):
        self._history: List[Message] = []
        self._max_history = max_history
    
    def add_message(self, role: str, content: str) -> None:
        """Add a message to history."""
        message = Message(role=role, content=content)
        self._history.append(message)
        
        if len(self._history) > self._max_history:
            self._history = self._history[-self._max_history:]
    
    def get_history(self) -> tuple[Message, ...]:
        """Get immutable copy of history."""
        return tuple(self._history)
    
    def clear(self) -> None:
        """Clear all history."""
        self._history.clear()
    
    def format_history(self) -> str:
        """Format history for display."""
        if not self._history:
            return "No history yet."
        
        lines = []
        for msg in self._history:
            role_label = "You" if msg.role == "user" else "Agent"
            lines.append(f"{role_label}: {msg.content}")
        return "\n".join(lines)
    
    @property
    def message_count(self) -> int:
        return len(self._history)


# ============================================================================
# ISP: Minimal interface that all tools implement
# ============================================================================

class Tool(ABC):
    """
    ISP: Only what EVERY tool needs.
    No bloated methods that simple tools don't use.
    """
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Tool name for command matching."""
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """Short description for help text."""
        pass
    
    @abstractmethod
    def execute(self, args: str = "") -> str:
        """
        Execute the tool.
        
        LSP: Must return str, must not raise unexpected exceptions.
        """
        pass


# ============================================================================
# OCP: New tools extend functionality without modifying existing code
# ============================================================================

class HelpTool(Tool):
    """OCP: Added without modifying ToolRegistry or Agent."""
    
    def __init__(self, tool_registry: 'ToolRegistry'):
        self._registry = tool_registry
    
    @property
    def name(self) -> str:
        return "help"
    
    @property
    def description(self) -> str:
        return "Show available commands"
    
    def execute(self, args: str = "") -> str:
        return self._registry.get_help_text()


class TimeTool(Tool):
    """OCP: Another extension, no existing code touched."""
    
    @property
    def name(self) -> str:
        return "time"
    
    @property
    def description(self) -> str:
        return "Show current time"
    
    def execute(self, args: str = "") -> str:
        now = datetime.datetime.now()
        return f"Current time: {now.strftime('%Y-%m-%d %H:%M:%S')}"


class HistoryTool(Tool):
    """OCP: Yet another extension."""
    
    def __init__(self, conversation: ConversationManager):
        self._conversation = conversation
    
    @property
    def name(self) -> str:
        return "history"
    
    @property
    def description(self) -> str:
        return "Show conversation history"
    
    def execute(self, args: str = "") -> str:
        return self._conversation.format_history()


class ClearTool(Tool):
    """OCP: One more, still no existing code modified."""
    
    def __init__(self, conversation: ConversationManager):
        self._conversation = conversation
    
    @property
    def name(self) -> str:
        return "clear"
    
    @property
    def description(self) -> str:
        return "Clear conversation history"
    
    def execute(self, args: str = "") -> str:
        self._conversation.clear()
        return "History cleared."


class CountTool(Tool):
    """OCP: Easy to add!"""
    
    def __init__(self, conversation: ConversationManager):
        self._conversation = conversation
    
    @property
    def name(self) -> str:
        return "count"
    
    @property
    def description(self) -> str:
        return "Show message count"
    
    def execute(self, args: str = "") -> str:
        count = self._conversation.message_count
        return f"Total messages: {count}"


# ============================================================================
# SRP: ToolRegistry only manages tools
# ============================================================================

class ToolRegistry:
    """SRP: Only manage tool registration and lookup."""
    
    def __init__(self):
        self._tools: Dict[str, Tool] = {}
    
    def register(self, tool: Tool) -> None:
        """Register a new tool. OCP: Extension point!"""
        self._tools[tool.name] = tool
    
    def get(self, name: str) -> Optional[Tool]:
        """Get a tool by name. DIP: Returns abstract Tool."""
        return self._tools.get(name)
    
    def list_tools(self) -> List[Tool]:
        """Get all registered tools."""
        return list(self._tools.values())
    
    def get_help_text(self) -> str:
        """Generate help text."""
        lines = ["Available commands:"]
        for tool in self._tools.values():
            lines.append(f"  /{tool.name} - {tool.description}")
        return "\n".join(lines)


# ============================================================================
# DIP: Agent depends on abstractions, not concretions
# ============================================================================

class Agent:
    """
    DIP: Depends on ConversationManager and ToolRegistry abstractions.
    
    We can inject:
    - Real implementations (production)
    - Mock implementations (testing)
    - Different implementations (future)
    """
    
    def __init__(
        self,
        conversation: Optional[ConversationManager] = None,
        tools: Optional[ToolRegistry] = None
    ):
        # DIP: Use provided or create default (still depends on abstraction)
        self._conversation = conversation or ConversationManager()
        self._tools = tools or ToolRegistry()
        self._setup_tools()
    
    def _setup_tools(self) -> None:
        """Register all tools. OCP: Easy to add more!"""
        # DIP: Injecting self._tools into tools that need it
        self._tools.register(HelpTool(self._tools))
        self._tools.register(TimeTool())
        self._tools.register(HistoryTool(self._conversation))
        self._tools.register(ClearTool(self._conversation))
        self._tools.register(CountTool(self._conversation))
    
    def run(self, user_input: str) -> str:
        """Main entry point. SRP: Just coordinate."""
        self._conversation.add_message("user", user_input)
        response = self._process_input(user_input)
        self._conversation.add_message("agent", response)
        return response
    
    def _process_input(self, user_input: str) -> str:
        """Process input. SRP: Just decide what to do."""
        if user_input.startswith("/"):
            return self._handle_command(user_input)
        return f"Received: '{user_input}'. (LLM coming in Tutorial 25!)"
    
    def _handle_command(self, user_input: str) -> str:
        """Handle commands. DIP: Uses abstract Tool interface."""
        parts = user_input[1:].split(maxsplit=1)
        command = parts[0] if parts else ""
        args = parts[1] if len(parts) > 1 else ""
        
        tool = self._tools.get(command)
        if tool:
            # LSP: Any Tool works here, no matter which concrete class
            return tool.execute(args)
        
        return f"Unknown command: /{command}. Type /help for available commands."
    
    @property
    def message_count(self) -> int:
        return self._conversation.message_count


# ============================================================================
# MAIN
# ============================================================================

def main():
    """Run the agent."""
    print("=" * 60)
    print("Coding Agent v2.0 - SOLID Principles Applied")
    print("=" * 60)
    print("\nCommands: /help, /time, /history, /clear, /count")
    print("Type 'quit' to exit.\n")
    
    # DIP: Can inject dependencies here if needed
    agent = Agent()
    
    while True:
        try:
            user_input = input("You: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print(f"\nGoodbye! Total messages: {agent.message_count}")
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

---

## 🧪 Test It

```bash
python agent_v2.py
```

**Try the new `/count` command:**

```
You: Hello
Agent: Received: 'Hello'. (LLM coming in Tutorial 25!)

You: /count
Agent: Total messages: 2

You: /help
Agent: Available commands:
  /help - Show available commands
  /time - Show current time
  /history - Show conversation history
  /clear - Clear conversation history
  /count - Show message count

You: /count
Agent: Total messages: 6
```

---

## 🔍 SOLID Check

| Principle | How We Applied It |
|-----------|-------------------|
| **S**ingle Responsibility | `Agent` coordinates, `ConversationManager` manages history, `ToolRegistry` manages tools |
| **O**pen/Closed | Added `/count` tool without modifying `Agent`, `ToolRegistry`, or other tools |
| **L**iskov Substitution | Any `Tool` subclass works in `ToolRegistry` - they're interchangeable |
| **I**nterface Segregation | `Tool` interface is minimal - only 3 methods |
| **D**ependency Inversion | `Agent` depends on `ConversationManager` and `ToolRegistry` abstractions, not concrete classes |

---

## 🎯 Exercise: Add a `/save` Tool

**Task:** Create a tool that saves conversation history to a file.

**Requirements:**
1. Create `SaveTool` class implementing `Tool`
2. Takes optional filename as argument (default: `conversation.txt`)
3. Saves formatted history to file
4. Returns confirmation message

**Hint:** You'll need to inject `ConversationManager` like `HistoryTool` does.

**Solution:**

```python
class SaveTool(Tool):
    """Save conversation to file."""
    
    def __init__(self, conversation: ConversationManager):
        self._conversation = conversation
    
    @property
    def name(self) -> str:
        return "save"
    
    @property
    def description(self) -> str:
        return "Save conversation to file (usage: /save [filename])"
    
    def execute(self, args: str = "") -> str:
        filename = args.strip() or "conversation.txt"
        history = self._conversation.format_history()
        
        try:
            with open(filename, 'w') as f:
                f.write(history)
            return f"Conversation saved to {filename}"
        except Exception as e:
            return f"Error saving: {e}"

# In Agent._setup_tools():
self._tools.register(SaveTool(self._conversation))
```

---

## 🐛 Common Pitfalls

1. **Violating SRP**
   - ❌ `Agent` class that also handles file I/O
   - ✅ Separate `FileTool` for file operations

2. **Violating OCP**
   - ❌ Modifying `Agent.run()` for every new feature
   - ✅ Extend via `Tool` interface

3. **Violating LSP**
   - ❌ `Tool` subclass that returns `None` instead of `str`
   - ✅ All subclasses follow the contract

4. **Violating ISP**
   - ❌ Bloated interface forcing empty implementations
   - ✅ Minimal, focused interfaces

5. **Violating DIP**
   - ❌ `Agent` creating concrete `HelpTool()` directly in `__init__`
   - ✅ Inject via `_setup_tools()` or constructor

---

## 📝 Key Takeaways

- ✅ **SRP** - One class, one job. Easy to understand, easy to test.
- ✅ **OCP** - Extend without modifying. Add features safely.
- ✅ **LSP** - Subtypes are interchangeable. Polymorphism works.
- ✅ **ISP** - Small interfaces. No forced implementations.
- ✅ **DIP** - Depend on abstractions. Testable, flexible code.

---

## 🎯 Next Tutorial

In **Tutorial 7**, we'll learn design patterns (Strategy, Command, Observer) and apply them to make our agent even more powerful.

---

## ✅ Commit Your Work

```bash
git add agent_v2.py
git commit -m "Tutorial 6: Apply SOLID principles to agent architecture"
git push origin main
```

**Your agent is now SOLID!** 🎉

---

*This is tutorial 6/24 for Day 1. The architecture is rock-solid!*
