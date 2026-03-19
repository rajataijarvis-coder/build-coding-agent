# Day 1, Tutorial 3: Component Breakdown

**Course:** Build Your Own Coding Agent  
**Day:** 1  
**Tutorial:** 3 of 288  
**Estimated Time:** 20 minutes

---

## 🎯 What You'll Learn

By the end of this tutorial, you'll understand:
- The four main components of a coding agent
- What each component does
- How they work together

---

## 🔧 The Four Components

In Tutorial 2, we saw the high-level architecture. Now let's break down each component.

### 1. User Interface (UI)

The **UI** is how you interact with the agent.

**Responsibilities:**
- Receives your commands (text input)
- Displays agent responses
- Shows file changes and execution results
- Provides feedback (progress, errors, confirmations)

**Example:**
```
You: "Refactor the auth module"
Agent: "I'll analyze the auth module and suggest improvements..."
[Shows file changes]
Agent: "Done! I've extracted 3 functions and added type hints."
```

**In our implementation:** We'll build a simple CLI interface first, then optionally add a web UI.

---

### 2. Controller (The Brain)

The **Controller** is the orchestrator. It makes decisions.

**Responsibilities:**
- Parses your intent (what do you want?)
- Plans multi-step actions
- Manages conversation state (what we've done so far)
- Decides when to use tools vs respond directly
- Handles errors and retries

**Example workflow:**
```
1. You: "Add error handling to all API endpoints"
2. Controller: "I need to:
   - Find all API endpoint files
   - Analyze current error handling
   - Add try/except blocks
   - Test the changes"
3. Controller calls tools to execute each step
4. Controller summarizes results
```

**Key insight:** The Controller doesn't execute code itself - it tells other components what to do.

---

### 3. Tool System

The **Tool System** executes actions. It's the "hands" of the agent.

**Responsibilities:**
- File operations (read, write, edit, delete)
- Shell command execution (run tests, install packages)
- Code search (find functions, classes, imports)
- Git operations (commit, branch, diff)

**Example tools:**
```python
# File tool
read_file("/path/to/file.py")
write_file("/path/to/file.py", "content")

# Shell tool
run_command("pytest tests/")
run_command("pip install requests")

# Search tool
find_function("authenticate_user")
find_imports("fastapi")
```

**Safety:** Tools should validate inputs (no deleting root, no rm -rf /).

---

### 4. LLM Client

The **LLM Client** talks to the language model. It's the "voice" of the agent.

**Responsibilities:**
- Sends prompts to the LLM (Claude, GPT, etc.)
- Handles tool use / function calling
- Processes structured responses
- Manages API keys and rate limits
- Handles retries and errors

**Example:**
```python
# Controller sends to LLM Client
prompt = """The user wants to refactor the auth module.
Current file content:
[file content here]

What changes should I make?"""

# LLM Client sends to LLM
response = llm_client.send(prompt)

# LLM responds with tool calls
response = {
    "tool": "edit_file",
    "path": "/path/to/auth.py",
    "changes": [...]
}
```

---

## 🔄 How They Work Together

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│     UI      │────▶│  Controller │────▶│  LLM Client │
└─────────────┘     └──────┬──────┘     └──────┬──────┘
                           │                    │
                           │              ┌─────▼─────┐
                           │              │    LLM    │
                           │              └─────┬─────┘
                           │                    │
                    ┌──────▼──────┐              │
                    │ Tool System │◀─────────────┘
                    └──────┬──────┘
                           │
                    ┌──────▼──────┐
                    │ File System │
                    │   Shell     │
                    └─────────────┘
```

**Flow:**
1. **UI** receives your command
2. **Controller** decides what to do
3. **LLM Client** asks the LLM for guidance
4. **LLM** suggests tool calls
5. **Controller** calls **Tool System**
6. **Tool System** executes and returns results
7. **Controller** sends results back to **LLM**
8. **LLM** provides final response
9. **UI** displays it to you

---

## 🎯 Key Takeaways

- **UI** = Input/output (your window into the agent)
- **Controller** = Decision maker (the brain)
- **Tool System** = Action executor (the hands)
- **LLM Client** = Communication with AI (the voice)
- They work in a loop: UI → Controller → LLM → Tools → Controller → UI

---

## 🛠️ Exercise: Component Mapping

**Task:** For each scenario, identify which component does the work.

1. You type "fix the bug in line 42"
   - UI receives input
   - ______ decides what to do
   - ______ executes the fix

2. Agent shows "Running tests..."
   - ______ displays the message
   - ______ runs the test command

3. Agent asks "Should I commit these changes?"
   - ______ generates the question
   - ______ displays it to you
   - ______ receives your "yes/no"

**Answers:**
1. Controller, Tool System
2. UI, Tool System
3. LLM/Controller, UI, UI

---

## 🎯 Next Tutorial

In Tutorial 4, we'll explore **Data Flow** - how information moves between these components.

---

*This is tutorial 3/24 for Day 1. You're building a mental model of the system!*