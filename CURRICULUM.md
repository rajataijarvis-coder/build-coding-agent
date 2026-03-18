# 🎓 Build Your Own Coding Agent - Course Curriculum

**Target Audience:** Junior developers with basic Python knowledge  
**Goal:** Production-ready coding agent (like Claude Code)  
**Format:** 24 hourly tutorials per day, building incrementally  
**Duration:** ~10-12 days (240-288 tutorials)  
**Output:** Open-source course + working agent

---

## 📚 Course Structure

### **Phase 1: Foundations (Days 1-3)**
*Core concepts before writing code*

#### Day 1: Architecture & Design Principles
- **T1:** What is a coding agent? (vs copilot, vs IDE)
- **T2:** System architecture overview (diagram)
- **T3:** Component breakdown: UI, Controller, Tools, LLM
- **T4:** Data flow: User → Agent → Tools → LLM → Response
- **T5:** OOP refresher: Classes, objects, encapsulation
- **T6:** SOLID principles applied to agents
- **T7:** Design patterns: Strategy, Command, Observer
- **T8:** Project structure: How to organize multi-module Python
- **T9:** Setting up the project: Poetry, structure, git
- **T10:** Creating our first module: The Agent class skeleton
- **T11:** Interface design: What contracts do we need?
- **T12:** Dependency injection basics
- **T13-T24:** Hands-on: Build the skeleton architecture

#### Day 2: LLM Fundamentals
- **T25:** What is an LLM? (brief, practical)
- **T26:** Tokens, context windows, and limitations
- **T27:** Prompt engineering basics for agents
- **T28:** System prompts vs user prompts
- **T29:** Temperature, top_p, and generation parameters
- **T30:** Anthropic Claude API overview
- **T31:** OpenAI GPT API overview
- **T32:** Local LLMs with Ollama
- **T33:** API keys and environment setup
- **T34:** First LLM call: Hello world
- **T35:** Handling responses: Text vs structured output
- **T36:** Error handling: Rate limits, timeouts, retries
- **T37-T48:** Hands-on: Build the LLM client module

#### Day 3: Tool Use & Function Calling
- **T49:** Why tools? LLM limitations
- **T50:** Tool use concept: LLM requests, code executes
- **T51:** JSON Schema for tool definitions
- **T52:** Anthropic tool use format
- **T53:** OpenAI function calling format
- **T54:** Designing tool interfaces
- **T55:** Tool registry pattern
- **T56:** Tool execution loop
- **T57:** Handling tool results
- **T58:** Error handling in tools
- **T59:** Tool validation and sanitization
- **T60:** Building our first tool: echo
- **T61-T72:** Hands-on: Tool system implementation

---

### **Phase 2: Core Agent (Days 4-6)**
*The heart of the system*

#### Day 4: File Operations
- **T73:** File system as API
- **T74:** read_file tool design
- **T75:** write_file tool design
- **T76:** File safety: Path traversal protection
- **T77:** Git integration: Auto-commit before changes
- **T78:** File diff visualization
- **T79:** Multi-file operations
- **T80:** File watching and change detection
- **T81:** Binary file handling
- **T82:** Large file handling (chunking)
- **T83:** File search and grep
- **T84:** Directory listing and traversal
- **T85-T96:** Hands-on: File tool suite

#### Day 5: Context Management
- **T97:** The context problem: Token limits
- **T98:** Sliding window approach
- **T99:** Message history management
- **T100:** File caching strategies
- **T101:** Relevance scoring: What to keep?
- **T102:** Summarization techniques
- **T103:** Hierarchical context: Project → File → Function
- **T104:** Embedding-based retrieval (QMD-style)
- **T105:** Context compression
- **T106:** User preferences memory
- **T107:** Session persistence
- **T108:** Context visualization for debugging
- **T109-T120:** Hands-on: Context manager

#### Day 6: Shell & Command Execution
- **T121:** Shell tool design
- **T122:** Command whitelisting/blacklisting
- **T123:** Timeout and resource limits
- **T124:** Output capture and streaming
- **T125:** Working directory management
- **T126:** Environment variables
- **T127:** Interactive commands (less, vim)
- **T128:** Background processes
- **T129:** Command history
- **T130:** Error parsing from shell output
- **T131:** Safety: Preventing rm -rf /
- **T132:** Dry-run mode
- **T133-T144:** Hands-on: Shell tool with safety

---

### **Phase 3: Intelligence (Days 7-9)**
*Making it smart*

#### Day 7: Planning & Reasoning
- **T145:** ReAct pattern: Reasoning + Acting
- **T146:** Chain of thought prompting
- **T147:** Planning before execution
- **T148:** Breaking tasks into steps
- **T149:** Step validation and rollback
- **T150:** Multi-turn conversations
- **T151:** Clarifying questions
- **T152:** Intent classification
- **T153:** Task decomposition
- **T154:** Parallel vs sequential execution
- **T155:** Plan visualization
- **T156:** Self-correction loops
- **T157-T168:** Hands-on: Planning engine

