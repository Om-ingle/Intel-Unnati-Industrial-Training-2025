"""
Tool system for nodes
"""

import sys
from pathlib import Path
from typing import Any, Dict, Callable, Optional

# Handle imports - import from state, not node
try:
    from .state import State, NodeResult, NodeStatus
except ImportError:
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from core.state import State, NodeResult, NodeStatus


class Tool:
    """
    A reusable tool that can be called by nodes.
    
    Example:
        def multiply(x, y):
            return x * y
        
        tool = Tool("multiply", multiply, "Multiplies two numbers")
    """
    
    def __init__(
        self,
        name: str,
        func: Callable,
        description: str = "",
        parameters: Optional[Dict[str, Any]] = None
    ):
        self.name = name
        self.func = func
        self.description = description
        self.parameters = parameters or {}
    
    def execute(self, **kwargs) -> Any:
        """Execute the tool with given arguments"""
        return self.func(**kwargs)
    
    def __repr__(self):
        return f"Tool(name={self.name})"


class ToolRegistry:
    """
    Registry for managing available tools.
    
    Example:
        registry = ToolRegistry()
        registry.register(Tool("add", lambda x, y: x + y))
        result = registry.execute("add", x=1, y=2)
    """
    
    def __init__(self):
        self._tools: Dict[str, Tool] = {}
    
    def register(self, tool: Tool):
        """Register a tool"""
        self._tools[tool.name] = tool
    
    def get(self, name: str) -> Optional[Tool]:
        """Get a tool by name"""
        return self._tools.get(name)
    
    def execute(self, name: str, **kwargs) -> Any:
        """Execute a tool by name"""
        tool = self.get(name)
        if not tool:
            raise ValueError(f"Tool not found: {name}")
        return tool.execute(**kwargs)
    
    def list_tools(self) -> list:
        """List all registered tools"""
        return list(self._tools.keys())
    
    def __repr__(self):
        return f"ToolRegistry(tools={len(self._tools)})"


# ============================================================================
# TESTING
# ============================================================================

if __name__ == "__main__":
    print("Testing Tool System...\n")
    
    # Test Tool
    print("[1/2] Testing Tool...")
    
    def add_numbers(x, y):
        return x + y
    
    tool = Tool("add", add_numbers, "Adds two numbers")
    result = tool.execute(x=5, y=3)
    
    print(f"✅ Tool: {tool}")
    print(f"   Result: {result}")
    
    # Test ToolRegistry
    print("\n[2/2] Testing ToolRegistry...")
    
    registry = ToolRegistry()
    registry.register(tool)
    registry.register(Tool("multiply", lambda x, y: x * y, "Multiplies"))
    
    print(f"✅ Registry: {registry}")
    print(f"   Tools: {registry.list_tools()}")
    print(f"   Add result: {registry.execute('add', x=10, y=5)}")
    print(f"   Multiply result: {registry.execute('multiply', x=10, y=5)}")
    
    print("\n✅ Tool system is working!")
