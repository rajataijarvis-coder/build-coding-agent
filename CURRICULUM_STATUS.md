# 🎓 Build Your Own Coding Agent - Working Curriculum

**Status:** In Progress (28 tutorials written, 32 to create)  
**Current:** Day 1 complete, Day 2-3 partial, Days 4-5 not started

---

## ✅ COMPLETE: Day 1 - Foundations (13 tutorials)

| # | Tutorial | Status |
|---|----------|--------|
| T1 | What is a coding agent? | ✅ Written |
| T2 | System architecture deep dive | ✅ Written |
| T3 | Component breakdown | ✅ Written |
| T4 | Data flow implementation | ✅ Written |
| T5 | OOP refresher: Classes, objects, encapsulation | ✅ Written |
| T6 | SOLID principles applied to agents | ✅ Written |
| T7 | Design patterns: Strategy, Command, Observer | ✅ Written |
| T8 | Project structure: Multi-module Python | ✅ Written |
| T9-T11 | Project setup, Agent skeleton, Architecture | ✅ Written (consolidated) |
| T12 | Dependency injection basics | ✅ Written |
| T13 | Hands-on: Build skeleton architecture | ✅ Written |

**Day 1 Deliverable:** Working skeleton agent with patterns applied

---

## ⚠️ PARTIAL: Day 2 - LLM Integration (24 tutorials planned, 13 written)

### T14-T24: LLM Fundamentals (NEED TO CREATE)
These are brief overviews before the detailed T25-T37.

| # | Tutorial | Status |
|---|----------|--------|
| T14 | LLM landscape: Claude, GPT, Llama, local models | 📝 TO WRITE |
| T15 | API vs local: Tradeoffs and costs | 📝 TO WRITE |
| T16 | Authentication: API keys, rate limits | 📝 TO WRITE |
| T17 | First integration: Connecting agent to LLM | 📝 TO WRITE |
| T18 | Testing with mocks | 📝 TO WRITE |
| T19 | Prompt templates and Jinja2 | 📝 TO WRITE |
| T20 | Streaming responses | 📝 TO WRITE |
| T21 | Handling timeouts and retries | 📝 TO WRITE |
| T22 | Token counting basics | 📝 TO WRITE |
| T23 | Response parsing and validation | 📝 TO WRITE |
| T24 | LLM client factory pattern | 📝 TO WRITE |

### T25-T37: Detailed LLM Coverage (COMPLETE ✅)

| # | Tutorial | Status |
|---|----------|--------|
| T25 | What is an LLM? | ✅ Written |
| T26 | Tokens, context windows, limitations | ✅ Written |
| T27 | Prompt engineering basics | ✅ Written |
| T28 | System prompts vs user prompts | ✅ Written |
| T29 | Temperature, top_p, generation parameters | ✅ Written |
| T30 | Anthropic Claude API overview | ✅ Written |
| T31 | OpenAI GPT API overview | ✅ Written |
| T32 | Local LLMs with Ollama | ✅ Written |
| T33 | API keys and environment setup | ✅ Written |
| T34 | First LLM call: Hello world | ✅ Written |
| T35 | Handling responses: Text vs structured output | ✅ Written |
| T36 | Error handling: Rate limits, timeouts, retries | ✅ Written |
| T37 | Hands-on: Build LLM client module | ✅ Written |

**Day 2 Deliverable:** Agent can chat with LLM (Claude, OpenAI, Ollama)

---

## ⚠️ PARTIAL: Day 3 - Tool System (36 tutorials planned, 4 written)

### T38-T48: Tool System Implementation (NEED TO CREATE)

| # | Tutorial | Status |
|---|----------|--------|
| T38 | Tool architecture review | 📝 TO WRITE |
| T39 | BaseTool class implementation | 📝 TO WRITE |
| T40 | ToolRegistry: Registration and lookup | 📝 TO WRITE |
| T41 | ToolResult and error handling | 📝 TO WRITE |
| T42 | Command pattern for tool execution | 📝 TO WRITE |
| T43 | Built-in tools: help, time, history | 📝 TO WRITE |
| T44 | Tool input validation | 📝 TO WRITE |
| T45 | Tool execution loop | 📝 TO WRITE |
| T46 | Error recovery in tools | 📝 TO WRITE |
| T47 | Tool logging and observability | 📝 TO WRITE |
| T48 | Hands-on: Complete tool system | 📝 TO WRITE |

