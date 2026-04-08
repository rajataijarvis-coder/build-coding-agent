# Day 3, Tutorial 27: Anthropic Tool Use Format

**Course:** Build Your Own Coding Agent  
**Day:** 3 - Tool Use Loop  
**Tutorial:** 27 of 60  
**Estimated Time:** 60 minutes  

---

## 🎯 What You'll Learn

By the end of this tutorial, you'll:
- Understand **Anthropic's tool_use format** specifically
- Learn the exact API structure for Claude's function calling
- Implement an Anthropic client that handles tool calls correctly
- Parse the nested response structure from Claude
- Build robust error handling for tool_use responses

---

## 🎭 The Big Picture

In Tutorial 25, we learned about the general concept of tool use. In Tutorial 26, we mastered JSON Schema for defining tools. Now we dive into **Anthropic's specific implementation**.

### Why Anthropic Format Matters

Anthropic (Claude) uses a **distinct format** from OpenAI. Understanding this format is critical because:

1. **Different API structure** - Tool calls come in `content` blocks, not a top-level field
2. **Unique response parsing** - Need to handle `tool_use` block type
3. **Stop reason differences** - Claude signals "I need tools" with `stop_reason="tool_use"`
4. **ID tracking** - Each tool call has a unique `id` for tracking

Let's examine the exact format so you can implement it correctly.

---

## 📐 Anthropic Tool Use Architecture

```mermaid
flowchart TD
    A[User Request] --> B[Anthropic API Call]
    
    B --> C[Include tools in request]
    C --> D[tools: [{name, description, input_schema}]]
    D --> E[tool_choice: auto]
    
    E --> F[Claude Response]
    
    F --> G{stop_reason?}
    G -->|"end_turn"| H[Text Response - Done]
    G -->|"tool_use"| I[Tool Use Blocks]
    
    I --> J[Parse content blocks]
    J --> K[Extract tool_use blocks]
    K --> L[Get: name, input, id]
    
    L --> M[Execute Tool]
    M --> N[Return result with tool_use_id]
    N --> B
    
    H --> O[Final Response to User]
```

### Key Differences: Anthropic vs OpenAI

| Aspect | Anthropic (Claude) | OpenAI (GPT) |
|--------|-------------------|--------------|
| **Tool field** | `tools` in request | `tools` in request |
| **Response location** | `content[]` blocks | `tool_calls[]` at top level |
| **Block type** | `tool_use` | `function_call` |
| **Arguments field** | `input` (dict) | `arguments` (JSON string) |
| **Return format** | Separate `tool_result` message | Includes in next request |
| **Stop reason** | `"tool_use"` means tools called | `"tool_calls"` means tools called |

---

## 💻 Implementation

### Step 1: Understanding the Anthropic API Structure

