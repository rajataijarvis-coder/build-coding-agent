# Day 3 Capstone: Complete Tool Use System - Hands-On

**Course:** Build Your Own Coding Agent  
**Day:** 3 - Tool Use Loop  
**Tutorial:** 36 of 60  
**Estimated Time:** 90 minutes

---

## 🎉 Congratulations on Completing Day 3!

You've built the complete tool use system that allows your agent to autonomously decide when and how to use tools. Let's consolidate everything into a working system.

---

## 📚 Day 3 Concepts Summary

| Tutorial | Concept | Implementation |
|----------|---------|----------------|
| **T25** | Tool use concept | LLM outputs JSON function calls |
| **T26** | JSON Schema | Tool definitions for LLM |
| **T27** | Anthropic format | Claude tool_use API |
| **T28** | OpenAI format | function_call API |
| **T29** | Parsing tool calls | Extract from LLM responses |
| **T30** | Execution loop | Call → Execute → Return result |
| **T31** | Error handling | Graceful failures in tool loop |
| **T32** | ReAct pattern | Thought → Action → Observation |
| **T33** | Multi-step tasks | Planning before execution |
| **T34** | Token tracking | Cost awareness |
| **T35** | Persistence | Session save/load |

---

## 🏗️ Integration Architecture

Here's how Day 3 Tool Use integrates with Days 1-2:

```mermaid
flowchart TB
    subgraph "User Interaction"
        U[User Input]
    end
    
    subgraph "Day 1 - Core (T13)"
        A[Agent]
        LLM[LLMClient]
        TR[ToolRegistry]
        CM[ContextManager]
    end
    
    subgraph "Day 2 - File Operations (T24)"
        FV[File Tools]
        SV[Search Tools]
    end
    
    subgraph "Day 3 - Tool Use Loop (T36)"
        TD[Tool Definitions]
        PC[Parse Tool Calls]
        TE[Tool Executor]
        RA[ReAct Loop]
        TT[Token Tracker]
        PS[Persistence]
    end
    
    U --> A
    A --> LLM
    LLM -->|tool_calls| PC
    PC --> TE
    TE --> TR
    TR --> FV
    TR --> SV
    TE -->|result| A
    A --> CM
    CM --> TT
    CM --> PS
    
    style A fill:#e3f2fd,stroke:#1565c0
    style TE fill:#c8e6c9,stroke:#2e7d32
    style RA fill:#fff3e0,stroke:#e65100
```

---

## 💾 Complete Working Code

Below is the consolidated code for Day 3 Tool Use System, integrating with Days 1-2.

---

### `src/coding_agent/tool_use/modern.py`

