# Build Your Own Coding Agent: Tutorial 1 - What is a Coding Agent?

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

---

## 🏗️ Architecture Overview

A coding agent has 4 main layers:

---

## 🔄 How the Loop Works

The magic happens in a **loop**:

1. You ask something
2. Agent decides what tools to use
3. Tools execute and return results
4. LLM interprets results
5. Repeat until done
6. Final response to you

---

## 🎓 Why Build From Scratch?

**Benefits:**

1. **Deep Understanding** - You'll know exactly how it works
2. **Customization** - Add your own tools, workflows
3. **Cost Control** - Optimize token usage
4. **Privacy** - Run local LLMs
5. **Portfolio** - Impressive project to show
6. **Career** - AI engineering is high-demand

---

## 🛠️ What We'll Build

By the end of this 12-day course, you'll have:

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

## 🎯 Next Tutorial

In Tutorial 2, we'll dive into the system architecture.

---

*This is tutorial 1/24 for Day 1. Let's build something amazing!*