```python
# src/coding_agent/llm/anthropic_client.py
"""
Anthropic Claude client with native tool_use support.

This client handles the specific format Anthropic uses for tool calls,
which is different from OpenAI's function calling.
"""

from typing import List, Dict, Any, Optional
import anthropic
from dataclasses import dataclass


# Import from our previous work
from coding_agent.llm.responses import LLMResponse, ToolCall


class AnthropicToolUseError(Exception):
    """Error during Anthropic tool use execution."""
    pass


class AnthropicClient:
    """
    Anthropic Claude client with native tool_use format support.
    
    Key aspects of Anthropic's format:
    - Tools passed in 'tools' parameter as list of schemas
    - Response contains 'content' blocks of different types
    - 'tool_use' blocks contain the tool call details
    - Stop reason tells us if tools were used
    """
    
    def __init__(
        self, 
        api_key: str, 
        model: str = "claude-3-5-sonnet-20241022",
        max_tokens: int = 4096
    ):
        """
        Initialize the Anthropic client.
        
        Args:
            api_key: Anthropic API key
            model: Claude model to use (default: claude-3-5-sonnet-20241022)
            max_tokens: Maximum tokens in response
        """
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model
        self.max_tokens = max_tokens
    
    def generate(
        self,
        messages: List[Dict[str, str]],
        tools: Optional[List[Dict]] = None,
        system: Optional[str] = None,
        temperature: Optional[float] = None
    ) -> LLMResponse:
        """
        Call Claude with optional tool support.
        
        This is the CORE method that implements Anthropic's tool_use format.
        
        Args:
            messages: Conversation history [{"role": "user", "content": "..."}]
            tools: List of tool schemas (from ToolRegistry.get_schemas())
            system: Optional system prompt
            temperature: Optional temperature setting
            
        Returns:
            LLMResponse with text and/or tool_calls
            
        Example messages format:
        [
            {"role": "user", "content": "What files are in src/?"},
            {"role": "assistant", "content": "I'll check that for you."},
            {"role": "user", "content": "Tool 'list_dir' returned:\n- src/\n- tests/\n- README.md"}
        ]
        """
        # Build the API request
        request_kwargs = {
            "model": self.model,
            "max_tokens": self.max_tokens,
            "messages": messages,
        }
        
        # Add tools if provided - this enables tool_use mode
        if tools:
            request_kwargs["tools"] = tools
            # "auto" lets Claude decide whether to use tools
            # Alternatives: {"type": "tool", "name": "tool_name"} to force specific tool
            request_kwargs["tool_choice"] = {"type": "auto"}
        
        if system:
            request_kwargs["system"] = system
            
        if temperature is not None:
            request_kwargs["temperature"] = temperature
        
        # Make the API call
        try:
            response = self.client.messages.create(**request_kwargs)
        except anthropic.APIConnectionError as e:
            raise AnthropicToolUseError(f"Connection error: {e}") from e
        except anthropic.RateLimitError as e:
            raise AnthropicToolUseError(f"Rate limited: {e}") from e
        except Exception as e:
            raise AnthropicToolUseError(f"API error: {e}") from e
        
        # PARSE THE RESPONSE - This is where Anthropic format matters!
        return self._parse_response(response)


```

### Step 2: Parsing the Anthropic Response Format

```python
    def _parse_response(self, response) -> LLMResponse:
        """
        Parse Anthropic's response into our LLMResponse format.
        
        Anthropic returns a response object with:
        - content: List of content blocks (text, tool_use, etc.)
        - stop_reason: Why generation stopped ("end_turn", "max_tokens", "tool_use")
        - usage: Token usage statistics
        
        The key is handling the 'content' blocks which can be:
        - {"type": "text", "text": "..."}
        - {"type": "tool_use", "name": "...", "input": {...}, "id": "..."}
        """
        text_parts = []
        tool_calls = []
        
        # Iterate through all content blocks
        for block in response.content:
            if block.type == "text":
                # Regular text response from Claude
                text_parts.append(block.text)
                
            elif block.type == "tool_use":
                # THIS IS THE KEY - Claude wants to call a tool!
                # Parse the tool_use block
                tool_call = self._parse_tool_use_block(block)
                tool_calls.append(tool_call)
                
            elif block.type == "tool_result":
                # This is a result from a previous tool call (rare in direct response)
                # Usually handled by adding to messages manually
                pass
                
            else:
                # Future block types - log for awareness
                print(f"⚠️  Unknown content block type: {block.type}")
        
        # Determine stop reason
        stop_reason = response.stop_reason  # "end_turn", "max_tokens", "tool_use"
        
        # Build the response
        return LLMResponse(
            text="\n\n".join(text_parts) if text_parts else None,
            tool_calls=tool_calls if tool_calls else None,
            stop_reason=stop_reason,
            usage=dict(response.usage) if hasattr(response, 'usage') else None
        )
    
    def _parse_tool_use_block(self, block) -> ToolCall:
        """
        Parse a single tool_use block from Anthropic response.
        
        Structure:
        {
            "type": "tool_use",
            "id": "toolu_abc123",  # Unique ID for this call
            "name": "read_file",   # Tool name
            "input": {             # Arguments (already parsed as dict!)
                "path": "/src/main.py"
            }
        }
        
        Note: Anthropic gives us 'input' as a dict, not a JSON string!
        This is different from OpenAI.
        """
        return ToolCall(
            name=block.name,
            arguments=block.input,  # Already a dict, not JSON string!
            tool_id=block.id        # Unique ID for tracking
        )
```

### Step 3: Creating the ToolCall Data Class