```python
"""
T29-T30: Tool Call Parser and Executor

This module handles:
- Parsing tool calls from LLM responses (T29)
- Executing tools and returning results (T30)
- Error handling and recovery (T31)
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Callable
import logging
import json
import time

from coding_agent.tools.base import BaseTool, ToolResult
from coding_agent.tools.registry import ToolRegistry
from coding_agent.exceptions import ToolError, ToolNotFoundError

logger = logging.getLogger(__name__)


@dataclass
class ToolCall:
    """Represents a single tool call from the LLM."""
    
    id: str  # Unique ID for this tool call
    name: str  # Tool name
    arguments: Dict[str, Any] = field(default_factory=dict)  # Tool arguments
    
    # Execution metadata
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    status: str = "pending"  # pending, executing, success, error
    result: Optional[str] = None
    error: Optional[str] = None
    
    @property
    def execution_time_ms(self) -> float:
        """Calculate execution time in milliseconds."""
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at) * 1000
        return 0.0


@dataclass
class ToolCallResult:
    """Result of executing a tool call."""
    
    tool_call_id: str
    tool_name: str
    success: bool
    output: str
    error: Optional[str] = None
    execution_time_ms: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


class ToolCallParser:
    """
    Parse tool calls from various LLM response formats.
    
    Supports:
    - Anthropic tool_use format (T27)
    - OpenAI function_call format (T28)
    - Generic JSON format
    
    Usage:
        parser = ToolCallParser()
        tool_calls = parser.parse(response, format="anthropic")
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def parse(
        self,
        response: Any,
        format: str = "anthropic"
    ) -> List[ToolCall]:
        """
        Parse tool calls from LLM response.
        
        Args:
            response: Raw LLM response
            format: Response format ("anthropic", "openai", "json")
            
        Returns:
            List of ToolCall objects
        """
        if format == "anthropic":
            return self._parse_anthropic(response)
        elif format == "openai":
            return self._parse_openai(response)
        elif format == "json":
            return self._parse_json(response)
        else:
            self.logger.warning(f"Unknown format: {format}, returning empty list")
            return []
    
    def _parse_anthropic(self, response: Any) -> List[ToolCall]:
        """Parse Anthropic tool_use format."""
        tool_calls = []
        
        # Handle response with tool_use
        if hasattr(response, 'tool_calls') and response.tool_calls:
            for tc in response.tool_calls:
                tool_call = ToolCall(
                    id=tc.get("id", f"call_{len(tool_calls)}"),
                    name=tc.get("function", {}).get("name", ""),
                    arguments=json.loads(tc.get("function", {}).get("arguments", "{}"))
                )
                tool_calls.append(tool_call)
        
        # Handle raw content blocks
        elif hasattr(response, 'content'):
            for block in response.content:
                if hasattr(block, 'type') and block.type == "tool_use":
                    tool_call = ToolCall(
                        id=block.id,
                        name=block.name,
                        arguments=block.input
                    )
                    tool_calls.append(tool_call)
        
        return tool_calls
    
    def _parse_openai(self, response: Any) -> List[ToolCall]:
        """Parse OpenAI function_call format."""
        tool_calls = []
        
        # Handle response with tool_calls
        if hasattr(response, 'tool_calls') and response.tool_calls:
            for tc in response.tool_calls:
                func = tc.get("function", {})
                tool_call = ToolCall(
                    id=tc.get("id", f"call_{len(tool_calls)}"),
                    name=func.get("name", ""),
                    arguments=json.loads(func.get("arguments", "{}"))
                )
                tool_calls.append(tool_call)
        
        return tool_calls
    
    def _parse_json(self, response: Any) -> List[ToolCall]:
        """Parse generic JSON format."""
        tool_calls = []
        
        # Try to extract from content
        content = ""
        if hasattr(response, 'content'):
            content = response.content
        elif isinstance(response, dict):
            content = response.get("content", "")
        
        # Try to find JSON array of tool calls
        try:
            # Look for tool_calls in the response
            if isinstance(response, dict):
                tool_calls_data = response.get("tool_calls", [])
                for tc in tool_calls_data:
                    tool_call = ToolCall(
                        id=tc.get("id", f"call_{len(tool_calls)}"),
                        name=tc.get("name", ""),
                        arguments=tc.get("arguments", {})
                    )
                    tool_calls.append(tool_call)
        except Exception as e:
            self.logger.debug(f"Failed to parse JSON format: {e}")
        
        return tool_calls


class ToolExecutor:
    """
    Execute tools and handle the execution loop.
    
    This is the core of T30 - the tool execution loop:
    1. Receive tool call
    2. Validate tool exists
    3. Execute tool
    4. Handle errors
    5. Return result
    
    Usage:
        executor = ToolExecutor(registry)
        result = executor.execute(tool_call)
    """
    
    def __init__(
        self,
        registry: ToolRegistry,
        error_handler: Optional[Callable] = None
    ):
        """
        Initialize the executor.
        
        Args:
            registry: ToolRegistry with registered tools
            error_handler: Optional custom error handler
        """
        self.registry = registry
        self.error_handler = error_handler or self._default_error_handler
        self.logger = logging.getLogger(__name__)
        
        # Execution statistics
        self._execution_count = 0
        self._error_count = 0
    
    def execute(
        self,
        tool_call: ToolCall,
        context: Optional[Dict[str, Any]] = None
    ) -> ToolCallResult:
        """
        Execute a single tool call.
        
        Args:
            tool_call: ToolCall to execute
            context: Optional execution context
            
        Returns:
            ToolCallResult with execution results
        """
        self._execution_count += 1
        start_time = time.time()
        
        # Mark as executing
        tool_call.status = "executing"
        tool_call.started_at = start_time
        
        self.logger.info(f"Executing tool: {tool_call.name} (id: {tool_call.id})")
        
        try:
            # Get the tool from registry
            try:
                tool = self.registry.get(tool_call.name)
            except ToolNotFoundError as e:
                raise ToolError(f"Tool not found: {tool_call.name}") from e
            
            # Validate input (T31: error handling)
            try:
                tool.validate_input(tool_call.arguments)
            except ValueError as e:
                raise ToolError(f"Invalid input for {tool_call.name}: {e}") from e
            
            # Execute the tool
            result = tool.execute(**tool_call.arguments)
            
            # Convert tool result to our format
            tool_call.status = "success"
            tool_call.completed_at = time.time()
            tool_call.result = result.output if hasattr(result, 'output') else str(result)
            
            execution_time = (tool_call.completed_at - start_time) * 1000
            
            self.logger.info(
                f"Tool {tool_call.name} executed successfully "
                f"in {execution_time:.2f}ms"
            )
            
            return ToolCallResult(
                tool_call_id=tool_call.id,
                tool_name=tool_call.name,
                success=True,
                output=tool_call.result,
                execution_time_ms=execution_time,
                metadata={
                    "tool_name": tool.name,
                    "description": tool.description
                }
            )
        
        except Exception as e:
            self._error_count += 1
            tool_call.status = "error"
            tool_call.completed_at = time.time()
            tool_call.error = str(e)
            
            execution_time = (tool_call.completed_at - start_time) * 1000
            
            self.logger.error(f"Tool execution failed: {tool_call.name} - {e}")
            
            # Apply error handler
            error_output = self.error_handler(e, tool_call)
            
            return ToolCallResult(
                tool_call_id=tool_call.id,
                tool_name=tool_call.name,
                success=False,
                output="",
                error=str(e),
                execution_time_ms=execution_time,
                metadata={"error_handled": True}
            )
    
    def execute_batch(
        self,
        tool_calls: List[ToolCall],
        context: Optional[Dict[str, Any]] = None
    ) -> List[ToolCallResult]:
        """
        Execute multiple tool calls in sequence.
        
        Args:
            tool_calls: List of tool calls to execute
            context: Optional execution context
            
        Returns:
            List of ToolCallResult objects
        """
        results = []
        
        for tool_call in tool_calls:
            result = self.execute(tool_call, context)
            results.append(result)
            
            # Stop on error if configured
            if not result.success and context and context.get("stop_on_error"):
                self.logger.warning("Stopping batch execution due to error")
                break
        
        return results
    
    def _default_error_handler(
        self,
        error: Exception,
        tool_call: ToolCall
    ) -> str:
        """
        Default error handler - generates user-friendly error message.
        
        Args:
            error: The exception that occurred
            tool_call: The tool call that failed
            
        Returns:
            Error message string
        """
        error_type = type(error).__name__
        
        if isinstance(error, ToolNotFoundError):
            return f"Error: Tool '{tool_call.name}' not found. Available tools: {', '.join(self.registry.list_tools())}"
        elif isinstance(error, ToolError):
            return f"Error executing {tool_call.name}: {error}"
        else:
            return f"Unexpected error in {tool_call.name}: {error_type} - {error}"
    
    def get_stats(self) -> Dict[str, Any]:
        """Get execution statistics."""
        return {
            "total_executions": self._execution_count,
            "total_errors": self._error_count,
            "success_rate": (
                (self._execution_count - self._error_count) / self._execution_count
                if self._execution_count > 0 else 0
            )
        }
```

---

### `src/coding_agent/tool_use/react.py`

