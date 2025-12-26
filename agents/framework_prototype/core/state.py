"""
State management for agent workflows
"""

from typing import Any, Dict, Optional
from datetime import datetime
from enum import Enum


# ============================================================================
# STATE CLASS
# ============================================================================

class State:
    """
    Shared state across workflow execution.
    Stores variables that can be accessed by all nodes.
    """
    
    def __init__(self):
        self._data: Dict[str, Any] = {}
        self._history: list = []
    
    def set(self, key: str, value: Any):
        """Set a value in state"""
        self._data[key] = value
        self._history.append({
            "action": "set",
            "key": key,
            "timestamp": datetime.now()
        })
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a value from state"""
        return self._data.get(key, default)
    
    def delete(self, key: str):
        """Delete a key from state"""
        if key in self._data:
            del self._data[key]
            self._history.append({
                "action": "delete",
                "key": key,
                "timestamp": datetime.now()
            })
    
    def has(self, key: str) -> bool:
        """Check if key exists"""
        return key in self._data
    
    def get_all(self) -> Dict[str, Any]:
        """Get all state data"""
        return self._data.copy()
    
    def clear(self):
        """Clear all state"""
        self._data.clear()
        self._history.append({
            "action": "clear",
            "timestamp": datetime.now()
        })


# ============================================================================
# NODE STATUS
# ============================================================================

class NodeStatus(Enum):
    """Status of node execution"""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"


# ============================================================================
# NODE RESULT
# ============================================================================

class NodeResult:
    """
    Result of a node execution.
    Contains output, status, error info, and metadata.
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
    
    @classmethod
    def success(cls, output: Any = None, metadata: Optional[Dict[str, Any]] = None):
        """Create a successful result"""
        return cls(NodeStatus.SUCCESS, output=output, metadata=metadata)
    
    @classmethod
    def failure(cls, error: str, metadata: Optional[Dict[str, Any]] = None):
        """Create a failed result"""
        return cls(NodeStatus.FAILED, error=error, metadata=metadata)
    
    @classmethod
    def skipped(cls, reason: str = "Skipped", metadata: Optional[Dict[str, Any]] = None):
        """Create a skipped result"""
        if metadata is None:
            metadata = {}
        metadata["skip_reason"] = reason
        return cls(NodeStatus.SKIPPED, metadata=metadata)
    
    def is_success(self) -> bool:
        """Check if execution was successful"""
        return self.status == NodeStatus.SUCCESS
    
    def is_failed(self) -> bool:
        """Check if execution failed"""
        return self.status == NodeStatus.FAILED
    
    def is_skipped(self) -> bool:
        """Check if execution was skipped"""
        return self.status == NodeStatus.SKIPPED


# ============================================================================
# TESTING
# ============================================================================

if __name__ == "__main__":
    print("Testing State Management...\n")
    
    # Test State
    print("[1/3] Testing State...")
    state = State()
    state.set("user", "Alice")
    state.set("score", 95)
    state.set("items", ["a", "b", "c"])
    
    print(f"✅ user = {state.get('user')}")
    print(f"✅ score = {state.get('score')}")
    print(f"✅ items = {state.get('items')}")
    print(f"✅ missing = {state.get('missing', 'default')}")
    
    # Test NodeResult
    print("\n[2/3] Testing NodeResult...")
    
    success_result = NodeResult.success(
        output="Task completed",
        metadata={"duration": 1.5}
    )
    print(f"✅ Success result: {success_result.is_success()}")
    
    failure_result = NodeResult.failure(
        error="Connection timeout",
        metadata={"attempts": 3}
    )
    print(f"✅ Failure result: {failure_result.is_failed()}")
    
    skipped_result = NodeResult.skipped(
        reason="Condition not met"
    )
    print(f"✅ Skipped result: {skipped_result.is_skipped()}")
    
    # Test NodeStatus
    print("\n[3/3] Testing NodeStatus...")
    print(f"✅ Statuses: {[s.value for s in NodeStatus]}")
    
    print("\n✅ State management is working correctly!")