### T49-T52: Tool Use Format (COMPLETE ✅)

| # | Tutorial | Status |
|---|----------|--------|
| T49 | Why tools? LLM limitations | ✅ Written |
| T50 | Tool use concept: JSON Schema | ✅ Written |
| T51 | Anthropic tool use format | ✅ Written |
| T52 | OpenAI function calling format | ✅ Written |

**Day 3 Deliverable:** Agent has working tool system with built-in tools

---

## 📝 TO WRITE: Day 4 - File Operations + Context (12 tutorials)

| # | Tutorial | Status |
|---|----------|--------|
| T53 | File operations: read_file, write_file | 📝 TO WRITE |
| T54 | Path validation and safety | 📝 TO WRITE |
| T55 | Directory listing and traversal | 📝 TO WRITE |
| T56 | File search: grep and find | 📝 TO WRITE |
| T57 | Multi-file operations | 📝 TO WRITE |
| T58 | The context problem: Token limits | 📝 TO WRITE |
| T59 | Sliding window approach | 📝 TO WRITE |
| T60 | Message history management | 📝 TO WRITE |
| T61 | Context compression basics | 📝 TO WRITE |
| T62 | Conversation persistence | 📝 TO WRITE |
| T63 | Integration: Files + Context | 📝 TO WRITE |
| T64 | Hands-on: File tools + context manager | 📝 TO WRITE |

**Day 4 Deliverable:** Agent can read/write files and manage context

---

## 📝 TO WRITE: Day 5 - Shell + Tool Loop + Polish (12 tutorials)

| # | Tutorial | Status |
|---|----------|--------|
| T65 | Shell tool: execute_shell | 📝 TO WRITE |
| T66 | Command whitelisting | 📝 TO WRITE |
| T67 | Timeout and output limits | 📝 TO WRITE |
| T68 | Tool use loop: LLM decides when to use tools | 📝 TO WRITE |
| T69 | Parsing tool calls from LLM | 📝 TO WRITE |
| T70 | ReAct pattern: Reasoning + Acting | 📝 TO WRITE |
| T71 | Error handling in tool loop | 📝 TO WRITE |
| T72 | Testing with mocked LLM | 📝 TO WRITE |
| T73 | CLI arguments and configuration | 📝 TO WRITE |
| T74 | Logging and observability | 📝 TO WRITE |
| T75 | Documentation and README | 📝 TO WRITE |
| T76 | Hands-on: Package and publish | 📝 TO WRITE |

**Day 5 Deliverable:** Production-ready CLI agent

---

## Summary

| Day | Status | Tutorials | Written | To Write |
|-----|--------|-----------|---------|----------|
| 1 | ✅ Complete | 13 | 13 | 0 |
| 2 | ⚠️ Partial | 24 | 13 | 11 |
| 3 | ⚠️ Partial | 15 | 4 | 11 |
| 4 | 📝 New | 12 | 0 | 12 |
| 5 | 📝 New | 12 | 0 | 12 |
| **Total** | - | **76** | **30** | **46** |

---

## Next Steps

**Priority 1: Bridge gaps**
1. Create T14-T24 (LLM fundamentals - brief)
2. Create T38-T48 (Tool system hands-on)

**Priority 2: Complete course**
3. Create T53-T76 (Files, shell, context, polish)

**Priority 3: Clean up**
4. Ensure all tutorials reference previous ones correctly
5. Add cross-links between tutorials
6. Create comprehensive index

---

## File Naming Convention

- `day01-t01-...` through `day01-t13-...` ✅ Done
- `day02-t14-...` through `day02-t37-...` (T25-T37 exist, T14-T24 to create)
- `day03-t38-...` through `day03-t52-...` (T49-T52 exist, T38-T48 to create)
- `day04-t53-...` through `day04-t64-...` (all to create)
- `day05-t65-...` through `day05-t76-...` (all to create)
