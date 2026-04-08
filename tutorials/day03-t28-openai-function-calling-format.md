# Day 3, Tutorial 28: OpenAI Function Calling Format

**Course:** Build Your Own Coding Agent  
**Day:** 3 - Tool Use Loop  
**Tutorial:** 28 of 60  
**Estimated Time:** 60 minutes

---

## 🎯 What You'll Learn

By the end of this tutorial, you'll:
- Understand **OpenAI's function_calling format** (different from Anthropic!)
- Learn the exact API structure for GPT's tool calling
- Implement an OpenAI client that handles function calls correctly
- Parse the nested response structure from GPT-4
- Build a **unified client** that supports both Anthropic and OpenAI

---

## 🎭 The Big Picture

In Tutorial 27, we learned Anthropic's `tool_use` format. Now we dive into **OpenAI's specific implementation**. While both allow LLMs to call tools, the formats are surprisingly different!

### Why You Need Both

As a coding agent developer, you want flexibility:
- **Anthropic (Claude)**: Often better reasoning, competitive pricing
- **OpenAI (GPT-4)**: More mature function calling, wider adoption

Your agent should work with **both** providers. This tutorial shows you how.

---

## 📐 OpenAI Function Calling Architecture

```mermaid
flowchart TD
    A[User Request] --> B[OpenAI API Call]
    
    B --> C[Include tools in request]
    C --> D[tools: [{type: function, function: {name, description, parameters}}]]
    D --> E[function_call: auto]
    
    E --> F[GPT Response]
    
    F --> G{finish_reason?}
    G -->|"stop"| H[Text Response - Done]
    G -->|"tool_calls"| I[Function Calls]
    
    I --> J[Parse tool_calls array]
    J --> K[Extract: id, function.name, function.arguments]
    K --> L[Parse JSON arguments string]
    
    L --> M[Execute Tool]
    M --> N[Add tool result to next request]
    N --> B
    
    H --> O[Final Response to User]
```

### Key Differences: OpenAI vs Anthropic

| Aspect | OpenAI (GPT) | Anthropic (Claude) |
|--------|--------------|-------------------|
| **Tool field** | `tools: [{type: "function", function: {...}}]` | `tools: [{name, description, input_schema}]` |
| **Response location** | `tool_calls[]` at top level | `content[]` blocks with `tool_use` type |
| **Arguments field** | `arguments` is **JSON string** | `input` is **Python dict** |
| **Return format** | Include in `tool` role message | Use `user` role message |
| **Stop reason** | `"tool_calls"` means tools called | `"tool_use"` means tools called |
| **Call ID** | In `tool_calls[].id` | In `tool_use.id` |

---

## 💻 Implementation

### Step 1: Understanding the OpenAI API Structure

