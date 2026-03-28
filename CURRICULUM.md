# 🎓 Build Your Own Coding Agent - Streamlined Curriculum

**Target Audience:** Junior developers with basic Python knowledge  
**Goal:** Working CLI coding agent (Claude Code-style) with core concepts  
**Duration:** 5 days (~60 tutorials)  
**Output:** Open-source course + runnable agent

---

## Course Philosophy

**NOT a production system** - Focus on understanding core concepts  
**NOT full Claude Code clone** - Simplified but working version  
**CLI only** - No IDE extensions, no web UI  
**Safety basics only** - Path validation, command whitelisting, but no Docker sandboxing

---

## 📚 Course Structure (5 Days)

### **Day 1: Foundations (T1-T12)**
*Architecture, patterns, skeleton agent*

- **T1:** What is a coding agent? Architecture overview
- **T2:** Design patterns: Strategy, Command, Observer
- **T3:** Project structure with Poetry
- **T4:** Config system with environment variables
- **T5:** LLM client abstraction (Claude/OpenAI/Ollama)
- **T6:** Tool system: Base class, registry, built-ins
- **T7:** Built-in tools: help, time, history, clear
- **T8:** Event system for observability
- **T9:** Agent class: Orchestrating everything
- **T10:** Dependency injection basics
- **T11:** CLI entry point and main loop
- **T12:** **Hands-on:** Build complete skeleton agent

**Day 1 Deliverable:** Agent that can chat and run built-in tools

---

### **Day 2: File Operations (T13-T24)**
*The most important tool: reading and writing code*

- **T13:** File tool design: read_file, write_file
- **T14:** Path validation and safety (no ../ escapes)
- **T15:** Directory listing: list_dir
- **T16:** File search: grep, find
- **T17:** Multi-file operations
- **T18:** Git integration: read-only status check
- **T19:** Error handling: File not found, permission denied
- **T20:** Large file handling (truncation)
- **T21:** Binary file detection
- **T22:** File diff preview
- **T23:** Tool: execute_code (Python one-liners)
- **T24:** **Hands-on:** Complete file tool suite

**Day 2 Deliverable:** Agent can read/write files, search code

---

### **Day 3: Tool Use Loop (T25-T36)**
*The magic: LLM decides when to use tools*

- **T25:** Tool use concept: LLM outputs JSON function calls
- **T26:** JSON Schema for tool definitions
- **T27:** Anthropic tool use format
- **T28:** Parsing tool calls from LLM responses
- **T29:** Tool execution loop: Call → Execute → Return result
- **T30:** Error handling in tool loop
- **T31:** Chain of thought: ReAct pattern (Thought → Action → Observation)
- **T32:** Multi-step tasks: Planning before execution
- **T33:** Self-correction: When tools fail
- **T34:** Token tracking and cost awareness
- **T35:** Conversation persistence (save/load)
- **T36:** **Hands-on:** Complete tool use system

**Day 3 Deliverable:** Agent can reason and use tools autonomously

---

### **Day 4: Shell & Context (T37-T48)**
*Running commands and managing memory*

- **T37:** Shell tool design: execute_shell
- **T38:** Command whitelisting (allow only safe commands)
- **T39:** Timeout and output limits
- **T40:** Working directory management
- **T41:** Context problem: Token limits
- **T42:** Sliding window: Keep recent messages
- **T43:** Message history management
- **T44:** Summary when context overflows
- **T45:** Context compression basics
- **T46:** File context: Caching file contents
- **T47:** Integration: Shell + Files + Context
- **T48:** **Hands-on:** Shell tool with safety + context manager

**Day 4 Deliverable:** Agent can run shell commands, manages context

---

### **Day 5: Polish & Testing (T49-T60)**
*Making it usable and reliable*

- **T49:** Prompt engineering: System prompt design
- **T50:** Testing: Mock LLM for unit tests
- **T51:** Integration test scenarios
- **T52:** Error messages: User-friendly output
- **T53:** Progress indicators for long operations
- **T54:** Configuration file support (not just env vars)
- **T55:** Logging: Structured logs for debugging
- **T56:** CLI arguments: --verbose, --model, --provider
- **T57:** Basic safety review: Path checks, command validation
- **T58:** Documentation: README and usage examples
- **T59:** Final integration: End-to-end demo
- **T60:** **Hands-on:** Package and publish to PyPI

**Day 5 Deliverable:** Production-ready CLI agent, installable via pip

---

## 🎯 What Was Removed

