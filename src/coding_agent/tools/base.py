"""
Base classes for the tool system.

This module defines the abstract base for all tools in our agent.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class ToolParameter(BaseModel):
    """Definition of a single tool parameter."""
    type: str = Field(..., description="JSON Schema type (string, integer, etc.)")
    description: str = Field(..., description="Human-readable description")
    default: Optional[Any] = Field(default=None, description="Default value if optional")
    enum: Optional[list] = Field(default=None, description="Allowed values")
    minimum: Optional[float] = Field(default=None, description="Minimum for numbers")
    maximum: Optional[float] = Field(default=None, description="Maximum for numbers")


class ToolDefinition(BaseModel):
    """Complete tool definition following Anthropic format."""
    name: str = Field(..., description="Tool name (unique identifier)")
    description: str = Field(..., description="What this tool does")
    parameters: Dict[str, ToolParameter] = Field(
        default_factory=dict,
        description="Tool parameters"
    )
    required: list = Field(
        default_factory=list,
        description="Required parameter names"
    )
    
    def to_anthropic_schema(self) -> Dict[str, Any]:
        """
        Convert to Anthropic's tool use format.
        
        This creates the exact JSON structure the Claude API expects.
        """
        properties = {}
        for param_name, param_def in self.parameters.items():
            prop = {"type": param_def.type, "description": param_def.description}
            
            if param_def.default is not None:
                prop["default"] = param_def.default
            if param_def.enum:
                prop["enum"] = param_def.enum
            if param_def.minimum is not None:
                prop["minimum"] = param_def.minimum
            if param_def.maximum is not None:
                prop["maximum"] = param_def.maximum
                
            properties[param_name] = prop
        
        schema = {
            "type": "object",
            "properties": properties,
            "required": self.required
        }
        
        return {
            "name": self.name,
            "description": self.description,
            "input_schema": schema
        }


class BaseTool(ABC):
    """
    Abstract base class for all tools.
    
    All tools in our system should inherit from this class.
    """
    
    def __init__(self):
        self._definition = self.define()
    
    @abstractmethod
    def define(self) -> ToolDefinition:
        """
        Define this tool's interface.
        
        Subclasses must implement this to provide their tool definition.
        """
        pass
    
    @abstractmethod
    def execute(self, **kwargs) -> str:
        """
        Execute the tool with given parameters.
        
        Args:
            **kwargs: Parameters as defined in the tool definition
            
        Returns:
            str: Tool execution result (text)
        """
        pass
    
    @property
    def name(self) -> str:
        return self._definition.name
    
    @property
    def definition(self) -> ToolDefinition:
        return self._definition
    
    def get_anthropic_schema(self) -> Dict[str, Any]:
        """Get the Anthropic-format schema for this tool."""
        return self._definition.to_anthropic_schema()