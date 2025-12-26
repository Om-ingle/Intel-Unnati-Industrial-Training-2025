"""
Parallel Execution Engine
"""

import sys
from pathlib import Path
from typing import Dict, Any, List, Set
import asyncio
from concurrent.futures import ThreadPoolExecutor

# Handle imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from core import Flow, FlowExecution, State, NodeStatus, NodeResult
from nodes import ALL_NODE_TYPES


class ParallelFlowEngine:
    """Execute flows with parallel nodes"""
    
    def __init__(self, max_workers: int = 5):
        self.node_types = ALL_NODE_TYPES
        self.max_workers = max_workers
    
    def _build_dependency_graph(self, flow: Flow) -> Dict[str, Set[str]]:
        """Build dependency graph"""
        dependencies = {node["id"]: set() for node in flow.node_configs}
        
        for edge in flow.edges:
            from_node = edge["from"]
            to_node = edge["to"]
            dependencies[to_node].add(from_node)
        
        return dependencies
    
    def _get_executable_nodes(
        self,
        dependencies: Dict[str, Set[str]],
        completed: Set[str],
        running: Set[str]
    ) -> List[str]:
        """Get nodes that can execute now"""
        executable = []
        
        for node_id, deps in dependencies.items():
            if node_id in completed or node_id in running:
                continue
            
            if deps.issubset(completed):
                executable.append(node_id)
        
        return executable
    
    def execute_sync(self, flow: Flow, input_data: Dict[str, Any]) -> FlowExecution:
        """Execute flow synchronously"""
        return asyncio.run(self.execute_async(flow, input_data))
    
    async def execute_async(self, flow: Flow, input_data: Dict[str, Any]) -> FlowExecution:
        """Execute flow asynchronously with parallel nodes"""
        execution = FlowExecution(flow.flow_id, flow.name, input_data)
        execution.start()
        
        state = execution.state
        for key, value in input_data.items():
            state.set(key, value)
        
        print(f"\n🚀 Parallel Execution: {flow.name}")
        
        dependencies = self._build_dependency_graph(flow)
        completed: Set[str] = set()
        running: Set[str] = set()
        node_config_map = {n["id"]: n for n in flow.node_configs}
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            while len(completed) < len(flow.node_configs):
                executable = self._get_executable_nodes(dependencies, completed, running)
                
                if not executable:
                    if not running:
                        break
                    await asyncio.sleep(0.1)
                    continue
                
                futures = []
                for node_id in executable:
                    running.add(node_id)
                    node_config = node_config_map[node_id]
                    
                    future = executor.submit(
                        self._execute_node,
                        node_id,
                        node_config,
                        state
                    )
                    futures.append((node_id, future))
                
                for node_id, future in futures:
                    try:
                        result = future.result(timeout=30)
                        execution.node_results[node_id] = result
                        completed.add(node_id)
                        running.discard(node_id)
                        
                        if result.is_failed():
                            execution.fail(f"Node {node_id} failed")
                            return execution
                        else:
                            print(f"   ✅ {node_id} completed")
                    except Exception as e:
                        execution.fail(f"Node {node_id} error: {str(e)}")
                        return execution
        
        execution.complete()
        print(f"\n✅ Parallel execution completed!")
        
        return execution
    
    def _execute_node(self, node_id: str, node_config: Dict, state: State):
        """Execute a single node"""
        node_type = node_config["type"]
        config = node_config.get("config", {})
        
        try:
            if node_type not in self.node_types:
                return NodeResult.failure(f"Unknown node type: {node_type}")
            
            node_class = self.node_types[node_type]
            node = node_class(node_id, config)
            
            return node.execute(state)
        
        except Exception as e:
            return NodeResult.failure(f"Execution error: {str(e)}")


if __name__ == "__main__":
    print("Testing Parallel Flow Engine...\n")
    
    from core import Flow
    import time
    
    flow = Flow(
        flow_id="test",
        name="Test",
        nodes=[
            {"id": "n1", "type": "transform", "config": {"operation": "uppercase", "input_key": "text", "output_key": "out"}},
            {"id": "n2", "type": "delay", "config": {"seconds": 0.3, "input_key": "out", "output_key": "r1"}},
            {"id": "n3", "type": "delay", "config": {"seconds": 0.3, "input_key": "out", "output_key": "r2"}},
        ],
        edges=[
            {"from": "n1", "to": "n2"},
            {"from": "n1", "to": "n3"}
        ]
    )
    
    engine = ParallelFlowEngine(max_workers=2)
    start = time.time()
    execution = engine.execute_sync(flow, {"text": "hello"})
    duration = time.time() - start
    
    print(f"\n✅ Duration: {duration:.2f}s")
    print(f"   Status: {execution.status}")