| Original | Removed | Why |
|----------|---------|-----|
| Days 7-9 (Planning, Code Understanding, Multi-file) | ✅ Removed | Advanced features, not core to "basics" |
| Day 10 (Testing) | ✅ Partially removed | T217-T240 → T50-T52 (essentials only) |
| Day 11 (Safety & Security) | ✅ Reduced | T241-T264 → T57 (basics only) |
| Day 12 (Deployment & Polish) | ✅ Reduced | T265-T288 → T53-T60 (CLI focus) |
| Phase 5 (WebMCP) | ✅ Removed | Web integration, not CLI core |
| VS Code extension | ✅ Removed | IDE integration out of scope |
| Docker sandboxing | ✅ Removed | Too complex for learning |
| AST parsing, code analysis | ✅ Removed | Advanced features |
| Multi-file editing transactions | ✅ Removed | Complexity for later |

---

## ✅ What Remains (The Core)

### Must-Have (Kept)
- ✅ Architecture & patterns (T1-T4)
- ✅ Project setup (T3-T4)
- ✅ LLM abstraction (T5)
- ✅ Tool system (T6-T7)
- ✅ File operations (T13-T24) - **Critical**
- ✅ Tool use loop (T25-T36) - **Critical**
- ✅ Shell execution (T37-T40) - **Critical**
- ✅ Context management (T41-T48) - **Critical**
- ✅ Testing basics (T50-T52)
- ✅ CLI polish (T53-T56)

### Nice-to-Have (Kept Simplified)
- ✅ Git integration (T18, read-only)
- ✅ Safety basics (T57, path + command validation)
- ✅ Error handling (T19, T42)
- ✅ Logging (T56)

---

## 📁 Final Project Structure

```
coding-agent/
├── pyproject.toml
├── README.md
├── .env.example
├── src/
│   └── coding_agent/
│       ├── __init__.py
│       ├── agent.py              # Main Agent class
│       ├── cli.py                # Entry point
│       ├── config.py             # Tutorial 9 structure
│       ├── llm/
│       │   ├── __init__.py
│       │   ├── client.py         # LLMClient interface
│       │   ├── anthropic.py      # Claude provider
│       │   ├── openai.py         # GPT provider
│       │   └── ollama.py         # Local LLM
│       ├── tools/
│       │   ├── __init__.py
│       │   ├── base.py           # BaseTool
│       │   ├── registry.py       # ToolRegistry
│       │   ├── builtins.py       # help, time, history, clear
│       │   ├── files.py          # read_file, write_file, list_dir
│       │   ├── shell.py          # execute_shell
│       │   └── search.py         # grep, find
│       ├── context/
│       │   ├── __init__.py
│       │   └── manager.py        # ConversationManager
│       └── events.py             # EventEmitter
└── tests/
    ├── test_agent.py
    ├── test_tools.py
    └── test_integration.py
```

---

## 🎯 Learning Outcomes (Simplified)

By the end, students will:
1. **Understand** agent architecture and design patterns
2. **Build** a working CLI agent that can:
   - Chat with LLM (Claude, OpenAI, Ollama)
   - Read/write files safely
   - Execute shell commands with whitelisting
   - Manage context and token limits
   - Use tools autonomously via LLM function calling
3. **Test** agent with mocked LLM
4. **Package** and publish to PyPI

---

## 🚀 Stretch Goals (Optional)

For students who finish early or want more:

**Bonus Tutorials (not required):**
- B1: Multi-file editing with transactions
- B2: Code understanding with AST parsing
- B3: Planning engine with ReAct
- B4: VS Code extension basics
- B5: Web UI with Flask/FastAPI
- **B6: Sub-Agent Pattern (woodx9 approach) — PLACEHOLDER**
- **B7: Dynamic Tool Generation (hot-reload) — PLACEHOLDER**
- **B6: Sub-Agent Pattern (woodx9 approach) — PLACEHOLDER**
- **B7: Dynamic Tool Generation (hot-reload) — PLACEHOLDER**

---

## 📊 Comparison

| Metric | Original | Streamlined | Reduction |
|--------|----------|-------------|-----------|
| Days | 14 | 5 | 64% |
| Tutorials | ~324 | 60 | 81% |
| Complexity | Production system | Working prototype | - |
| Scope | Full Claude Code | CLI agent | - |
| Safety | Docker sandbox | Path validation | Basics |

---

**Focus:** Understanding over completeness. A working CLI agent beats a half-finished IDE extension.
