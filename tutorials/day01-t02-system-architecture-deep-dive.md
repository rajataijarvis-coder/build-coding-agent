# Day 1, Tutorial 2: System Architecture Deep Dive

**Course:** Build Your Own Coding Agent  
**Day:** 1  
**Tutorial:** 2 of 288  
**Estimated Time:** 20 minutes

---

## 🎯 What You'll Learn

By the end of this tutorial, you'll understand:
- The high-level architecture of a coding agent
- How components communicate with each other
- Data flow from user input to code execution

---

## 🏗️ System Architecture Overview

A coding agent consists of four main components:

### 1. User Interface (UI)
- Receives user commands
- Displays agent responses
- Shows file changes and execution results

### 2. Controller (The Brain)
- Parses user intent
- Plans multi-step actions
- Manages conversation state

### 3. Tool System
- File operations (read, write, edit)
- Shell command execution
- Code search and analysis

### 4. LLM Client
- Sends prompts to language model
- Handles tool use / function calling
- Processes structured responses

---

## 🔄 Data Flow

```
User Input → Controller → LLM Client → LLM
                              ↓
                    Tool Requests → Tool System
                              ↓
                    Results → Controller → User
```

---

## 📝 Key Insight

The **Controller** is the orchestrator. It doesn't execute code directly - it asks the LLM what to do, then uses the Tool System to execute those actions.

---

## 🎯 Next Tutorial

In Tutorial 3, we'll break down each component in detail.

---

*This is tutorial 2/24 for Day 1. Keep going!*