```python
"""
T32: ReAct Pattern Implementation

ReAct = Reasoning + Acting
- Thought: The LLM thinks about what to do
- Action: The LLM executes a tool
- Observation: The LLM sees the result and continues thinking

This creates a loop that allows multi-step reasoning.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Callable
from enum import Enum
import logging

from coding_agent.tool_use.modern import ToolCallParser, ToolExecutor, ToolCall, ToolCallResult

logger = logging.getLogger(__name__)


class ReActStepType(Enum):
    """Types of steps in ReAct loop."""
    THOUGHT = "thought"
    ACTION = "action"
    OBSERVATION = "observation"
    FINAL = "final"


@dataclass
class ReActStep:
    """A single step in the ReAct reasoning process."""
    
    step_type: ReActStepType
    content: str
    tool_call: Optional[ToolCall] = None
    tool_result: Optional[ToolCallResult] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        result = {
            "step_type": self.step_type.value,
            "content": self.content
        }
        
        if self.tool_call:
            result["tool_name"] = self.tool_call.name
            result["tool_arguments"] = self.tool_call.arguments
        
        if self.tool_result:
            result["tool_result"] = self.tool_result.output
            result["tool_success"] = self.tool_result.success
        
        return result


@dataclass
class ReActResult:
    """Result of a complete ReAct reasoning process."""
    
    final_answer: str
    steps: List[ReActStep] = field(default_factory=list)
    tool_calls: List[ToolCall] = field(default_factory=list)
    total_thoughts: int = 0
    total_actions: int = 0
    total_observations: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "final_answer": self.final_answer,
            "steps": [s.to_dict() for s in self.steps],
            "total_thoughts": self.total_thoughts,
            "total_actions": self.total_actions,
            "total_observations": self.total_observations,
            "tool_call_count": len(self.tool_calls)
        }


class ReActAgent:
    """
    Implements the ReAct (Reasoning + Acting) pattern.
    
    This is T32 - the ReAct pattern that allows the agent to:
    1. Think about the problem
    2. Decide on an action (tool call)
    3. Execute the action
    4. Observe the result
    5. Repeat until satisfied
    
    Usage:
        react = ReActAgent(llm_client, tool_executor, max_iterations=10)
        result = react.run("Read the main.py file and count lines")
    """
    
    def __init__(
        self,
        llm_client: Any,
        tool_executor: ToolExecutor,
        max_iterations: int = 10,
        max_tokens_per_iteration: int = 1024,
    ):
        """
        Initialize the ReAct agent.
        
        Args:
            llm_client: LLM client for generating responses
            tool_executor: Tool executor for running tools
            max_iterations: Maximum ReAct loops before giving up
            max_tokens: Max tokens for each LLM call
        """
        self.llm_client = llm_client
        self.tool_executor = tool_executor
        self.max_iterations = max_iterations
        self.max_tokens = max_tokens_per_iteration
        
        self.parser = ToolCallParser()
        self.logger = logging.getLogger(__name__)
        
        # State
        self._iteration = 0
        self._steps: List[ReActStep] = []
    
    def run(
        self,
        user_input: str,
        system_prompt: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> ReActResult:
        """
        Run the ReAct loop on user input.
        
        Args:
            user_input: The user's request
            system_prompt: Optional system prompt
            context: Optional execution context
            
        Returns:
            ReActResult with the final answer and reasoning steps
        """
        self._iteration = 0
        self._steps = []
        
        # Build the initial prompt
        messages = self._build_messages(user_input, system_prompt)
        
        # ReAct loop
        while self._iteration < self.max_iterations:
            self._iteration += 1
            self.logger.debug(f"ReAct iteration {self._iteration}/{self.max_iterations}")
            
            # Call LLM
            response = self.llm_client.complete(
                messages=messages,
                max_tokens=self.max_tokens
            )
            
            # Check for tool calls
            tool_calls = self.parser.parse(response)
            
            if not tool_calls:
                # No tool calls - this is the final answer
                final_answer = response.content if hasattr(response, 'content') else str(response)
                
                # Add final thought
                self._steps.append(ReActStep(
                    step_type=ReActStepType.FINAL,
                    content=final_answer
                ))
                
                break
            
            # Execute each tool call
            for tool_call in tool_calls:
                # Add thought step
                self._steps.append(ReActStep(
                    step_type=ReActStepType.THOUGHT,
                    content=f"I need to use {tool_call.name} with arguments: {tool_call.arguments}"
                ))
                
                # Add action step
                self._steps.append(ReActStep(
                    step_type=ReActStepType.ACTION,
                    content=f"Executing {tool_call.name}...",
                    tool_call=tool_call
                ))
                
                # Execute the tool
                result = self.tool_executor.execute(tool_call, context)
                
                # Add observation step
                self._steps.append(ReActStep(
                    step_type=ReActStepType.OBSERVATION,
                    content=result.output if result.success else f"Error: {result.error}",
                    tool_result=result
                ))
                
                # Add tool result to messages
                messages.append({
                    "role": "user",
                    "content": f"Tool result for {tool_call.name}: {result.output}"
                })
        
        # Build final result
        final_step = self._steps[-1] if self._steps else None
        final_answer = final_step.content if final_step else "No response generated"
        
        result = ReActResult(
            final_answer=final_answer,
            steps=self._steps,
            tool_calls=[s.tool_call for s in self._steps if s.tool_call],
            total_thoughts=sum(1 for s in self._steps if s.step_type == ReActStepType.THOUGHT),
            total_actions=sum(1 for s in self._steps if s.step_type == ReActStepType.ACTION),
            total_observations=sum(1 for s in self._steps if s.step_type == ReActStepType.OBSERVATION)
        )
        
        self.logger.info(
            f"ReAct completed: {result.total_thoughts} thoughts, "
            f"{result.total_actions} actions, {result.total_observations} observations"
        )
        
        return result
    
    def _build_messages(
        self,
        user_input: str,
        system_prompt: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Build the message list for LLM."""
        messages = []
        
        if system_prompt:
            messages.append({
                "role": "system",
                "content": system_prompt
            })
        
        messages.append({
            "role": "user",
            "content": user_input
        })
        
        return messages
    
    def get_reasoning_trace(self) -> List[Dict[str, Any]]:
        """Get the reasoning trace for display."""
        return [s.to_dict() for s in self._steps]
```