```python
# src/coding_agent/llm/openai_client.py
"""
OpenAI GPT client with native function calling support.

This client handles the specific format OpenAI uses for function calls,
which differs from Anthropic's tool_use format.
"""

from typing import List, Dict, Any, Optional
import openai
from openai import OpenAI
import json
from dataclasses import dataclass

# Import from our previous work
from coding_agent.llm.responses import LLMResponse, ToolCall


class OpenAIToolUseError(Exception):
    """Error during OpenAI function calling execution."""
    pass


class OpenAIClient:
    """
    OpenAI GPT client with native function_calling format support.
    
    Key aspects of OpenAI's format:
    - Tools wrapped in {"type": "function", "function": {...}}
    - Response has top-level "tool_calls" array
    - Arguments are a JSON STRING (not dict like Anthropic)
    - finish_reason tells us if functions were called
    """
    
    def __init__(
        self, 
        api_key: str, 
        model: str = "gpt-4o",
        max_tokens: int = 4096
    ):
        """
        Initialize the OpenAI client.
        
        Args:
            api_key: OpenAI API key
            model: GPT model to use (default: gpt-4o)
            max_tokens: Maximum tokens in response
        """
        self.client = OpenAI(api_key=api_key)
        self.model = model
        self.max_tokens = max_tokens
    
    def _convert_tools_to_openai_format(self, tools: List[Dict]) -> List[Dict]:
        """
        Convert our tool schemas to OpenAI's format.
        
        Our format (from T26):
        {
            "name": "read_file",
            "description": "...",
            "input_schema": {...}
        }
        
        OpenAI format:
        {
            "type": "function",
            "function": {
                "name": "read_file",
                "description": "...",
                "parameters": {...}
            }
        }
        """
        openai_tools = []
        for tool in tools:
            openai_tools.append({
                "type": "function",
                "function": {
                    "name": tool["name"],
                    "description": tool["description"],
                    "parameters": tool.get("input_schema", {})
                }
            })
        return openai_tools
    
    def generate(
        self,
        messages: List[Dict[str, str]],
        tools: Optional[List[Dict]] = None,
        system: Optional[str] = None,
        temperature: Optional[float] = None
    ) -> LLMResponse:
        """
        Call GPT with optional function calling support.
        
        This is the CORE method that implements OpenAI's function_calling format.
        
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
            {"role": "tool", "tool_call_id": "call_abc123", "content": "- src/\n- tests/"}
        ]
        """
        # Build the API request
        request_kwargs = {
            "model": self.model,
            "max_tokens": self.max_tokens,
            "messages": messages,
        }
        
        # Add tools if provided - convert to OpenAI format first!
        if tools:
            request_kwargs["tools"] = self._convert_tools_to_openai_format(tools)
            request_kwargs["tool_choice"] = "auto"  # Let GPT decide
        
        # Handle system prompt - OpenAI uses it differently
        if system:
            # OpenAI: system prompt becomes first message
            messages = [{"role": "system", "content": system}] + messages
            
        if temperature is not None:
            request_kwargs["temperature"] = temperature
        
        # Make the API call
        try:
            response = self.client.chat.completions.create(**request_kwargs)
        except openai.APIConnectionError as e:
            raise OpenAIToolUseError(f"Connection error: {e}") from e
        except openai.RateLimitError as e:
            raise OpenAIToolUseError(f"Rate limited: {e}") from e
        except Exception as e:
            raise OpenAIToolUseError(f"API error: {e}") from e
        
        # PARSE THE RESPONSE - This is where OpenAI format matters!
        return self._parse_response(response)


```

### Step 2: Parsing the OpenAI Response Format

```python
    def _parse_response(self, response) -> LLMResponse:
        """
        Parse OpenAI's response into our LLMResponse format.
        
        OpenAI returns a ChatCompletion with:
        - choices: List of completion choices
        - each choice has: message with content and/or tool_calls
        - finish_reason: Why generation stopped
        
        Key insight: tool_calls are at TOP LEVEL of message, not in content blocks!
        """
        # Get the first choice (we're not doing streaming)
        if not response.choices:
            return LLMResponse(text="", stop_reason="empty")
        
        message = response.choices[0].message
        finish_reason = response.choices[0].finish_reason
        
        text_parts = []
        tool_calls = []
        
        # Text content (like Anthropic's text blocks)
        if message.content:
            text_parts.append(message.content)
        
        # Function calls (OpenAI's tool_calls - different from Anthropic!)
        if message.tool_calls:
            for tc in message.tool_calls:
                tool_call = self._parse_tool_call(tc)
                tool_calls.append(tool_call)
        
        # Build the response
        return LLMResponse(
            text="\n\n".join(text_parts) if text_parts else None,
            tool_calls=tool_calls if tool_calls else None,
            stop_reason=finish_reason,
            usage={
                "prompt_tokens": response.usage.prompt_tokens if response.usage else 0,
                "completion_tokens": response.usage.completion_tokens if response.usage else 0,
                "total_tokens": response.usage.total_tokens if response.usage else 0,
            } if hasattr(response, 'usage') else None
        )
    
    def _parse_tool_call(self, tool_call) -> ToolCall:
        """
        Parse a single tool_call from OpenAI response.
        
        OpenAI structure:
        {
            "id": "call_abc123",
            "type": "function",
            "function": {
                "name": "read_file",
                "arguments": "{\"path\": \"/src/main.py\"}"
            }
        }
        
        CRITICAL: arguments is a JSON STRING, not a dict!
        Must use json.loads() to parse it.
        """
        # Parse the JSON string arguments
        try:
            arguments = json.loads(tool_call.function.arguments)
        except json.JSONDecodeError as e:
            raise OpenAIToolUseError(
                f"Failed to parse function arguments: {tool_call.function.arguments}"
            ) from e
        
        return ToolCall(
            name=tool_call.function.name,
            arguments=arguments,  # Now a dict after json.loads()
            tool_id=tool_call.id  # Unique ID for this call
        )
```

