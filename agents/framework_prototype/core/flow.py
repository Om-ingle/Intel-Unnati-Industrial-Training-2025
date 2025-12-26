"""
Flow and Execution classes
"""

import sys
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

# Handle imports
try:
    from .state import State, NodeStatus
except ImportError:
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from core.state import State, NodeStatus


class Flow:
    """
    Represents a workflow definition.
    Contains nodes and edges that define execution order.
    """
    
    def __init__(
        self,
        flow_id: str,
        name: str,
        description: str = "",
        nodes: Optional[List[Dict[str, Any]]] = None,
        edges: Optional[List[Dict[str, str]]] = None
    ):
        self.flow_id = flow_id
        self.name = name
        self.description = description
        self.node_configs = nodes or []
        self.edges = edges or []
        
        # Compute execution order
        self.execution_order = self._compute_execution_order()
    
    def _compute_execution_order(self) -> List[str]:
        """
        Compute the order in which nodes should be executed.
        Uses topological sort for DAG.
        """
        if not self.edges:
            # No edges, just return nodes in order
            return [node["id"] for node in self.node_configs]
        
        # Build adjacency list
        graph = {node["id"]: [] for node in self.node_configs}
        in_degree = {node["id"]: 0 for node in self.node_configs}
        
        for edge in self.edges:
            from_node = edge["from"]
            to_node = edge["to"]
            graph[from_node].append(to_node)
            in_degree[to_node] += 1
        
        # Topological sort (Kahn's algorithm)
        queue = [node_id for node_id, degree in in_degree.items() if degree == 0]
        order = []
        
        while queue:
            node_id = queue.pop(0)
            order.append(node_id)
            
            for neighbor in graph[node_id]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)
        
        return order
    
    def __repr__(self):
        return f"Flow(id={self.flow_id}, name={self.name}, nodes={len(self.node_configs)})"


class FlowExecution:
    """
    Represents a single execution of a flow.
    Tracks state, results, and metadata.
    """
    
    def __init__(self, flow_id: str, flow_name: str, input_data: Dict[str, Any]):
        import uuid
        
        self.execution_id = f"exec-{str(uuid.uuid4())[:8]}"
        self.flow_id = flow_id
        self.flow_name = flow_name
        self.input_data = input_data
        
        self.state = State()
        self.node_results: Dict[str, Any] = {}
        
        self.status = "pending"
        self.started_at: Optional[datetime] = None
        self.completed_at: Optional[datetime] = None
        self.error: Optional[str] = None
    
    def start(self):
        """Mark execution as started"""
        self.status = "running"
        self.started_at = datetime.now()
    
    def complete(self):
        """Mark execution as completed"""
        self.status = "completed"
        self.completed_at = datetime.now()
    
    def fail(self, error: str):
        """Mark execution as failed"""
        self.status = "failed"
        self.completed_at = datetime.now()
        self.error = error
    
    def get_duration(self) -> float:
        """Get execution duration in seconds"""
        if not self.started_at:
            return 0.0
        
        end_time = self.completed_at or datetime.now()
        return (end_time - self.started_at).total_seconds()
    
    def __repr__(self):
        return f"FlowExecution(id={self.execution_id}, status={self.status})"


# ============================================================================
# TESTING
# ============================================================================

if __name__ == "__main__":
    print("Testing Flow and FlowExecution...\n")
    
    # Test Flow
    print("[1/2] Testing Flow...")
    flow = Flow(
        flow_id="test-flow-1",
        name="Test Flow",
        description="A test workflow",
        nodes=[
            {"id": "node1", "type": "transform"},
            {"id": "node2", "type": "output"},
        ],
        edges=[
            {"from": "node1", "to": "node2"}
        ]
    )
    
    print(f"✅ Created: {flow}")
    print(f"   Execution order: {flow.execution_order}")
    
    # Test FlowExecution
    print("\n[2/2] Testing FlowExecution...")
    execution = FlowExecution(
        flow_id=flow.flow_id,
        flow_name=flow.name,
        input_data={"test": "data"}
    )
    
    execution.start()
    print(f"✅ Started: {execution}")
    
    import time
    time.sleep(0.1)
    
    execution.complete()
    print(f"✅ Completed: {execution}")
    print(f"   Duration: {execution.get_duration():.3f}s")
    
    print("\n✅ Flow classes are working!")