---

### `src/coding_agent/tool_use/planner.py`

```python
"""
T33: Multi-Step Task Planning

Before executing tools, the agent creates a plan.
This module handles planning and plan execution.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Callable
from enum import Enum
import logging
import json

logger = logging.getLogger(__name__)


class PlanStepStatus(Enum):
    """Status of a plan step."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class PlanStep:
    """A single step in a plan."""
    
    step_id: str
    description: str
    tool_name: str
    arguments: Dict[str, Any] = field(default_factory=dict)
    depends_on: List[str] = field(default_factory=list)
    status: PlanStepStatus = PlanStepStatus.PENDING
    result: Optional[str] = None
    error: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "step_id": self.step_id,
            "description": self.description,
            "tool_name": self.tool_name,
            "arguments": self.arguments,
            "depends_on": self.depends_on,
            "status": self.status.value,
            "result": self.result,
            "error": self.error
        }


@dataclass
class Plan:
    """A plan consisting of multiple steps."""
    
    goal: str  # The overall goal
    steps: List[PlanStep] = field(default_factory=list)
    created_at: str = ""  # ISO timestamp
    
    def get_next_step(self) -> Optional[PlanStep]:
        """Get the next step that can be executed."""
        for step in self.steps:
            if step.status != PlanStepStatus.PENDING:
                continue
            
            # Check dependencies
            deps_met = all(
                self._get_step(sid).status == PlanStepStatus.COMPLETED
                for sid in step.depends_on
                if self._get_step(sid)
            )
            
            if deps_met:
                return step
        
        return None
    
    def _get_step(self, step_id: str) -> Optional[PlanStep]:
        """Get step by ID."""
        for step in self.steps:
            if step.step_id == step_id:
                return step
        return None
    
    def is_complete(self) -> bool:
        """Check if all steps are complete."""
        return all(
            step.status in (PlanStepStatus.COMPLETED, PlanStepStatus.SKIPPED)
            for step in self.steps
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "goal": self.goal,
            "steps": [s.to_dict() for s in self.steps],
            "created_at": self.created_at,
            "completed": self.is_complete()
        }


class TaskPlanner:
    """
    Creates and executes plans for multi-step tasks.
    
    This is T33 - planning before execution.
    
    Usage:
        planner = TaskPlanner(llm_client)
        plan = planner.create_plan("Read all Python files and count lines")
        
        # Execute plan
        for step in plan.steps:
            result = executor.execute(step)
    """
    
    def __init__(self, llm_client: Any):
        """
        Initialize the planner.
        
        Args:
            llm_client: LLM client for generating plans
        """
        self.llm_client = llm_client
        self.logger = logging.getLogger(__name__)
    
    def create_plan(
        self,
        task: str,
        available_tools: List[Dict[str, Any]],
        context: Optional[Dict[str, Any]] = None
    ) -> Plan:
        """
        Create a plan for the given task.
        
        Args:
            task: The task to plan for
            available_tools: List of available tool definitions
            context: Optional context information
            
        Returns:
            Plan object with steps
        """
        self.logger.info(f"Creating plan for: {task}")
        
        # Build the planning prompt
        prompt = self._build_planning_prompt(task, available_tools, context)
        
        # Call LLM
        response = self.llm_client.complete(
            messages=[{"role": "user", "content": prompt}],
            max_tokens=2048
        )
        
        # Parse the response
        plan = self._parse_plan_response(task, response)
        
        self.logger.info(f"Created plan with {len(plan.steps)} steps")
        
        return plan
    
    def _build_planning_prompt(
        self,
        task: str,
        available_tools: List[Dict[str, Any]],
        context: Optional[Dict[str, Any]]
    ) -> str:
        """Build the prompt for planning."""
        tools_description = "\n".join([
            f"- {t['name']}: {t['description']}"
            for t in available_tools
        ])
        
        context_str = ""
        if context:
            context_str = f"\n\nContext:\n{json.dumps(context, indent=2)}"
        
        return f"""You are a planning agent. Break down the user's task into a sequence of tool calls.

Available tools:
{tools_description}

User task: {task}
{context_str}

Create a plan as a JSON array of steps. Each step should have:
- step_id: unique identifier (e.g., "step1", "step2")
- description: what this step does
- tool_name: which tool to use
- arguments: tool arguments as JSON
- depends_on: array of step_ids this depends on (empty if no dependencies)

Respond ONLY with the JSON plan, no other text. Format:
```json
[
  {{"step_id": "step1", "description": "...", "tool_name": "...", "arguments": {{}}, "depends_on": []}},
  ...
]
```"""
    
    def _parse_plan_response(self, task: str, response: Any) -> Plan:
        """Parse the LLM response into a Plan."""
        content = response.content if hasattr(response, 'content') else str(response)
        
        # Extract JSON from response
        try:
            # Try to find JSON in code blocks
            if "```json" in content:
                json_str = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                json_str = content.split("```")[1].split("```")[0]
            else:
                json_str = content
            
            # Parse JSON
            steps_data = json.loads(json_str.strip())
            
            plan = Plan(goal=task)
            
            for step_data in steps_data:
                step = PlanStep(
                    step_id=step_data["step_id"],
                    description=step_data["description"],
                    tool_name=step_data["tool_name"],
                    arguments=step_data.get("arguments", {}),
                    depends_on=step_data.get("depends_on", [])
                )
                plan.steps.append(step)
            
            return plan
        
        except Exception as e:
            self.logger.error(f"Failed to parse plan: {e}")
            # Return a simple single-step plan as fallback
            return Plan(
                goal=task,
                steps=[
                    PlanStep(
                        step_id="step1",
                        description=task,
                        tool_name="unknown",
                        arguments={}
                    )
                ]
            )
    
    def execute_plan(
        self,
        plan: Plan,
        executor: Any,
        context: Optional[Dict[str, Any]] = None
    ) -> Plan:
        """
        Execute a plan using the tool executor.
        
        Args:
            plan: Plan to execute
            executor: Tool executor
            context: Optional context
            
        Returns:
            Updated Plan with results
        """
        self.logger.info(f"Executing plan: {plan.goal}")
        
        while not plan.is_complete():
            # Get next step
            step = plan.get_next_step()
            
            if not step:
                self.logger.warning("No executable steps found, plan may have failed")
                break
            
            # Execute step
            step.status = PlanStepStatus.IN_PROGRESS
            
            try:
                from coding_agent.tool_use.modern import ToolCall
                tool_call = ToolCall(
                    id=step.step_id,
                    name=step.tool_name,
                    arguments=step.arguments
                )
                
                result = executor.execute(tool_call, context)
                
                if result.success:
                    step.status = PlanStepStatus.COMPLETED
                    step.result = result.output
                else:
                    step.status = PlanStepStatus.FAILED
                    step.error = result.error
            
            except Exception as e:
                step.status = PlanStepStatus.FAILED
                step.error = str(e)
                self.logger.error(f"Step {step.step_id} failed: {e}")
        
        self.logger.info(f"Plan execution complete: {plan.is_complete()}")
        
        return plan