### Step 3: Tool Result Return Format (OpenAI Style)

```python
    def format_tool_result_message(
        self, 
        tool_call: ToolCall, 
        result: str,
        error: Optional[str] = None
    ) -> Dict[str, str]:
        """
        Format a tool result for the next API call.
        
        OpenAI requires tool results as dedicated messages:
        - role: "tool" (not "user" like Anthropic!)
        - tool_call_id: The ID from the original call
        - content: The result string
        
        This is CRITICAL - differs from Anthropic!
        
        Args:
            tool_call: The ToolCall that was executed
            result: The result string from tool execution
            error: Optional error message if tool failed
            
        Returns:
            Message dict ready for next API call
        """
        return {
            "role": "tool",
            "tool_call_id": tool_call.tool_id,
            "content": result if not error else f"Error: {error}"
        }
    
    def format_tool_result_for_multiple(
        self,
        tool_results: List[Dict]
    ) -> List[Dict[str, str]]:
        """
        Format multiple tool results (for parallel tool calls).
        
        When GPT calls multiple tools at once, we need to return
        all results before the next LLM call.
        
        Args:
            tool_results: List of {tool_call, result, error}
            
        Returns:
            List of message dicts for the next API call
        """
        messages = []
        for tr in tool_results:
            tool_call = tr["tool_call"]
            result = tr.get("result", "")
            error = tr.get("error")
            
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.tool_id,
                "content": result if not error else f"Error: {error}"
            })
        
        return messages
```

### Step 4: Complete OpenAI Integration Example

```python
# src/coding_agent/agent_openai.py
"""
Agent with OpenAI function calling integration.
"""

from typing import List, Dict, Optional
from coding_agent.tools.registry import ToolRegistry
from coding_agent.llm.responses import LLMResponse, ToolCall


class OpenAIAgent:
    """
    Autonomous coding agent using OpenAI's function_calling format.
    
    This implementation specifically uses OpenAI's format:
    - Tools wrapped in {"type": "function", "function": {...}}
    - Parse top-level tool_calls array
    - Return results as 'tool' role messages
    """
    
    def __init__(
        self,
        llm_client,  # OpenAIClient instance
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
        Run the agent with OpenAI function calling loop.
        
        The loop:
        1. Call LLM with tools (OpenAI format)
        2. Parse response - check finish_reason for tool_calls
        3. If tool_calls: execute each tool, format results
        4. Add results to messages, repeat
        5. If stop: return text response
        """
        # Initialize conversation
        # Note: OpenAI system prompt goes in messages, not separate param
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": user_input}
        ]
        
        # Get tool schemas
        tool_schemas = self.tools.get_schemas()
        
        iteration = 0
        while iteration < self.max_iterations:
            iteration += 1
            
            # Step 1: Call OpenAI API with tools
            response = self.llm.generate(
                messages=messages,
                tools=tool_schemas if tool_schemas else None,
                system=None  # Already in messages
            )
            
            # Step 2: Check if GPT wants to use tools
            # finish_reason="tool_calls" means LLM called a function
            # finish_reason="stop" means LLM is done
            if response.stop_reason == "stop" or not response.has_tool_calls():
                # GPT is done - return text response
                return response.text or "(No response)"
            
            # Step 3: Execute tool calls
            if response.has_tool_calls():
                # Handle potentially multiple parallel tool calls
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
                    
                    # Step 4: Format result in OpenAI style
                    # Note: role="tool" (not "user" like Anthropic!)
                    tool_result_message = self.llm.format_tool_result_message(
                        tool_call=tool_call,
                        result=result
                    )
                    messages.append(tool_result_message)
                    
                    print(f"   Result: {result[:100]}...")
            
            # Loop continues - GPT decides next action
        
        return f"(Max iterations {self.max_iterations} reached)"
```

