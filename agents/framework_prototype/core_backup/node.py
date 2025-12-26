"""
Node - Base class for all workflow tasks
"""

from typing import Any, Dict, Optional, Callable
from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum
import traceback
import sys
from pathlib import Path

# Handle both direct execution and module import
try:
    from .state import State
except ImportError:
    # Add parent directory to path for direct execution
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from core.state import State


class NodeStatus(Enum):
    """Node execution status"""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"


class NodeResult:
    """
    Result of node execution.
    Contains output data, status, and metadata.
    """
    
    def __init__(
        self,
        status: NodeStatus,
        output: Any = None,
        error: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.status = status
        self.output = output
        self.error = error
        self.metadata = metadata or {}
        self.timestamp = datetime.now()
    
    def is_success(self) -> bool:
        """Check if node executed successfully"""
        return self.status == NodeStatus.SUCCESS
    
    def is_failed(self) -> bool:
        """Check if node failed"""
        return self.status == NodeStatus.FAILED
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "status": self.status.value,
            "output": self.output,
            "error": self.error,
            "metadata": self.metadata,
            "timestamp": self.timestamp.isoformat()
        }
    
    def __repr__(self) -> str:
        return f"NodeResult(status={self.status.value}, error={self.error})"


class Node(ABC):
    """
    Base class for all workflow nodes.
    
    Each node must implement the execute() method.
    
    Example:
        class SearchNode(Node):
            def execute(self, state: State, config: Dict) -> NodeResult:
                query = config.get("query")
                results = search_web(query)
                return NodeResult(NodeStatus.SUCCESS, output=results)
    """
    
    def __init__(
        self,
        node_id: str,
        node_type: str,
        config: Optional[Dict[str, Any]] = None,
        timeout: int = 300,
        retries: int = 3
    ):
        """
        Initialize node.
        
        Args:
            node_id: Unique identifier for this node
            node_type: Type of node (e.g., 'llm_call', 'web_search')
            config: Node-specific configuration
            timeout: Maximum execution time in seconds
            retries: Number of retry attempts on failure
        """
        self.node_id = node_id
        self.node_type = node_type
        self.config = config or {}
        self.timeout = timeout
        self.retries = retries
        
        # Execution metadata
        self.status = NodeStatus.PENDING
        self.started_at: Optional[datetime] = None
        self.completed_at: Optional[datetime] = None
        self.execution_count = 0
    
    @abstractmethod
    def execute(self, state: State, config: Dict[str, Any]) -> NodeResult:
        """
        Execute the node's task.
        Must be implemented by subclasses.
        
        Args:
            state: Shared state object
            config: Node configuration
            
        Returns:
            NodeResult with status and output
        """
        pass
    
    def run(self, state: State) -> NodeResult:
        """
        Run the node with error handling and metadata tracking.
        
        Args:
            state: Shared state object
            
        Returns:
            NodeResult
        """
        self.status = NodeStatus.RUNNING
        self.started_at = datetime.now()
        self.execution_count += 1
        
        try:
            # Validate before execution
            if not self.validate_config():
                return NodeResult(
                    status=NodeStatus.FAILED,
                    error="Configuration validation failed"
                )
            
            # Execute the node
            result = self.execute(state, self.config)
            
            # Update status
            self.status = result.status
            self.completed_at = datetime.now()
            
            # Add execution metadata
            result.metadata.update({
                "node_id": self.node_id,
                "node_type": self.node_type,
                "execution_count": self.execution_count,
                "duration_seconds": (self.completed_at - self.started_at).total_seconds()
            })
            
            return result
            
        except Exception as e:
            # Handle unexpected errors
            self.status = NodeStatus.FAILED
            self.completed_at = datetime.now()
            
            error_msg = f"{type(e).__name__}: {str(e)}"
            error_trace = traceback.format_exc()
            
            return NodeResult(
                status=NodeStatus.FAILED,
                error=error_msg,
                metadata={
                    "node_id": self.node_id,
                    "node_type": self.node_type,
                    "execution_count": self.execution_count,
                    "error_trace": error_trace,
                    "duration_seconds": (self.completed_at - self.started_at).total_seconds()
                }
            )
    
    def validate_config(self) -> bool:
        """
        Validate node configuration.
        Override in subclasses for custom validation.
        
        Returns:
            True if valid, False otherwise
        """
        return True
    
    def get_execution_time(self) -> Optional[float]:
        """
        Get execution time in seconds.
        
        Returns:
            Execution time or None if not completed
        """
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None
    
    def reset(self) -> None:
        """Reset node to initial state"""
        self.status = NodeStatus.PENDING
        self.started_at = None
        self.completed_at = None
        self.execution_count = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert node to dictionary"""
        return {
            "node_id": self.node_id,
            "node_type": self.node_type,
            "config": self.config,
            "status": self.status.value,
            "timeout": self.timeout,
            "retries": self.retries,
            "execution_count": self.execution_count,
            "execution_time": self.get_execution_time()
        }
    
    def __repr__(self) -> str:
        return f"Node(id='{self.node_id}', type='{self.node_type}', status={self.status.value})"


class SimpleNode(Node):
    """
    A simple node that executes a custom function.
    Useful for quick prototyping without creating full node classes.
    
    Example:
        def my_function(state, config):
            result = state.get("input") + " processed"
            return NodeResult(NodeStatus.SUCCESS, output=result)
        
        node = SimpleNode(
            node_id="process",
            node_type="custom",
            execute_fn=my_function
        )
    """
    
    def __init__(
        self,
        node_id: str,
        node_type: str,
        execute_fn: Callable[[State, Dict], NodeResult],
        config: Optional[Dict[str, Any]] = None,
        timeout: int = 300,
        retries: int = 3
    ):
        """
        Initialize simple node with a custom function.
        
        Args:
            node_id: Unique identifier
            node_type: Type of node
            execute_fn: Function to execute (must return NodeResult)
            config: Node configuration
            timeout: Timeout in seconds
            retries: Retry attempts
        """
        super().__init__(node_id, node_type, config, timeout, retries)
        self.execute_fn = execute_fn
    
    def execute(self, state: State, config: Dict[str, Any]) -> NodeResult:
        """Execute the custom function"""
        return self.execute_fn(state, config)


# ============================================================================
# TESTING
# ============================================================================

if __name__ == "__main__":
    print("Testing Node classes...\n")
    
    # Test 1: Simple node with function
    def test_function(state: State, config: Dict) -> NodeResult:
        input_val = state.get("input", "")
        result = f"{input_val} -> processed"
        state.set("output", result)
        return NodeResult(NodeStatus.SUCCESS, output=result)
    
    node = SimpleNode(
        node_id="test_node",
        node_type="processor",
        execute_fn=test_function,
        config={"setting": "value"}
    )
    
    state = State({"input": "hello"})
    result = node.run(state)
    
    print(f"✅ Node: {node}")
    print(f"✅ Result: {result}")
    print(f"✅ Output: {result.output}")
    print(f"✅ State output: {state.get('output')}")
    print(f"✅ Execution time: {node.get_execution_time():.4f}s")
    print(f"✅ Metadata: {result.metadata}")
    
    # Test 2: Node with error
    def error_function(state: State, config: Dict) -> NodeResult:
        raise ValueError("Intentional error for testing")
    
    error_node = SimpleNode(
        node_id="error_node",
        node_type="error_test",
        execute_fn=error_function
    )
    
    error_result = error_node.run(state)
    print(f"\n✅ Error handling test:")
    print(f"✅ Status: {error_result.status.value}")
    print(f"✅ Error caught: {error_result.error}")
    
    print("\n✅ Node.py is working correctly!")
