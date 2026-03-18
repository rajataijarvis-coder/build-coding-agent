# Tutorial 1: What is a Coding Agent?

**Course:** Build Your Own Coding Agent  
**Day:** 1  
**Tutorial:** 1 of 288  
**Estimated Time:** 15 minutes

---

## 🎯 What You'll Learn

By the end of this tutorial, you'll understand:
- What makes a coding agent different from other AI tools
- The key components of a coding agent
- Why we're building one from scratch

---

## 🤖 What IS a Coding Agent?

A **coding agent** is an AI system that can:
1. **Understand** your codebase
2. **Plan** changes across multiple files
3. **Execute** those changes (write code, run commands)
4. **Verify** the results

### Comparison Table

| Tool | What It Does | Example |
|------|--------------|---------|
| **Autocomplete** | Suggests next few characters | GitHub Copilot |
| **Chat** | Answers questions about code | ChatGPT |
| **Coding Agent** | Plans, edits, tests entire features | Claude Code, Aider |

### Key Difference

A coding agent doesn't just *suggest* code - it **acts**:

```
You: "Add error handling to all API endpoints"

Copilot: [Suggests try/except block for current file]

Coding Agent:
1. Scans all files for API endpoints
2. Identifies which need error handling
3. Edits each file
4. Adds appropriate exception types
5. Runs tests to verify
6. Shows you a summary
```

---

## 🏗️ Architecture Overview

A coding agent has 4 main layers:

```
┌─────────────────────────────────────┐
│  1. USER INTERFACE (CLI/IDE)        │  ← You type here
│     - Parse your intent             │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│  2. AGENT CONTROLLER              │  ← The brain
│     - Maintain conversation       │
│     - Decide what to do next      │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│  3. TOOL ORCHESTRATOR             │  ← The hands
│     - Read/write files            │
│     - Run shell commands          │
│     - Search code                 │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│  4. LLM (Claude/GPT)              │  ← The intelligence
│     - Reason about problems       │
│     - Generate code               │
│     - Interpret results           │
└─────────────────────────────────────┘
```

---

## 🔄 How the Loop Works

The magic happens in a **loop**:

```
1. You ask something
2. Agent decides what tools to use
3. Tools execute and return results
4. LLM interprets results
5. Repeat until done
6. Final response to you
```

**Example Flow:**

```
You: "Find all unused imports"

Agent → LLM: "User wants to find unused imports. 
              I should search the codebase."

LLM → Agent: "Use the search_code tool to find import statements"

Agent → Tool: search_code(pattern="^import|^from")

Tool → Agent: [Returns list of imports]

Agent → LLM: "Here are the imports. Which are unused?"

LLM → Agent: "These imports are unused: [list]"

Agent → You: "Found 5 unused imports in 3 files"
```

---

## 🎓 Why Build From Scratch?

You might wonder: "Why not just use Claude Code?"

**Benefits of building your own:**

1. **Deep Understanding** - You'll know exactly how it works
2. **Customization** - Add your own tools, workflows
3. **Cost Control** - Optimize token usage
4. **Privacy** - Run local LLMs
5. **Portfolio** - Impressive project to show
6. **Career** - AI engineering is high-demand

---

## 🛠️ What We'll Build

By the end of this course, you'll have:

- A **CLI tool** you can run: `my-agent "refactor this function"`
- **File operations** with safety checks
- **Shell command** execution
- **Code analysis** (find functions, imports, etc.)
- **Multi-file editing** with git integration
- **Context management** for large codebases
- **Planning** capabilities
- **Tests** and documentation

---

## 📋 Prerequisites Check

Before continuing, make sure you have:

- [ ] Python 3.10+ installed (`python --version`)
- [ ] Basic Python knowledge (functions, classes)
- [ ] Git installed
- [ ] A code editor (VS Code recommended)
- [ ] Terminal/Command line access

**Don't have these?** Pause here and set up your environment.

---

## 🎯 Today's Exercise

**Task:** Write down 3 tasks you'd want your coding agent to do.

Examples:
1. "Find all TODO comments and organize them"
2. "Add type hints to all function signatures"
3. "Refactor this 500-line file into smaller modules"

**Why this matters:** These will become your test cases as we build!

---

## 🚀 Next Tutorial

**Tutorial 2:** System Architecture Deep Dive

We'll draw the complete system diagram and understand:
- How components communicate
- Data flow between layers
- Interface contracts

---

## 💡 Key Takeaways

1. A coding agent **acts**, not just suggests
2. It has 4 layers: UI, Controller, Tools, LLM
3. The core is a **loop**: plan → execute → interpret
4. Building one teaches you AI engineering
5. You'll have a real tool at the end

---

## 📚 Further Reading

- [Claude Code Documentation](https://docs.anthropic.com/en/docs/agents-and-tools/claude-code)
- [Aider Architecture](https://aider.chat/docs/llms.html)
- [ReAct Paper](https://arxiv.org/abs/2210.03629) (advanced)

---

*Next: Tutorial 2 - System Architecture Deep Dive*