### Step 5: Unified Client for Both Providers

```python
# src/coding_agent/llm/unified_client.py
"""
Unified LLM client that supports both Anthropic and OpenAI.

This allows your agent to work with either provider seamlessly.
"""

from typing import List, Dict, Optional, Union
from enum import Enum

from coding_agent.llm.responses import LLMResponse, ToolCall


class LLMProvider(Enum):
    """Supported LLM providers."""
    ANTHROPIC = "anthropic"
    OPENAI = "openai"


class UnifiedLLMClient:
    """
    Unified client that wraps Anthropic or OpenAI.
    
    This abstracts away the format differences so your agent
    code doesn't need to know which provider is being used.
    """
    
    def __init__(
        self,
        provider: LLMProvider,
        api_key: str,
        model: str = None,
        **kwargs
    ):
        """
        Initialize the unified client.
        
        Args:
            provider: ANTHROPIC or OPENAI
            api_key: API key for the provider
            model: Model name (provider-specific default if None)
            **kwargs: Additional provider-specific options
        """
        self.provider = provider
        self._client = None
        self._model = model
        
        if provider == LLMProvider.ANTHROPIC:
            from coding_agent.llm.anthropic_client import AnthropicClient
            self._model = model or "claude-3-5-sonnet-20241022"
            self._client = AnthropicClient(api_key=api_key, model=self._model)
            
        elif provider == LLMProvider.OPENAI:
            from coding_agent.llm.openai_client import OpenAIClient
            self._model = model or "gpt-4o"
            self._client = OpenAIClient(api_key=api_key, model=self._model)
        
        self._system_prompt = kwargs.get("system_prompt", "")
    
    @property
    def provider_name(self) -> str:
        """Get provider name for display."""
        return f"{self.provider.value.title()} ({self._model})"
    
    def generate(
        self,
        messages: List[Dict[str, str]],
        tools: Optional[List[Dict]] = None,
        system: Optional[str] = None,
        temperature: Optional[float] = None
    ) -> LLMResponse:
        """
        Generate a response using the appropriate provider.
        
        This method is the same regardless of provider - the client
        handles format conversion internally.
        """
        # Use system prompt from init if not provided
        system = system or self._system_prompt
        
        return self._client.generate(
            messages=messages,
            tools=tools,
            system=system,
            temperature=temperature
        )
    
    def format_tool_result_message(
        self,
        tool_call: ToolCall,
        result: str,
        error: Optional[str] = None
    ) -> Dict[str, str]:
        """
        Format tool result - handles provider differences.
        """
        return self._client.format_tool_result_message(
            tool_call=tool_call,
            result=result,
            error=error
        )


def create_llm_client(
    provider: str = "anthropic",
    api_key: str = None,
    model: str = None,
    **kwargs
) -> UnifiedLLMClient:
    """
    Factory function to create a unified LLM client.
    
    Args:
        provider: "anthropic" or "openai"
        api_key: API key (reads from env if not provided)
        model: Optional model override
        **kwargs: Additional options
        
    Returns:
        UnifiedLLMClient instance
        
    Example:
        # Use Anthropic
        client = create_llm_client("anthropic", api_key=os.getenv("ANTHROPIC_API_KEY"))
        
        # Use OpenAI
        client = create_llm_client("openai", api_key=os.getenv("OPENAI_API_KEY"))
    """
    import os
    
    # Get API key from environment if not provided
    if not api_key:
        if provider.lower() == "anthropic":
            api_key = os.getenv("ANTHROPIC_API_KEY")
        elif provider.lower() == "openai":
            api_key = os.getenv("OPENAI_API_KEY")
    
    if not api_key:
        raise ValueError(f"API key required for {provider}")
    
    # Convert provider string to enum
    provider_enum = LLMProvider.ANTHROPIC if provider.lower() == "anthropic" else LLMProvider.OPENAI
    
    return UnifiedLLMClient(
        provider=provider_enum,
        api_key=api_key,
        model=model,
        **kwargs
    )
```

---

## 🔍 Deep Dive: The OpenAI Format Differences

### Why This Matters

