# Day 1, Tutorial 6: SOLID Principles Applied to Agents

**Course:** Build Your Own Coding Agent  
**Day:** 1  
**Tutorial:** 6 of 288  
**Estimated Time:** 25 minutes

---

## 🎯 What You'll Learn

By the end of this tutorial, you'll:
- Understand each SOLID principle in the context of coding agents
- Refactor the SimpleAgent class using SOLID design
- See how these principles make your code testable and extensible

---

## 🏗️ Why SOLID Matters for Agents

In Tutorial 4, we built a simple `SimpleAgent` class. It's functional, but it has problems:

- **Single Responsibility Violation**: The agent handles input, processes commands, formats history, AND manages conversation
- **Open/Closed Violation**: Adding new commands requires modifying the `_handle_command` method
- **Tight Coupling**: Command handling is hard-coded with if/elif/else

Let's fix these issues using SOLID principles.

---

## 🔨 The Five SOLID Principles

### S - Single Responsibility Principle

**Rule:** A class should have one, and only one, reason to change.

**In agent terms:**
- Don't put command handling inside the Agent class
- Don't mix UI logic with business logic
- Each class does one thing well

### O - Open/Closed Principle

**Rule:** Software entities should be open for extension but closed for modification.

**In agent terms:**
- Add new commands without changing existing code
- New tools should work without modifying the tool runner

### L - Liskov Substitution Principle

**Rule:** Objects of a superclass should be replaceable with objects of a subclass.

**In agent terms:**
- Any command should be usable wherever a command is expected
- Different LLM clients should be interchangeable

### I - Interface Segregation Principle

**Rule:** Many small, specific interfaces are better than one large interface.

**In agent terms:**
- Don't force agents to implement methods they don't need
- Tools should have focused, specific interfaces

### D - Dependency Inversion Principle

**Rule:** Depend on abstractions, not concretions.

**In agent terms:**
- The Agent should depend on a `CommandHandler` interface, not a specific implementation
- Tools should be injected, not created internally

---

## 🛠️ Let's Refactor

We'll create a properly structured agent with separate classes:

```
agent_v1/
├── __init__.py
├── agent.py        # Main agent (thin orchestration)
├── commands/
│   ├── __init__.py
│   ├── base.py    # Abstract base command
│   ├── help.py    # Help command
│   ├── history.py # History command
│   └── clear.py   # Clear command
└── history.py     # History management
```

---

## 📁 Step 1: Create the Command Base

Create `commands/base.py`:

```python
#!/usr/bin/env python3
"""
Command pattern base classes for SOLID command handling.
"""

from abc import ABC, abstractmethod
from typing import Any


class Command(ABC):
    """Abstract base class for all commands."""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """The command name (e.g., 'help', 'clear')."""
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """Brief description for help text."""
        pass
    
    @abstractmethod
    def execute(self, context: dict[str, Any]) -> str:
        """
        Execute the command.
        
        Args:
            context: Contains 'history' (list of messages), 'agent' (the agent instance)
            
        Returns:
            The command result as a string
        """
        pass
```

---

## 📁 Step 2: Create Individual Commands

Create `commands/help.py`:

```python
#!/usr/bin/env python3
"""Help command implementation."""

from .base import Command
from typing import Any


class HelpCommand(Command):
    """Show available commands."""
    
    def __init__(self, command_registry: dict[str, Command]):
        self._registry = command_registry
    
    @property
    def name(self) -> str:
        return "help"
    
    @property
    def description(self) -> str:
        return "Show available commands"
    
    def execute(self, context: dict[str, Any]) -> str:
        lines = ["Available commands:"]
        for cmd in self._registry.values():
            lines.append(f"  /{cmd.name} - {cmd.description}")
        return "\n".join(lines)
```

Create `commands/history.py`:

