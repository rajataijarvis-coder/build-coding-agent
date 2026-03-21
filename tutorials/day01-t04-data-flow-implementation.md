# Day 1, Tutorial 4: Data Flow Implementation

**Course:** Build Your Own Coding Agent  
**Day:** 1  
**Tutorial:** 4 of 288  
**Estimated Time:** 25 minutes

---

## 🎯 What You'll Learn

By the end of this tutorial, you'll:
- Implement the basic data flow loop
- Create your first working agent code
- See how user input travels through the system

---

## 🔄 The Data Flow Loop

From Tutorial 2, you learned the architecture. Now let's implement it:

```
User Input → Controller → LLM → (optional) Tools → Controller → User
```

In this tutorial, we'll build a **simplified version** without the LLM - just the flow structure.

---

## 🛠️ Let's Build It

Create a new file: `agent_v0.py`

```python
#!/usr/bin/env python3
"""
Coding Agent v0.1 - Basic Data Flow
A minimal agent that demonstrates the core loop.
"""

class SimpleAgent:
    """Our first agent - just the flow, no LLM yet."""
    
    def __init__(self):
        self.conversation_history = []
    
    def run(self, user_input: str) -> str:
        """
        Main entry point - the Controller in our architecture.
        
        Flow:
        1. Process input (decide what to do)
        2. Store in history (only for non-commands)
        3. Return response
        """
        # Step 1: Process (Controller logic)
        response = self._process_input(user_input)
        
        # Step 2: Store in history only for non-command messages
        if not user_input.startswith("/"):
            self.conversation_history.append({"role": "user", "content": user_input})
            self.conversation_history.append({"role": "agent", "content": response})
        
        return response
    
    def _process_input(self, user_input: str) -> str:
        """
        Simple processing logic (placeholder for LLM in future).
        
        In a real agent, this would:
        - Send to LLM
        - Parse tool calls
        - Execute tools
        - Return final response
        
        For now, we just echo with a twist.
        """
        # Check for special commands (simulating tool use)
        if user_input.startswith("/"):
            return self._handle_command(user_input)
        
        # Default: echo with acknowledgment
        return f"Received: '{user_input}'. (LLM integration coming in Tutorial 25!)"
    
    def _handle_command(self, command: str) -> str:
        """Simulate tool execution."""
        if command == "/help":
            return """Available commands:
/help - Show this help
/history - Show conversation history
/clear - Clear history"""
        
        elif command == "/history":
            return self._format_history()
        
        elif command == "/clear":
            self.conversation_history.clear()
            return "History cleared."
        
        else:
            return f"Unknown command: {command}. Type /help for available commands."
    
    def _format_history(self) -> str:
        """Format conversation history for display."""
        if not self.conversation_history:
            return "No history yet."
        
        lines = []
        for msg in self.conversation_history:
            role = "You" if msg["role"] == "user" else "Agent"
            lines.append(f"{role}: {msg['content']}")
        return "\n".join(lines)


def main():
    """Run the agent in an interactive loop."""
    print("=" * 50)
    print("Coding Agent v0.1 - Basic Data Flow Demo")
    print("=" * 50)
    print("\nType your message and press Enter.")
    print("Special commands: /help, /history, /clear")
    print("Type 'quit' to exit.\n")
    
    agent = SimpleAgent()
    
    while True:
        # Get user input
        user_input = input("You: ").strip()
        
        # Check for exit
        if user_input.lower() in ['quit', 'exit', 'q']:
            print("\nGoodbye!")
            break
        
        # Skip empty input
        if not user_input:
            continue
        
        # Process through agent (this is THE LOOP)
        response = agent.run(user_input)
        
        # Display response
        print(f"Agent: {response}\n")


if __name__ == "__main__":
    main()
```

---

## 🧪 Test It

Run the agent:

```bash
python agent_v0.py
```

**Try these interactions:**

```
You: Hello
Agent: Received: 'Hello'. (LLM integration coming in Tutorial 25!)

You: /help
Agent: Available commands:
/help - Show this help
/history - Show conversation history
/clear - Clear history

You: /history
Agent: You: Hello
Agent: Received: 'Hello'. (LLM integration coming in Tutorial 25!)

You: /clear
Agent: History cleared.

You: quit
```

---

## 🔍 Code Breakdown

### The `SimpleAgent` Class
This is our **Controller** from the architecture:
- `run()` - Main entry point (receives input, returns response)
- `_process_input()` - Decision logic (will become LLM calls later)
- `_handle_command()` - Tool system simulation

### The Data Flow
1. **User Input** → `input()` in `main()`
2. **Controller** → `agent.run(user_input)`
3. **Processing** → `_process_input()` (placeholder for LLM)
4. **Response** → Returned to `main()`
5. **Display** → `print()` shows it to user

### What's Missing?
- ❌ Real LLM (we'll add in Tutorial 25)
- ❌ Real tools (we'll add file/shell tools in Tutorial 49+)
- ❌ Context management (we'll improve in Tutorial 97+)

But the **structure is there** - the loop works!

---

## 🎯 Exercise: Add a "Tool"

**Task:** Add a `/time` command that shows the current time.

**Hint:** You'll need to:
1. Import `datetime`
2. Add a new condition in `_handle_command()`
3. Return the current time as a string

**Solution:**

```python
import datetime  # Add at top

# In _handle_command(), add:
elif command == "/time":
    return f"Current time: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
```

---

## 🐛 Common Pitfalls

1. **Forgetting to store history**
   - ❌ `self.conversation_history` not updated
   - ✅ Always append both user input and agent response

2. **Not handling empty input**
   - ❌ Empty string causes issues
   - ✅ Check `if not user_input: continue`

3. **Infinite loop without exit**
   - ❌ No way to quit
   - ✅ Always provide 'quit' or 'exit' option

---

## 📝 Key Takeaways

- ✅ The **Controller** is the orchestrator class
- ✅ **Data flow** = Input → Process → Output
- ✅ **History** lets the agent remember context
- ✅ **Commands** simulate tool use (we'll make them real later)
- ✅ This is the **skeleton** - we'll add muscles (LLM) and organs (tools) later

---

## 🎯 Next Tutorial

In **Tutorial 5**, we'll do an OOP refresher and make this code more robust with proper classes and interfaces.

---

## ✅ Commit Your Work

```bash
git add agent_v0.py
git commit -m "Tutorial 4: Implement basic data flow loop"
git push origin main
```

**You've built your first agent code!** 🎉

---

*This is tutorial 4/24 for Day 1. The foundation is set!*