Many implementations fail because they mix up the formats. Here's exactly what's different:

```python
# ❌ WRONG - Anthropic style for OpenAI
# Anthropic uses: role="user", content=result
messages.append({
    "role": "user", 
    "content": f"Tool '{tool_name}' returned:\n{result}"
})

# ✅ CORRECT - OpenAI style
# OpenAI uses: role="tool", tool_call_id=..., content=result
messages.append({
    "role": "tool", 
    "tool_call_id": "call_abc123",
    "content": result
})
```

### Another Key Difference: Arguments Format

```python
# ❌ WRONG - Treating arguments as dict (Anthropic style)
arguments = block["input"]  # Won't work for OpenAI!

# ✅ CORRECT - OpenAI gives you a JSON STRING!
arguments = json.loads(block["function"]["arguments"])  # Must parse!
```

### Tool Schema Format

```python
# ❌ WRONG - Anthropic format for OpenAI
tools = [
    {"name": "read_file", "description": "...", "input_schema": {...}}
]

# ✅ CORRECT - OpenAI format wraps in type:function
tools = [
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "...",
            "parameters": {...}
        }
    }
]
```

### Stop Reason Handling

```python
# OpenAI uses different finish_reasons
response.choices[0].finish_reason values:
- "stop" → GPT finished generating normally
- "length" → Hit token limit, response truncated  
- "tool_calls" → GPT made function calls (key one!)
- "content_filter" → Content filtered

# vs Anthropic
# Anthropic uses: stop_reason values
# - "end_turn" → Claude finished
# - "tool_use" → Claude requested tool execution
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
You: Read the config.py file and summarize its purpose

🔧 Executing: read_file
   Arguments: {'path': 'src/config.py'}
   Result: """Configuration management for coding agent..."""

Agent: The config.py file handles configuration management:

1. **Purpose**: Loads settings from environment variables and .env files
2. **Key classes**:
   - LLMConfig: Provider settings (API keys, models, temperature)
   - ToolConfig: Tool settings (allowed directories, timeouts)
   - AgentConfig: Main configuration aggregator
3. **Features**:
   - Environment-based configuration
   - Validation on load
   - Singleton pattern for global access

The configuration system follows SOLID principles with clear separation of concerns.
```

---

## ✅ Exercise

1. **Run the OpenAI Agent:**
   ```bash
   export OPENAI_API_KEY=your-key
   python scripts/run_agent_openai.py
   ```

2. **Test Function Calls:**
   - Ask: "List files in the current directory"
   - Ask: "Read the README.md file"
   - Ask: "What's in the src folder?"

3. **Compare Providers:**
   - Run same queries with both Anthropic and OpenAI
   - Note differences in response style

4. **Test the Unified Client:**
   - Use `create_llm_client("anthropic")` and `create_llm_client("openai")`
   - Verify same agent code works with both

---

## 🔗 Integration with Previous Tutorials

This tutorial builds on:
- **T13** (Day 1 Capstone): Base architecture, ToolRegistry, DI
- **T25** (Tool Use Loop): General tool use concept
- **T26** (JSON Schema): Tool schema definitions
- **T27** (Anthropic format): Anthropic's specific format

### What We Use from T13:
- `ToolRegistry` class with `get_schemas()` and `execute()`
- Agent structure with dependency injection
- Error handling patterns

### What We Use from T25-27:
- `ToolCall` and `LLMResponse` data classes
- JSON Schema format for tools
- The tool use loop concept
- Anthropic-specific format (for contrast)

---

## 🎯 Next Up

**Tutorial 29:** Parsing Tool Calls from LLM Responses

We'll cover:
- Extracting tool calls from different response formats
- Error handling for malformed responses
- Validation of tool names and arguments

---

## 📚 Resources

- [OpenAI Function Calling Documentation](https://platform.openai.com/docs/guides/function-calling)
- [OpenAI API Reference](https://platform.openai.com/docs/api-reference)
- [Function Calling Tutorial](https://cookbook.openai.com/examples/how_to_call_functions_with_chat_models)

---

*"OpenAI's function_calling is powerful but has subtle differences from Anthropic. The key: tool role messages and JSON string arguments."*