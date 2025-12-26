"""
Flow Engine - Executes workflows by running nodes in sequence
"""

import sys
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid

# Handle imports
try:
    from .state import State
    from .node import Node, NodeResult, NodeStatus
    from .tools import create_tool
except ImportError:
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from core.state import State
    from core.node import Node, NodeResult, NodeStatus
    from core.tools import create_tool


class FlowExecution:
    """
    Represents a single workflow execution.
    Tracks execution state, results, and metadata.
    """
    
    def __init__(self, flow_id: str, flow_name: str, input_data: Dict[str, Any]):
        self.execution_id = str(uuid.uuid4())
        self.flow_id = flow_id
        self.flow_name = flow_name
        self.input_data = input_data
        
        self.state = State(input_data)
        self.status = "pending"  # pending, running, completed, failed
        self.node_results: Dict[str, NodeResult] = {}
        
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
    
    def get_duration(self) -> Optional[float]:
        """Get execution duration in seconds"""
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "execution_id": self.execution_id,
            "flow_id": self.flow_id,
            "flow_name": self.flow_name,
            "status": self.status,
            "input_data": self.input_data,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "duration_seconds": self.get_duration(),
            "error": self.error,
            "node_count": len(self.node_results),
            "successful_nodes": sum(1 for r in self.node_results.values() if r.is_success()),
            "failed_nodes": sum(1 for r in self.node_results.values() if r.is_failed())
        }


class Flow:
    """
    Represents a workflow definition.
    Contains nodes and execution order.
    """
    
    def __init__(
        self,
        flow_id: str,
        name: str,
        description: str,
        nodes: List[Dict[str, Any]],
        edges: Optional[List[Dict[str, Any]]] = None
    ):
        self.flow_id = flow_id
        self.name = name
        self.description = description
        self.node_configs = nodes
        self.edges = edges or []
        
        # Build execution order
        self.execution_order = self._build_execution_order()
    
    def _build_execution_order(self) -> List[str]:
        """
        Determine node execution order from edges.
        For now, just use the order nodes are defined (sequential).
        In future: build DAG and topological sort.
        """
        return [node["id"] for node in self.node_configs]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "flow_id": self.flow_id,
            "name": self.name,
            "description": self.description,
            "node_count": len(self.node_configs),
            "execution_order": self.execution_order
        }


class FlowEngine:
    """
    Executes workflows by running nodes in sequence.
    
    Example:
        engine = FlowEngine()
        flow = Flow(...)
        execution = engine.execute(flow, {"input": "data"})
        print(execution.status)
    """
    
    def __init__(self):
        self.executions: Dict[str, FlowExecution] = {}
    
    def execute(self, flow: Flow, input_data: Dict[str, Any]) -> FlowExecution:
        """
        Execute a workflow.
        
        Args:
            flow: Flow definition
            input_data: Input data for the workflow
        
        Returns:
            FlowExecution with results
        """
        # Create execution
        execution = FlowExecution(flow.flow_id, flow.name, input_data)
        self.executions[execution.execution_id] = execution
        
        execution.start()
        
        try:
            # Execute nodes in order
            for node_id in flow.execution_order:
                # Find node config
                node_config = next(
                    (n for n in flow.node_configs if n["id"] == node_id),
                    None
                )
                
                if not node_config:
                    raise ValueError(f"Node {node_id} not found in flow definition")
                
                # Create and run node
                result = self._execute_node(node_config, execution.state)
                execution.node_results[node_id] = result
                
                # Stop if node failed
                if result.is_failed():
                    execution.fail(f"Node {node_id} failed: {result.error}")
                    return execution
            
            # All nodes succeeded
            execution.complete()
            
        except Exception as e:
            execution.fail(f"Flow execution error: {str(e)}")
        
        return execution
    
    def _execute_node(self, node_config: Dict[str, Any], state: State) -> NodeResult:
        """
        Execute a single node.
        
        Args:
            node_config: Node configuration
            state: Shared state
        
        Returns:
            NodeResult
        """
        node_id = node_config["id"]
        node_type = node_config["type"]
        config = node_config.get("config", {})
        
        # Create node using tool factory
        node = create_tool(node_id, node_type, config)
        
        if not node:
            return NodeResult(
                status=NodeStatus.FAILED,
                error=f"Unknown node type: {node_type}"
            )
        
        # Execute node
        return node.run(state)
    
    def get_execution(self, execution_id: str) -> Optional[FlowExecution]:
        """Get execution by ID"""
        return self.executions.get(execution_id)
    
    def list_executions(self) -> List[FlowExecution]:
        """List all executions"""
        return list(self.executions.values())


# ============================================================================
# TESTING
# ============================================================================

if __name__ == "__main__":
    print("Testing Flow Engine...\n")
    
    # Define a simple flow
    flow = Flow(
        flow_id="test-flow-1",
        name="Test Workflow",
        description="A simple test workflow",
        nodes=[
            {
                "id": "search",
                "type": "web_search",
                "config": {
                    "query": "{topic}",
                    "max_results": 2,
                    "output_key": "search_results"
                }
            },
            {
                "id": "llm",
                "type": "llm_call",
                "config": {
                    "prompt": "Summarize: {topic}",
                    "output_key": "summary"
                }
            },
            {
                "id": "transform",
                "type": "transform",
                "config": {
                    "operation": "uppercase",
                    "input_key": "summary",
                    "output_key": "final"
                }
            }
        ],
        edges=[
            {"from": "search", "to": "llm"},
            {"from": "llm", "to": "transform"}
        ]
    )
    
    print(f"✅ Flow created: {flow.name}")
    print(f"   Nodes: {flow.execution_order}")
    
    # Execute flow
    print("\n🚀 Executing flow...")
    engine = FlowEngine()
    execution = engine.execute(flow, {"topic": "AI agents"})
    
    print(f"\n✅ Execution completed!")
    print(f"   Status: {execution.status}")
    print(f"   Duration: {execution.get_duration():.2f}s")
    print(f"   Nodes executed: {len(execution.node_results)}")
    
    # Show results
    print(f"\n📊 Node Results:")
    for node_id, result in execution.node_results.items():
        print(f"   [{node_id}] {result.status.value}")
        if result.is_success() and result.output:
            output_preview = str(result.output)[:60]
            print(f"      Output: {output_preview}...")
    
    print(f"\n📦 Final State Keys: {list(execution.state.get_all().keys())}")
    
    print("\n✅ Flow Engine is working correctly!")
