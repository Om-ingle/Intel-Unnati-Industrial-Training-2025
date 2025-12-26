"""
Base Node class for workflow nodes
"""

import sys
from pathlib import Path
from abc import ABC, abstractmethod
from typing import Any, Dict

# Handle imports
try:
    from .state import State, NodeResult
except ImportError:
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from core.state import State, NodeResult


class Node(ABC):
    """
    Abstract base class for all workflow nodes.
    
    Each node:
    - Has a unique ID
    - Has configuration
    - Executes some logic
    - Returns a result
    """
    
    def __init__(self, node_id: str, config: Dict[str, Any]):
        self.node_id = node_id
        self.config = config
    
    @abstractmethod
    def execute(self, state: State) -> NodeResult:
        """
        Execute the node logic.
        
        Args:
            state: Shared workflow state
        
        Returns:
            NodeResult with output and status
        """
        pass
    
    def __repr__(self):
        return f"{self.__class__.__name__}(id={self.node_id})"


# ============================================================================
# TESTING
# ============================================================================

if __name__ == "__main__":
    print("Testing Node base class...\n")
    
    # Create a simple test node
    class TestNode(Node):
        def execute(self, state: State) -> NodeResult:
            value = state.get("input", 0)
            result = value * 2
            state.set("output", result)
            return NodeResult.success(
                output=result,
                metadata={"operation": "multiply"}
            )
    
    # Test it
    state = State()
    state.set("input", 5)
    
    node = TestNode("test1", {"multiplier": 2})
    result = node.execute(state)
    
    print(f"✅ Node executed: {node}")
    print(f"   Success: {result.is_success()}")
    print(f"   Output: {result.output}")
    print(f"   State output: {state.get('output')}")
    
    print("\n✅ Node base class is working!")