#### Day 8: Code Understanding
- **T169:** AST parsing with Python's ast module
- **T170:** Extracting function signatures
- **T171:** Finding function calls
- **T172:** Import analysis
- **T173:** Building a call graph
- **T174:** Code search with tree-sitter
- **T175:** Symbol indexing
- **T176:** Definition finding (go-to-definition)
- **T177:** Reference finding
- **T178:** Code summarization
- **T179:** Dependency analysis
- **T180:** Language detection
- **T181-T192:** Hands-on: Code analysis tools

#### Day 9: Multi-File Editing
- **T193:** Why multi-file matters
- **T194:** Change sets and transactions
- **T195:** Atomic operations: All or nothing
- **T196:** Dependency-aware ordering
- **T197:** Refactoring patterns
- **T198:** Rename across files
- **T199:** Extract function to new file
- **T200:** Import management
- **T201:** Preview mode: See before applying
- **T202:** Undo/redo stack
- **T203:** Conflict detection
- **T204:** Testing changes before committing
- **T205-T216:** Hands-on: Multi-file editor

---

### **Phase 4: Production (Days 10-12)**
*Making it robust and deployable*

#### Day 10: Testing & Quality
- **T217:** Unit testing agent components
- **T218:** Integration testing
- **T219:** Mocking LLM responses
- **T220:** Test scenarios and fixtures
- **T221:** Regression testing
- **T222:** Performance testing
- **T223:** Token usage optimization
- **T224:** Cost tracking
- **T225:** Error rate monitoring
- **T226:** User feedback collection
- **T227:** A/B testing prompts
- **T228:** Continuous evaluation
- **T229-T240:** Hands-on: Test suite

#### Day 11: Safety & Security
- **T241:** Threat model for coding agents
- **T242:** Sandboxing with Docker
- **T243:** Network isolation
- **T244:** Secret management
- **T245:** .env file protection
- **T246:** Confirmation prompts for destructive ops
- **T247:** Read-only mode
- **T248:** Audit logging
- **T249:** Rate limiting
- **T250:** Input sanitization
- **T251:** Output validation
- **T252:** Security headers
- **T253-T264:** Hands-on: Security hardening

#### Day 12: Deployment & Polish
- **T265:** CLI argument parsing
- **T266:** Configuration files
- **T267:** Logging and observability
- **T268:** Progress indicators
- **T269:** Rich terminal UI
- **T270:** Syntax highlighting in output
- **T271:** Markdown rendering
- **T272:** IDE integration (VS Code extension basics)
- **T273:** Documentation generation
- **T274:** Packaging with PyPI
- **T275:** Docker containerization
- **T276:** Final integration test
- **T277-T288:** Hands-on: Polish and package

---

## 🎯 Learning Outcomes

By the end, students will:
1. **Understand** coding agent architecture deeply
2. **Design** complex systems using OOP and patterns
3. **Implement** tool use, context management, planning
4. **Build** production-ready software with tests
5. **Deploy** a working coding agent
6. **Extend** it with custom tools

---

## 📁 Project Structure (Final)

```
coding-agent/
├── pyproject.toml
├── README.md
├── src/
│   ├── coding_agent/
│   │   ├── __init__.py
│   │   ├── agent.py          # Main controller
│   │   ├── llm/
│   │   │   ├── __init__.py
│   │   │   ├── client.py     # LLM abstraction
│   │   │   ├── anthropic.py  # Claude provider
│   │   │   └── openai.py     # GPT provider
│   │   ├── tools/
│   │   │   ├── __init__.py
│   │   │   ├── registry.py   # Tool registration
│   │   │   ├── file.py       # File operations
│   │   │   ├── shell.py      # Command execution
│   │   │   └── code.py       # Code analysis
│   │   ├── context/
│   │   │   ├── __init__.py
│   │   │   ├── manager.py    # Context management
│   │   │   └── memory.py     # Persistence
│   │   ├── planning/
│   │   │   ├── __init__.py
│   │   │   └── engine.py     # Planning logic
│   │   ├── safety/
│   │   │   ├── __init__.py
│   │   │   └── validator.py  # Safety checks
│   │   └── ui/
│   │       ├── __init__.py
│   │       └── cli.py        # User interface
│   └── main.py               # Entry point
├── tests/
│   ├── unit/
│   ├── integration/
│   └── fixtures/
├── docs/
│   └── tutorials/            # Course materials
└── scripts/
    └── setup.sh
```

---

## 🚀 Getting Started

**Prerequisites:**
- Python 3.10+
- Basic Python (functions, classes)
- Git
- API key (Claude or OpenAI)

**Estimated Time:** 10-12 days of hourly tutorials

**Next Step:** Start Day 1, Tutorial 1

---

*This course will be built incrementally and published to jarvis-blog as we progress.*