```python
# src/coding_agent/llm/responses.py
"""
Response parsing for different LLM providers.
"""

from dataclasses import dataclass
from typing import Optional, List, Dict, Any


@dataclass
class ToolCall:
    """
    Represents a single tool call from an LLM.
    
    This is provider-agnostic - we convert provider-specific
    formats into this unified structure.
    
    Attributes:
        name: Name of the tool to call
        arguments: Dict of arguments to pass to the tool
        tool_id: Optional unique ID for this call (Anthropic provides this)
    """
    name: str
    arguments: Dict[str, Any]
    tool_id: Optional[str] = None
    
    @classmethod
    def from_anthropic(cls, tool_use_block: dict) -> "ToolCall":
        """
        Parse Anthropic's tool_use format.
        
        Anthropic format:
        {
            "type": "tool_use",
            "id": "toolu_abc123",
            "name": "read_file",
            "input": {"path": "/src/main.py"}
        }
        """
        return cls(
            name=tool_use_block["name"],
            arguments=tool_use_block["input"],  # Already parsed!
            tool_id=tool_use_block.get("id")
        )
    
    @classmethod
    def from_openai(cls, function_call: dict) -> "ToolCall":
        """
        Parse OpenAI's function_call format.
        
        OpenAI format:
        {
            "type": "function",
            "id": "call_abc123",
            "function": {
                "name": "read_file",
                "arguments": "{\"path\": \"/src/main.py\"}"
            }
        }
        """
        import json
        return cls(
            name=function_call["function"]["name"],
            arguments=json.loads(function_call["function"]["arguments"]),
            tool_id=function_call.get("id")
        )
    
    def __repr__(self) -> str:
        return f"ToolCall(name={self.name}, args={self.arguments}, id={self.tool_id})"


@dataclass 
class LLMResponse:
    """
    Unified response from any LLM provider.
    
    Attributes:
        text: Text content from the LLM (None if only tool calls)
        tool_calls: List of ToolCall objects (None if only text)
        stop_reason: Why generation stopped
        usage: Token usage information
    """
    text: Optional[str] = None
    tool_calls: Optional[List[ToolCall]] = None
    stop_reason: str = "end_turn"
    usage: Optional[Dict[str, int]] = None
    
    def has_tool_calls(self) -> bool:
        """Check if response contains tool calls."""
        return bool(self.tool_calls)
    
    def has_text(self) -> bool:
        """Check if response contains text."""
        return bool(self.text)
    
    def __repr__(self) -> str:
        text_preview = (
            self.text[:50] + "..." 
            if self.text and len(self.text) > 50 
            else self.text
        ) if self.text else "None"
        tools = len(self.tool_calls) if self.tool_calls else 0
        return f"LLMResponse(text={text_preview}, tool_calls={tools}, stop={self.stop_reason})"
```

### Step 4: Tool Result Return Format

```python
# src/coding_agent/llm/anthropic_client.py (continued)

    def format_tool_result_message(
        self, 
        tool_call: ToolCall, 
        result: str,
        error: Optional[str] = None
    ) -> Dict[str, str]:
        """
        Format a tool result for the next API call.
        
        Anthropic requires tool results as user messages with specific format:
        - role: "user" (not "tool" like OpenAI!)
        - content: Contains tool_use_id reference + the result
        
        This is CRITICAL - many implementations get this wrong!
        
        Args:
            tool_call: The ToolCall that was executed
            result: The result string from tool execution
            error: Optional error message if tool failed
            
        Returns:
            Message dict ready for next API call
        """
        # Build the content - can be string or structured
        if error:
            content = (
                f"Tool '{tool_call.name}' failed with error:\n{error}"
            )
        else:
            content = (
                f"Tool '{tool_call.name}' returned:\n{result}"
            )
        
        return {
            "role": "user",
            "content": content
        }
    
    def build_tool_result_message_for_anthropic(
        self,
        tool_name: str,
        tool_id: str,  # The ID from tool_use block
        result: str
    ) -> Dict[str, Any]:
        """
        Alternative format using tool_result block (newer Anthropic format).
        
        This uses Anthropic's preferred structure with explicit tool_result:
        {
            "type": "tool_result",
            "tool_use_id": "toolu_abc123",
            "content": "result string"
        }
        """
        return {
            "role": "user",
            "content": [
                {
                    "type": "tool_result",
                    "tool_use_id": tool_id,
                    "content": result
                }
            ]
        }
```

### Step 5: Complete Integration Example