```python
#!/usr/bin/env python3 """History command implementation."""

from .base import Command
from typing import Any


class HistoryCommand(Command):
    """Show conversation history."""
    
    @property
    def name(self) -> str:
        return "history"
    
    @property
    def description(self) -> str:
        return "Show conversation history"
    
    def execute(self, context: dict[str, Any]) -> str:
        history = context.get("history", [])
        if not history:
            return "No history yet."
        
        lines = []
        for msg in history:
            role = "You" if msg["role"] == "user" else "Agent"
            lines.append(f"{role}: {msg['content']}")
        return "\n".join(lines)
```

Create `commands/clear.py`:

```python
#!/usr/bin/env python3 """Clear command implementation."""

from .base import Command
from typing import Any


class ClearCommand(Command):
    """Clear conversation history."""
    
    @property
    def name(self) -> str:
        return "clear"
    
    @property
    def description(self) -> str:
        return "Clear conversation history"
    
    def execute(self, context: dict[str, Any]) -> str:
        history = context.get("history")
        if history is not None:
            history.clear()
        return "History cleared."
```

---

## 📁 Step 3: Create Command Registry (Open/Closed)

Create `commands/registry.py`:

```python
#!/usr/bin/env python3
"""
Command registry - implements Open/Closed Principle.
New commands can be added without modifying this class.
"""

from .base import Command
from typing import Any


class CommandRegistry:
    """Registry for commands - open for extension, closed for modification."""
    
    def __init__(self):
        self._commands: dict[str, Command] = {}
    
    def register(self, command: Command) -> None:
        """Register a new command."""
        self._commands[command.name] = command
    
    def get(self, name: str) -> Command | None:
        """Get a command by name."""
        return self._commands.get(name)
    
    def get_all(self) -> dict[str, Command]:
        """Get all registered commands."""
        return self._commands.copy()
    
    def handle(self, command_name: str, context: dict[str, Any]) -> str:
        """Execute a command by name."""
        command = self.get(command_name)
        if command is None:
            return f"Unknown command: {command_name}"
        return command.execute(context)
```

---

## 📁 Step 4: The Refactored Agent (Dependency Inversion)

Create `agent.py`:

```python
#!/usr/bin/env python3
"""
Coding Agent v1 - Refactored with SOLID Principles
Single Responsibility: Agent only orchestrates, doesn't handle commands directly.
"""

from typing import Any


class Agent:
    """
    The main Agent class - thin orchestrator.
    
    Responsibilities:
    - Run the main loop
    - Manage conversation state
    - Delegate command execution to the command system
    
    This follows Single Responsibility - it does ONE thing: orchestrate.
    """
    
    def __init__(self, command_registry):
        """
        Initialize the agent.
        
        Args:
            command_registry: Any object with handle(command_name, context) method
                              (Dependency Inversion - we depend on interface, not concrete class)
        """
        self._registry = command_registry
        self.conversation_history: list[dict[str, str]] = []
    
    def run(self, user_input: str) -> str:
        """
        Main entry point - the Controller in our architecture.
        
        Flow:
        1. Receive user input
        2. Decide what to do
        3. Return response
        """
        # Store user input
        self.conversation_history.append({"role": "user", "content": user_input})
        
        # Process (delegate to command system)
        response = self._process_input(user_input)
        
        # Store agent response
        self.conversation_history.append({"role": "agent", "content": response})
        
        return response
    
    def _process_input(self, user_input: str) -> str:
        """Process input - delegate to command system."""
        # Check for command
        if user_input.startswith("/"):
            command_name = user_input[1:].strip()
            
            # Create context for command execution
            # This is Dependency Inversion - we pass an abstraction (dict)
            context = {"history": self.conversation_history, "agent": self}
            
            return self._registry.handle(command_name, context)
        
        # Default response (placeholder for LLM)
        return f"Received: '{user_input}'. (LLM integration coming in Tutorial 25!)"
```

---

## 📁 Step 5: Wire It All Together

Create `main.py`:

