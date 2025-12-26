"""
Workflow Executor - High-level orchestration
"""

import sys
from pathlib import Path
import yaml

# Handle imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from core import FlowEngine, Flow, FlowExecution
from nodes import ALL_NODE_TYPES


class WorkflowExecutor:
    """High-level workflow executor"""
    
    def __init__(self):
        self.engine = FlowEngine()
        
        # Register all node types
        for name, node_class in ALL_NODE_TYPES.items():
            self.engine.register_node_type(name, node_class)
    
    def execute_flow(self, flow: Flow, input_data: dict) -> FlowExecution:
        """Execute a flow"""
        return self.engine.execute(flow, input_data)
    
    def execute_flow_yaml(self, yaml_str: str, input_data: dict) -> FlowExecution:
        """Execute flow from YAML string"""
        flow_dict = yaml.safe_load(yaml_str)
        
        flow = Flow(
            flow_id=flow_dict.get("flow_id", "yaml-flow"),
            name=flow_dict["name"],
            description=flow_dict.get("description", ""),
            nodes=flow_dict.get("nodes", []),
            edges=flow_dict.get("edges", [])
        )
        
        return self.execute_flow(flow, input_data)
    
    def execute_flow_file(self, file_path: str, input_data: dict) -> FlowExecution:
        """Execute flow from YAML file"""
        with open(file_path, 'r') as f:
            yaml_str = f.read()
        
        return self.execute_flow_yaml(yaml_str, input_data)
    
    def get_execution(self, execution_id: str):
        """Get execution by ID (stub)"""
        return None
    
    def list_executions(self, **kwargs):
        """List executions (stub)"""
        return []
    
    def get_statistics(self):
        """Get statistics (stub)"""
        return {
            "total_executions": 0,
            "completed": 0,
            "failed": 0,
            "success_rate": 0.0
        }


if __name__ == "__main__":
    print("✅ WorkflowExecutor module loaded")