```python
# src/coding_agent/agent.py
"""
Agent with Anthropic tool use integration.
"""

from typing import List, Dict, Optional
from coding_agent.tools.registry import ToolRegistry
from coding_agent.llm.responses import LLMResponse, ToolCall


class Agent:
    """
    Autonomous coding agent using Anthropic's tool_use format.
    
    This implementation specifically uses Anthropic's format:
    - Tools in 'tools' parameter
    - Parse 'tool_use' content blocks
    - Return results as 'user' messages
    """
    
    def __init__(
        self,
        llm_client,  # AnthropicClient instance
        tool_registry: ToolRegistry,
        system_prompt: str = "You are a helpful coding assistant.",
        max_iterations: int = 10
    ):
        self.llm = llm_client
        self.tools = tool_registry
        self.system_prompt = system_prompt
        self.max_iterations = max_iterations
    
    def run(self, user_input: str) -> str:
        """
        Run the agent with Anthropic tool use loop.
        
        The loop:
        1. Call LLM with tools (Anthropic format)
        2. Parse response - check stop_reason for tool_use
        3. If tool_use: execute each tool, format results
        4. Add results to messages, repeat
        5. If end_turn: return text response
        """
        # Initialize conversation
        messages = [{"role": "user", "content": user_input}]
        
        # Get tool schemas in Anthropic format
        tool_schemas = self.tools.get_schemas()
        
        iteration = 0
        while iteration < self.max_iterations:
            iteration += 1
            
            # Step 1: Call Anthropic API with tools
            response = self.llm.generate(
                messages=messages,
                tools=tool_schemas if tool_schemas else None,
                system=self.system_prompt
            )
            
            # Step 2: Check if Claude wants to use tools
            # stop_reason="tool_use" means LLM called a tool
            # stop_reason="end_turn" means LLM is done
            if response.stop_reason == "end_turn" or not response.has_tool_calls():
                # Claude is done - return text response
                return response.text or "(No response)"
            
            # Step 3: Execute tool calls
            if response.has_tool_calls():
                for tool_call in response.tool_calls:
                    print(f"🔧 Executing: {tool_call.name}")
                    print(f"   Arguments: {tool_call.arguments}")
                    
                    # Execute the tool
                    try:
                        result = self.tools.execute(
                            tool_call.name, 
                            tool_call.arguments
                        )
                    except Exception as e:
                        result = f"Error: {str(e)}"
                    
                    # Step 4: Format result in Anthropic style
                    # Note: role="user" for tool results (not "tool"!)
                    tool_result_message = self.llm.format_tool_result_message(
                        tool_call=tool_call,
                        result=result
                    )
                    messages.append(tool_result_message)
                    
                    print(f"   Result: {result[:100]}...")
            
            # Loop continues - Claude decides next action
        
        return f"(Max iterations {self.max_iterations} reached)"
```

### Step 6: Running the Agent

```python
# scripts/run_agent.py
"""Run the agent with Anthropic tool use."""

import os
from coding_agent.llm.anthropic_client import AnthropicClient
from coding_agent.tools.registry import ToolRegistry
from coding_agent.tools.file_ops import ReadFileTool, WriteFileTool
from coding_agent.tools.shell import ListDirTool
from coding_agent.agent import Agent


def main():
    # Get API key from environment
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("Error: ANTHROPIC_API_KEY not set")
        print("Set it with: export ANTHROPIC_API_KEY=your-key-here")
        return
    
    # Initialize Anthropic client (with tool_use support!)
    llm = AnthropicClient(
        api_key=api_key,
        model="claude-3-5-sonnet-20241022"
    )
    
    # Set up tools
    tools = ToolRegistry()
    tools.register(ReadFileTool())
    tools.register(WriteFileTool())
    tools.register(ListDirTool())
    
    # System prompt tells Claude how to use tools
    system_prompt = """You are a coding assistant with file access.
When asked about code:
1. Use list_dir to explore directories
2. Use read_file to read file contents
3. Analyze and explain the code
4. Be concise and helpful"""
    
    # Create agent
    agent = Agent(
        llm_client=llm,
        tool_registry=tools,
        system_prompt=system_prompt,
        max_iterations=5
    )
    
    # Run interaction
    print("🤖 Agent ready! Type 'quit' to exit.\n")
    
    while True:
        user_input = input("You: ")
        if user_input.lower() == "quit":
            break
            
        response = agent.run(user_input)
        print(f"\nAgent: {response}\n")


if __name__ == "__main__":
    main()
```