```

---

### `src/coding_agent/tool_use/token_tracker.py`

```python
"""
T34: Token Tracking and Cost Awareness

Track token usage and estimate costs for budget management.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


# Token pricing (as of 2024 - update as needed)
TOKEN_PRICING = {
    "claude-3-5-sonnet-20241022": {
        "input": 0.003,  # $0.003 per 1K input tokens
        "output": 0.015,  # $0.015 per 1K output tokens
    },
    "claude-3-opus-20240229": {
        "input": 0.015,
        "output": 0.075,
    },
    "gpt-4o": {
        "input": 0.0025,
        "output": 0.01,
    },
    "gpt-4": {
        "input": 0.03,
        "output": 0.06,
    },
    "llama3.2": {
        "input": 0.0,  # Free for local
        "output": 0.0,
    }
}


@dataclass
class TokenUsage:
    """Token usage for a single request."""
    
    model: str
    input_tokens: int
    output_tokens: int
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    @property
    def total_tokens(self) -> int:
        return self.input_tokens + self.output_tokens
    
    def cost(self) -> float:
        """Calculate cost in dollars."""
        pricing = TOKEN_PRICING.get(self.model, {"input": 0, "output": 0})
        input_cost = (self.input_tokens / 1000) * pricing["input"]
        output_cost = (self.output_tokens / 1000) * pricing["output"]
        return input_cost + output_cost


@dataclass
class TokenTracker:
    """
    Track token usage and costs across all LLM calls.
    
    This is T34 - token tracking for cost awareness.
    
    Usage:
        tracker = TokenTracker("claude-3-5-sonnet-20241022")
        
        # After each LLM call
        tracker.add_usage(1000, 500)
        
        # Check budget
        if tracker.exceeds_budget(10.0):  # $10 limit
            print("Warning: Approaching budget limit!")
    """
    
    def __init__(
        self,
        model: str = "claude-3-5-sonnet-20241022",
        budget_limit: Optional[float] = None
    ):
        """
        Initialize the token tracker.
        
        Args:
            model: Model being used
            budget_limit: Optional budget limit in dollars
        """
        self.model = model
        self.budget_limit = budget_limit
        self._usage_history: List[TokenUsage] = []
        self.logger = logging.getLogger(__name__)
    
    def add_usage(
        self,
        input_tokens: int,
        output_tokens: int,
        model: Optional[str] = None
    ) -> TokenUsage:
        """
        Add a token usage record.
        
        Args:
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            model: Optional model override
            
        Returns:
            TokenUsage object
        """
        usage = TokenUsage(
            model=model or self.model,
            input_tokens=input_tokens,
            output_tokens=output_tokens
        )
        
        self._usage_history.append(usage)
        
        self.logger.debug(
            f"Added usage: {usage.total_tokens} tokens, "
            f"${usage.cost():.4f}"
        )
        
        # Check budget
        if self.budget_limit:
            total_cost = self.total_cost()
            if total_cost > self.budget_limit:
                self.logger.warning(
                    f"Budget exceeded: ${total_cost:.2f} > ${self.budget_limit:.2f}"
                )
        
        return usage
    
    def total_input_tokens(self) -> int:
        """Get total input tokens used."""
        return sum(u.input_tokens for u in self._usage_history)
    
    def total_output_tokens(self) -> int:
        """Get total output tokens used."""
        return sum(u.output_tokens for u in self._usage_history)
    
    def total_tokens(self) -> int:
        """Get total tokens used."""
        return sum(u.total_tokens for u in self._usage_history)
    
    def total_cost(self) -> float:
        """Get total cost in dollars."""
        return sum(u.cost() for u in self._usage_history)
    
    def request_count(self) -> int:
        """Get total number of requests."""
        return len(self._usage_history)
    
    def exceeds_budget(self, limit: float) -> bool:
        """Check if current usage exceeds the given limit."""
        return self.total_cost() > limit
    
    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of token usage."""
        return {
            "model": self.model,
            "total_input_tokens": self.total_input_tokens(),
            "total_output_tokens": self.total_output_tokens(),
            "total_tokens": self.total_tokens(),
            "total_cost": self.total_cost(),
            "request_count": self.request_count(),
            "budget_limit": self.budget_limit,
            "budget_remaining": (
                self.budget_limit - self.total_cost()
                if self.budget_limit else None
            )
        }
    
    def reset(self) -> None:
        """Reset all tracking."""
        self._usage_history.clear()
        self.logger.info("Token tracker reset")
```

---

### `src/coding_agent/tool_use/loop.py`

```python
"""
T36: Complete Tool Use Loop Integration

This is the main integration module that brings together:
- Tool call parsing (T29)
- Tool execution (T30)
- Error handling (T31)
- ReAct reasoning (T32)
- Planning (T33)
- Token tracking (T34)
- Session persistence (T35)
"""

