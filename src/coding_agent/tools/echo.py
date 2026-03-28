"""
Echo tool - Simple tool for testing the tool system.
"""

from typing import Optional

from .base import BaseTool, ToolDefinition, ToolParameter


class EchoTool(BaseTool):
    """
    Echo tool - Returns the input text, optionally transformed.
    
    This is primarily used for testing the tool system.
    """
    
    def define(self) -> ToolDefinition:
        return ToolDefinition(
            name="echo",
            description="Echoes back the input text with optional transformation. "
                       "Useful for testing the tool system or verifying connectivity.",
            parameters={
                "text": ToolParameter(
                    type="string",
                    description="The text to echo back verbatim"
                ),
                "uppercase": ToolParameter(
                    type="boolean",
                    description="Whether to return the text in uppercase",
                    default=False
                ),
                "reverse": ToolParameter(
                    type="boolean", 
                    description="Whether to reverse the text",
                    default=False
                )
            },
            required=["text"]
        )
    
    def execute(self, text: str, uppercase: bool = False, reverse: bool = False) -> str:
        """
        Execute the echo tool.
        
        Args:
            text: Text to echo
            uppercase: Transform to uppercase?
            reverse: Reverse the text?
            
        Returns:
            The transformed text
        """
        result = text
        
        if uppercase:
            result = result.upper()
        
        if reverse:
            result = result[::-1]
        
        return result