---

## 🔍 Deep Dive: The Anthropic Format Differences

### Why This Matters

Many implementations fail because they treat Anthropic like OpenAI. Here's exactly what's different:

```python
# ❌ WRONG - OpenAI style (will fail with Anthropic)
# OpenAI uses: messages with role="tool", content=result
messages.append({
    "role": "tool",
    "tool_call_id": "call_abc123",
    "content": result
})

# ✅ CORRECT - Anthropic style
# Anthropic uses: messages with role="user", content=result
messages.append({
    "role": "user", 
    "content": f"Tool '{tool_name}' returned:\n{result}"
})
```

### Another Key Difference: Arguments Format

```python
# ❌ WRONG - Treating input as JSON string (OpenAI style)
arguments = json.loads(block["function"]["arguments"])

# ✅ CORRECT - Anthropic gives you a dict directly!
arguments = block["input"]  # Already a Python dict!
```

### Stop Reason Handling

```python
# Anthropic uses different stop_reasons
response.stop_reason values:
- "end_turn" → Claude finished generating, has text response
- "max_tokens" → Hit token limit, response truncated
- "tool_use" → Claude requested tool execution (key one!)
- "stop_sequence" → Hit a stop sequence

# vs OpenAI
# OpenAI uses: finish_reason values
# - "stop" → Completed
# - "length" → Hit token limit  
# - "tool_calls" → Made function calls
```

---

## 🏃 Example Session

```
You: What Python files are in the src directory?

🔧 Executing: list_dir
   Arguments: {'path': 'src'}
   Result: - __init__.py
- agent.py
- config.py
- llm/
- tools/

Agent: I found these files in src/:
- __init__.py
- agent.py
- config.py
- llm/ (directory)
- tools/ (directory)
```

```
You: Read the agent.py file and explain what the Agent class does

🔧 Executing: read_file
   Arguments: {'path': 'src/agent.py'}
   Result: """Agent with Anthropic tool use integration..."""

Agent: The Agent class in agent.py is the main orchestrator:

1. **Purpose**: Coordinates between LLM and tools
2. **Key method**: run() implements the tool use loop
3. **Flow**:
   - Takes user input
   - Calls Claude with available tools
   - If Claude requests tools, executes them
   - Returns results to Claude
   - Repeats until done

The class uses dependency injection for the LLM client and tool registry, making it easy to test and swap components.
```

---

## ✅ Exercise

1. **Run the Agent:**
   ```bash
   export ANTHROPIC_API_KEY=your-key
   python scripts/run_agent.py
   ```

2. **Test Tool Calls:**
   - Ask: "List files in the current directory"
   - Ask: "Read the README.md file"
   - Ask: "What's in the src folder?"

3. **Verify Format:**
   - Add debug print to see the raw Anthropic response
   - Confirm `stop_reason="tool_use"` when tools are called
   - Confirm `content` blocks contain `tool_use` type

4. **Add a New Tool:**
   - Create a GrepTool
   - Register it
   - Test: "Find all files containing 'class Agent'"

---

## 🔗 Integration with Previous Tutorials

This tutorial builds on:
- **T13** (Day 1 Capstone): Base architecture, ToolRegistry, DI
- **T25** (Tool Use Loop): General tool use concept
- **T26** (JSON Schema): Tool schema definitions

### What We Use from T13:
- `ToolRegistry` class with `get_schemas()` and `execute()`
- Agent structure with dependency injection
- Error handling patterns

### What We Use from T25-26:
- `ToolCall` and `LLMResponse` data classes
- JSON Schema format for tools
- The tool use loop concept

---

## 🎯 Next Up

**Tutorial 28:** OpenAI Function Calling Format

We'll cover:
- OpenAI's `function_call` format (different from Anthropic!)
- Converting between formats
- Supporting both providers in one codebase

---

## 📚 Resources

- [Anthropic Tool Use Documentation](https://docs.anthropic.com/en/docs/build-with-claude/tool-use)
- [Anthropic API Reference](https://docs.anthropic.com/en/docs/api-reference)
- [Tool Use Examples](https://github.com/anthropics/claude-code-examples)

---

*"Anthropic's tool_use format is elegant once you understand it. The key insight: tools in request, tool_use blocks in response, user message for results."*