from typing import List, Dict, Any, Optional, Callable
import logging

from coding_agent.llm.client import LLMClient, Message
from coding_agent.tools.registry import ToolRegistry
from coding_agent.tool_use.modern import ToolCallParser, ToolExecutor, ToolCall
from coding_agent.tool_use.react import ReActAgent, ReActResult
from coding_agent.tool_use.planner import TaskPlanner, Plan
from coding_agent.tool_use.token_tracker import TokenTracker

logger = logging.getLogger(__name__)


class ToolUseLoop:
    """
    Complete tool use loop that integrates all Day 3 concepts.
    
    This is T36 - the capstone that brings everything together.
    
    The loop:
    1. Receive user input
    2. Optionally create a plan (if complex task)
    3. Execute ReAct loop (think → act → observe)
    4. Track tokens and costs
    5. Save session state
    
    Usage:
        loop = ToolUseLoop(
            llm_client=llm_client,
            tool_registry=registry,
            session_manager=session_manager
        )
        
        response = loop.run("Read main.py and count lines")
    """
    
    def __init__(
        self,
        llm_client: LLMClient,
        tool_registry: ToolRegistry,
        session_manager: Optional[Any] = None,
        use_planning: bool = True,
        use_react: bool = True,
        max_iterations: int = 10,
        budget_limit: Optional[float] = None,
    ):
        """
        Initialize the complete tool use loop.
        
        Args:
            llm_client: LLM client for generating responses
            tool_registry: Registry with available tools
            session_manager: Optional session manager for persistence
            use_planning: Whether to use planning for complex tasks
            use_react: Whether to use ReAct reasoning
            max_iterations: Maximum iterations in the loop
            budget_limit: Optional budget limit in dollars
        """
        self.llm_client = llm_client
        self.tool_registry = tool_registry
        self.session_manager = session_manager
        self.use_planning = use_planning
        self.use_react = use_react
        self.max_iterations = max_iterations
        
        # Initialize components
        self.parser = ToolCallParser(tool_registry)
        self.executor = ToolExecutor(tool_registry)
        self.planner = TaskPlanner(llm_client)
        self.token_tracker = TokenTracker(
            model=llm_client.model,
            budget_limit=budget_limit
        )
        
        # ReAct agent
        if use_react:
            self.react_agent = ReActAgent(
                llm_client=llm_client,
                tool_executor=self.executor,
                max_iterations=max_iterations
            )
        
        self.logger = logging.getLogger(__name__)
        
        # State
        self._messages: List[Dict[str, Any]] = []
        self._tool_call_history: List[Dict[str, Any]] = []
    
    def run(
        self,
        user_input: str,
        system_prompt: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Run the complete tool use loop.
        
        Args:
            user_input: User's request
            system_prompt: Optional system prompt
            context: Optional execution context
            
        Returns:
            Final response string
        """
        self.logger.info(f"ToolUseLoop processing: {user_input[:50]}...")
        
        # Add user message
        self._add_message("user", user_input)
        
        # Determine if we need planning
        if self.use_planning and self._is_complex_task(user_input):
            return self._run_with_planning(user_input, system_prompt, context)
        elif self.use_react:
            return self._run_react(user_input, system_prompt, context)
        else:
            return self._run_simple(user_input, system_prompt, context)
    
    def _is_complex_task(self, user_input: str) -> bool:
        """Determine if task needs planning."""
        complex_indicators = [
            "and then", "after that", "first", "finally",
            "multiple", "several files", "all files",
            "read all", "analyze", "compare"
        ]
        
        input_lower = user_input.lower()
        return any(indicator in input_lower for indicator in complex_indicators)
    
    def _run_with_planning(
        self,
        user_input: str,
        system_prompt: Optional[str],
        context: Optional[Dict[str, Any]]
    ) -> str:
        """Run with planning enabled."""
        self.logger.info("Using planning for complex task")
        
        # Get tool definitions for planner
        tool_defs = self.tool_registry.get_definitions()
        
        # Create plan
        plan = self.planner.create_plan(
            task=user_input,
            available_tools=tool_defs,
            context=context
        )
        
        # Execute plan
        plan = self.planner.execute_plan(plan, self.executor, context)
        
        # Build response from plan results
        results = [s.result for s in plan.steps if s.result]
        
        if results:
            final_response = "\n\n".join(results)
        else:
            final_response = "Task completed but no output generated"
        
        # Add to message history
        self._add_message("assistant", final_response)
        
        return final_response
    
    def _run_react(
        self,
        user_input: str,
        system_prompt: Optional[str],
        context: Optional[Dict[str, Any]]
    ) -> str:
        """Run with ReAct reasoning."""
        self.logger.info("Using ReAct for task")
        
        # Prepare system prompt
        if not system_prompt:
            system_prompt = self._get_default_system_prompt()
        
        # Run ReAct
        result = self.react_agent.run(
            user_input=user_input,
            system_prompt=system_prompt,
            context=context
        )
        
        # Track tokens (would come from actual LLM response)
        # self.token_tracker.add_usage(input_tokens, output_tokens)
        
        # Add to message history
        self._add_message("assistant", result.final_answer)
        
        # Record tool calls
        for tc in result.tool_calls:
            self._tool_call_history.append({
                "id": tc.id,
                "name": tc.name,
                "arguments": tc.arguments,
                "status": tc.status
            })
        
        return result.final_answer
    
    def _run_simple(
        self,
        user_input: str,
        system_prompt: Optional[str],
        context: Optional[Dict[str, Any]]
    ) -> str:
        """Run simple single-step tool use."""
        # Build messages
        messages = self._build_messages(user_input, system_prompt)
        
        # Add tool definitions
        tools = self.tool_registry.get_definitions()
        
        # Call LLM
        response = self.llm_client.complete(messages=messages, tools=tools)
        
        # Parse tool calls
        tool_calls = self.parser.parse(response)
        
        if not tool_calls:
            # No tool calls, return content
            return response.content
        
        # Execute tool calls
        results = self.executor.execute_batch(tool_calls, context)
        
        # Format response
        outputs = []
        for result in results:
            if result.success:
                outputs.append(result.output)
            else:
                outputs.append(f"Error: {result.error}")
        
        return "\n\n".join(outputs)
    
    def _build_messages(
        self,
        user_input: str,
        system_prompt: Optional[str]
    ) -> List[Dict[str, Any]]:
        """Build message list for LLM."""
        messages = []
        
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        messages.extend(self._messages)
        
        messages.append({"role": "user", "content": user_input})
        
        return messages
    
    def _get_default_system_prompt(self) -> str:
        """Get default system prompt for tool use."""
        return """You are a coding assistant with access to tools.
        
When you need to accomplish a task:
1. Think about what tools you need
2. Call the appropriate tool with parameters
3. Observe the result
4. Continue until the task is complete

Available tools:
{tools}

Use tools by outputting a tool_use block in your response."""
    
    def _add_message(self, role: str, content: str) -> None:
        """Add message to history."""
        self._messages.append({"role": role, "content": content})
    
    def get_stats(self) -> Dict[str, Any]:
        """Get usage statistics."""
        return {
            "total_messages": len(self._messages),
            "total_tool_calls": len(self._tool_call_history),
            "token_usage": self.token_tracker.get_summary()
        }
    
    def reset(self) -> None:
        """Reset the loop state."""
        self._messages.clear()
        self._tool_call_history.clear()
        self.token_tracker.reset()
        self.logger.info("ToolUseLoop reset")
```

---

## 🧪 Testing Day 3 Complete Tool Use System

```python
# tests/test_tool_use.py

import pytest
from unittest.mock import Mock, MagicMock

from coding_agent.tool_use.modern import (
    ToolCallParser, ToolExecutor, ToolCall, ToolCallResult
)
from coding_agent.tool_use.react import (
    ReActAgent, ReActStepType
)
from coding_agent.tool_use.planner import (
    TaskPlanner, Plan, PlanStep, PlanStepStatus
)
from coding_agent.tool_use.token_tracker import TokenTracker
from coding_agent.tool_use.loop import ToolUseLoop


class TestToolCallParser:
    """T29: Tool call parsing tests."""
    
    def test_parse_anthropic_format(self):
        """Parse Anthropic tool_use format."""
        parser = ToolCallParser()
        
        # Mock response with tool_use
        mock_response = Mock()
        mock_response.tool_calls = [
            {
                "id": "call_123",
                "function": {
                    "name": "read_file",
                    "arguments": '{"path": "main.py"}'
                }
            }
        ]
        
        tool_calls = parser.parse(mock_response, format="anthropic")
        
        assert len(tool_calls) == 1
        assert tool_calls[0].name == "read_file"
        assert tool_calls[0].arguments["path"] == "main.py"
    
    def test_parse_openai_format(self):
        """Parse OpenAI function_call format."""
        parser = ToolCallParser()
        
        mock_response = Mock()
        mock_response.tool_calls = [
            {
                "id": "call_456",
                "function": {
                    "name": "write_file",
                    "arguments": '{"path": "test.txt", "content": "hello"}'
                }
            }
        ]
        
        tool_calls = parser.parse(mock_response, format="openai")
        
        assert len(tool_calls) == 1
        assert tool_calls[0].name == "write_file"


class TestToolExecutor:
    """T30: Tool execution tests."""
    
    @pytest.fixture
    def mock_registry(self):
        """Create mock tool registry."""
        registry = Mock()
        
        # Mock tool
        mock_tool = Mock()
        mock_tool.name = "echo"
        mock_tool.description = "Echo back input"
        mock_tool.validate_input = Mock()
        mock_tool.execute = Mock(return_value=Mock(
            output="Echo: test message",
            success=True
        ))
        
        registry.get = Mock(return_value=mock_tool)
        registry.list_tools = Mock(return_value=["echo"])
        
        return registry
    
    def test_execute_tool(self, mock_registry):
        """Execute a tool call successfully."""
        executor = ToolExecutor(mock_registry)
        
        tool_call = ToolCall(
            id="call_1",
            name="echo",
            arguments={"message": "test message"}
        )
        
        result = executor.execute(tool_call)
        
        assert result.success is True
        assert "Echo" in result.output
        assert result.execution_time_ms > 0
    
    def test_execute_nonexistent_tool(self, mock_registry):
        """Execute non-existent tool fails gracefully."""
        mock_registry.get = Mock(side_effect=Exception("Tool not found"))
        
        executor = ToolExecutor(mock_registry)
        
        tool_call = ToolCall(
            id="call_2",
            name="nonexistent",
            arguments={}
        )
        
        result = executor.execute(tool_call)
        
        assert result.success is False
        assert result.error is not None


class TestTokenTracker:
    """T34: Token tracking tests."""
    
    def test_track_usage(self):
        """Track token usage correctly."""
        tracker = TokenTracker("claude-3-5-sonnet-20241022")
        
        tracker.add_usage(1000, 500)
        
        assert tracker.total_tokens() == 1500
        assert tracker.request_count() == 1
    
    def test_cost_calculation(self):
        """Calculate costs correctly."""
        tracker = TokenTracker("claude-3-5-sonnet-20241022")
        
        tracker.add_usage(1000, 500)
        
        # Input: 1000 * 0.003/1000 = $0.003
        # Output: 500 * 0.015/1000 = $0.0075
        # Total: $0.0105
        cost = tracker.total_cost()
        
        assert cost > 0
        assert cost < 1  # Should be small
    
    def test_budget_tracking(self):
        """Track budget limits."""
        tracker = TokenTracker("gpt-4o", budget_limit=1.0)
        
        tracker.add_usage(1000, 500)
        
        assert tracker.exceeds_budget(1.0) is False
        
        tracker.add_usage(100000, 50000)  # Big request
        
        assert tracker.exceeds_budget(1.0) is True


class TestReActAgent:
    """T32: ReAct pattern tests."""
    
    def test_react_creates_steps(self):
        """ReAct agent creates reasoning steps."""
        # This would need a mock LLM for full testing
        # For now, just test the structure
        from coding_agent.tool_use.react import ReActStep, ReActStepType
        
        step = ReActStep(
            step_type=ReActStepType.THOUGHT,
            content="I should read the file first"
        )
        
        assert step.step_type == ReActStepType.THOUGHT
        assert "read" in step.content.lower()


class TestToolUseLoop:
    """T36: Complete tool use loop tests."""
    
    @pytest.fixture
    def mock_components(self):
        """Create mock components."""
        llm_client = Mock()
        llm_client.model = "test-model"
        
        registry = Mock()
        registry.get_definitions = Mock(return_value=[])
        
        return llm_client, registry
    
    def test_loop_initialization(self, mock_components):
        """ToolUseLoop initializes correctly."""
        llm_client, registry = mock_components
        
        loop = ToolUseLoop(llm_client, registry)
        
        assert loop.llm_client is llm_client
        assert loop.tool_registry is registry
        assert loop.max_iterations == 10
    
    def test_complex_task_detection(self, mock_components):
        """Detect complex tasks that need planning."""
        llm_client, registry = mock_components
        
        loop = ToolUseLoop(llm_client, registry, use_planning=True)
        
        assert loop._is_complex_task("Read file A and then file B") is True
        assert loop._is_complex_task("Read the file") is False


class TestIntegration:
    """Integration tests for Day 3 complete system."""
    
    def test_all_components_integrate(self):
        """All Day 3 components can work together."""
        # This is a smoke test to ensure no import errors
        
        from coding_agent.tool_use.modern import (
            ToolCallParser, ToolExecutor, ToolCall
        )
        from coding_agent.tool_use.react import ReActAgent
        from coding_agent.tool_use.planner import TaskPlanner
        from coding_agent.tool_use.token_tracker import TokenTracker
        from coding_agent.tool_use.loop import ToolUseLoop
        
        # All imports successful
        assert ToolCallParser is not None
        assert ToolExecutor is not None
        assert ReActAgent is not None
        assert TaskPlanner is not None
        assert TokenTracker is not None
        assert ToolUseLoop is not None
```

---

## 🚀 Using Day 3 Tool Use in Your Agent

Here's how to integrate Day 3 Tool Use System with your Days 1-2 Agent:

```python
# scripts/run_agent_with_tool_use.py

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

from coding_agent.agent import Agent
from coding_agent.config import AgentConfig
from coding_agent.tools.registry import ToolRegistry
from coding_agent.llm.factory import create_llm_client

# Import Day 2 file tools
from coding_agent.tools import setup_file_tools

# Import Day 3 Tool Use
from coding_agent.tool_use.loop import ToolUseLoop


def create_autonomous_agent():
    """Create an agent with full autonomous tool use capability."""
    
    # Get allowed directories
    allowed_dirs = os.getenv("ALLOWED_DIRECTORIES", ".").split(",")
    
    # Create configuration
    config = AgentConfig(
        allowed_directories=allowed_dirs,
        read_only=os.getenv("READ_ONLY", "false").lower() == "true",
        shell_timeout=int(os.getenv("SHELL_TIMEOUT", "30")),
    )
    
    # Create LLM client
    llm_client = create_llm_client(config.llm)
    
    # Create tool registry and setup Day 2 tools
    registry = ToolRegistry()
    setup_file_tools(registry, config.allowed_directories)
    
    # Create the complete Tool Use Loop (Day 3)
    tool_loop = ToolUseLoop(
        llm_client=llm_client,
        tool_registry=registry,
        use_planning=True,
        use_react=True,
        max_iterations=10,
        budget_limit=10.0  # $10 budget
    )
    
    return tool_loop


if __name__ == "__main__":
    agent = create_autonomous_agent()
    
    # Example: Autonomous task
    response = agent.run(
        "Read all Python files in the src directory, "
        "search for 'TODO' comments, and create a summary file."
    )
    
    print("Response:")
    print(response)
    
    # Check stats
    stats = agent.get_stats()
    print("\nStats:")
    print(f"  Messages: {stats['total_messages']}")
    print(f"  Tool Calls: {stats['total_tool_calls']}")
    print(f"  Total Cost: ${stats['token_usage']['total_cost']:.4f}")
```

---

## 📋 Day 3 Summary Checklist

After completing Day 3, verify you have:

- [x] **ToolCallParser** - Parses LLM responses for tool calls (T29)
- [x] **ToolExecutor** - Executes tools and handles errors (T30-T31)
- [x] **ReActAgent** - Implements Thought → Action → Observation (T32)
- [x] **TaskPlanner** - Creates plans for multi-step tasks (T33)
- [x] **TokenTracker** - Tracks usage and costs (T34)
- [x] **ToolUseLoop** - Complete integration of all components (T36)
- [x] **Session Persistence** - Save/load conversations (T35)

---

## 🎯 What's Next: Day 4

With Day 3 complete, your agent can:
- ✅ Parse tool calls from LLM responses
- ✅ Execute tools autonomously
- ✅ Use ReAct reasoning pattern
- ✅ Plan multi-step tasks
- ✅ Track token usage and costs

**Day 4: Shell & Context** will add:
- Shell tool design: execute_shell
- Command whitelisting
- Timeout and output limits
- Working directory management
- Context problem: Token limits
- Sliding window and message management

Ready to continue? Let's add shell execution and context management! 🐚

---

## 🔗 Code Continuity Confirmation

This tutorial (T36) builds directly on:
- **T13** (Day 1 Capstone): Complete Agent with DI, ToolRegistry, LLMClient
- **T24** (Day 2 Capstone): Complete file operation suite
- **T25-T35** (Day 3 concepts): Tool use loop concepts

All code in this tutorial integrates with the existing architecture from T13/T24, using the same patterns:
- Strategy pattern for LLM clients
- Command pattern for tool execution
- Observer pattern for events
- Dependency injection for loose coupling

The complete project is now ready for Day 4!