```python
#!/usr/bin/env python3
"""
Main entry point - wires everything together.
"""

from agent import Agent
from commands.registry import CommandRegistry
from commands.help import HelpCommand
from commands.history import HistoryCommand
from commands.clear import ClearCommand


def create_agent() -> Agent:
    """Factory function - creates and configures the agent."""
    # Create registry (Open/Closed - add new commands without modifying)
    registry = CommandRegistry()
    
    # Register commands - each command is separate (Single Responsibility)
    registry.register(HelpCommand(registry))
    registry.register(HistoryCommand())
    registry.register(ClearCommand())
    
    # Create agent with registry (Dependency Inversion)
    return Agent(registry)


def main():
    print("=" * 50)
    print("Coding Agent v1 - SOLID Principles Demo")
    print("=" * 50)
    print("\nType your message and press Enter.")
    print("Special commands: /help, /history, /clear")
    print("Type 'quit' to exit.\n")
    
    agent = create_agent()
    
    while True:
        user_input = input("You: ").strip()
        
        if user_input.lower() in ['quit', 'exit', 'q']:
            print("\nGoodbye!")
            break
        
        if not user_input:
            continue
        
        response = agent.run(user_input)
        print(f"Agent: {response}\n")


if __name__ == "__main__":
    main()
```

---

## 🧪 Test It

```bash
python main.py
```

**Try these:**

```
You: /help
Agent: Available commands:
  /help - Show available commands
  /history - Show conversation history
  /clear - Clear conversation history

You: Hello
Agent: Received: 'Hello'. (LLM integration coming in Tutorial 25!)

You: /history
Agent: You: /help
Agent: Available commands:
...
You: Hello
Agent: Received: 'Hello'. (LLM integration coming in Tutorial 25!)

You: /clear
Agent: History cleared.

You: /history
Agent: No history yet.
```

---

## 📊 Before vs After Comparison

| Aspect | Before (v0) | After (v1) |
|--------|-------------|------------|
| **Single Responsibility** | Agent handles everything | Agent only orchestrates |
| **Open/Closed** | Modify `_handle_command` for new commands | Add new command class, register it |
| **Testing** | Hard to test individual parts | Each command is independently testable |
| **Adding Commands** | Edit agent code | Create new file, register it |
| **Lines in Agent class** | ~60 | ~25 |

---

## 🧩 Add a New Command (Exercise)

**Task:** Add a `/time` command that shows the current time.

**Steps:**
1. Create `commands/time.py` with a `TimeCommand` class
2. In `main.py`, import and register it

**Solution:**

```python
# commands/time.py
from .base import Command
from datetime import datetime


class TimeCommand(Command):
    @property
    def name(self) -> str:
        return "time"
    
    @property
    def description(self) -> str:
        return "Show current time"
    
    def execute(self, context: dict) -> str:
        return f"Current time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

# In main.py, add:
from commands.time import TimeCommand
registry.register(TimeCommand())
```

**Notice:** You didn't modify ANY existing code to add the new command. That's the **Open/Closed Principle** in action!

---

## 🎯 Key Takeaways

- **S**ingle Responsibility: Each class does one thing
- **O**pen/Closed: Extend without modifying existing code
- **L**iskov Substitution: Commands are interchangeable
- **I**nterface Segregation: Small, focused interfaces
- **D**ependency Inversion: Depend on abstractions

These patterns will be crucial as we add tools, LLM clients, and more complexity.

---

## 🎯 Next Tutorial

In **Tutorial 7**, we'll explore Design Patterns (Strategy, Command, Observer) that work well with agents.

---

## ✅ Commit Your Work

```bash
mkdir -p agent_v1/commands
# Save the files, then:
git add .
git commit -m "Tutorial 6: Refactor agent with SOLID principles"
git push origin main
```

**You've applied professional software design to your agent!** 🏗️

---

*This is tutorial 6/24 for Day 1. Your code is now SOLID!*