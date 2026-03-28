"""
Tool registry - Manages all available tools.
"""

from typing import Dict, List, Optional, Any
import logging

from .base import BaseTool

logger = logging.getLogger(__name__)


class ToolRegistry:
    """
    Central registry for all available tools.
    
    This class manages tool registration, lookup, and execution.
    """
    
    def __init__(self):
        self._tools: Dict[str, BaseTool] = {}
    
    def register(self, tool: BaseTool) -> None:
        """
        Register a tool.
        
        Args:
            tool: Tool instance to register
            
        Raises:
            ValueError: If a tool with the same name already exists
        """
        if tool.name in self._tools:
            raise ValueError(f"Tool '{tool.name}' is already registered")
        
        self._tools[tool.name] = tool
        logger.info(f"Registered tool: {tool.name}")
    
    def unregister(self, name: str) -> None:
        """
        Unregister a tool.
        
        Args:
            name: Tool name to remove
            
        Raises:
            KeyError: If tool doesn't exist
        """
        del self._tools[name]
        logger.info(f"Unregistered tool: {name}")
    
    def get(self, name: str) -> Optional[BaseTool]:
        """
        Get a tool by name.
        
        Args:
            name: Tool name to look up
            
        Returns:
            Tool instance or None if not found
        """
        return self._tools.get(name)
    
    def list_tools(self) -> List[str]:
        """Get list of all registered tool names."""
        return list(self._tools.keys())
    
    def get_all_schemas(self) -> List[Dict[str, Any]]:
        """
        Get Anthropic-format schemas for all tools.
        
        Returns:
            List of tool schemas ready for API calls
        """
        return [tool.get_anthropic_schema() for tool in self._tools.values()]
    
    def execute(self, name: str, parameters: Dict[str, Any]) -> str:
        """
        Execute a tool by name with given parameters.
        
        Args:
            name: Tool name to execute
            parameters: Parameters to pass to the tool
            
        Returns:
            Tool execution result
            
        Raises:
            KeyError: If tool doesn't exist
            Exception: If tool execution fails
        """
        tool = self.get(name)
        if not tool:
            raise KeyError(f"Tool '{name}' not found in registry")
        
        logger.info(f"Executing tool: {name} with params: {parameters}")
        
        try:
            result = tool.execute(**parameters)
            return result
        except Exception as e:
            logger.error(f"Tool execution failed: {e}")
            raise
    
    def __len__(self) -> int:
        return len(self._tools)
    
    def __contains__(self, name: str) -> bool:
        return name in self._tools


# Global registry instance
_default_registry: Optional[ToolRegistry] = None


def get_registry() -> ToolRegistry:
    """Get the default global registry."""
    global _default_registry
    if _default_registry is None:
        _default_registry = ToolRegistry()
    return _default_registry


def register_default_tools() -> ToolRegistry:
    """Register the default set of tools."""
    from .echo import EchoTool
    
    registry = get_registry()
    
    # Register built-in tools
    echo_tool = EchoTool()
    registry.register(echo_tool)
    
    return registry