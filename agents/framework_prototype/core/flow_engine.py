"""
Flow Engine - Executes workflows
"""

import sys
from pathlib import Path
from typing import Dict, Any

# Handle imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from core.flow import Flow, FlowExecution
from core.state import State


class FlowEngine:
    """
    Basic flow execution engine.
    Executes nodes sequentially.
    """
    
    def __init__(self):
        self.node_types = {}
    
    def register_node_type(self, name: str, node_class):
        """Register a node type"""
        self.node_types[name] = node_class
    
    def execute(self, flow: Flow, input_data: Dict[str, Any]) -> FlowExecution:
        """
        Execute a flow.
        
        Args:
            flow: Flow to execute
            input_data: Input data
        
        Returns:
            FlowExecution with results
        """
        # Create execution
        execution = FlowExecution(flow.flow_id, flow.name, input_data)
        execution.start()
        
        # Initialize state
        state = execution.state
        for key, value in input_data.items():
            state.set(key, value)
        
        # Initialize Kafka Service (Phase 4)
        try:
            from infrastructure.messaging.kafka_service import KafkaService
            kafka = KafkaService()
            kafka_topic = "agent_workflow_events"
        except ImportError:
            kafka = None
            print("⚠️ Could not import KafkaService. Is infrastructure/messaging in path?")

        # Notify Flow Start
        if kafka and kafka.enabled:
            kafka.send_event(kafka_topic, "FLOW_STARTED", {
                "flow_id": flow.flow_id,
                "execution_id": execution.execution_id,
                "input": input_data
            })

        # Execute nodes in topological order (if edges defined) or sequential order
        if flow.execution_order:
            # Use topological sort order
            node_map = {node["id"]: node for node in flow.node_configs}
            execution_order = flow.execution_order
        else:
            # No edges, execute in YAML order
            execution_order = [node["id"] for node in flow.node_configs]
            node_map = {node["id"]: node for node in flow.node_configs}
        
        for node_id in execution_order:
            node_config = node_map[node_id]
            node_type = node_config["type"]
            config = node_config.get("config", {})
            
            try:
                # Get node class
                if node_type not in self.node_types:
                    raise ValueError(f"Unknown node type: {node_type}")
                
                node_class = self.node_types[node_type]
                node = node_class(node_id, config)
                
                # Notify Node Start
                if kafka and kafka.enabled:
                    kafka.send_event(kafka_topic, "NODE_STARTED", {
                        "flow_id": flow.flow_id,
                        "execution_id": execution.execution_id,
                        "node_id": node_id,
                        "node_type": node_type
                    })

                # Execute
                result = node.execute(state)
                execution.node_results[node_id] = result
                
                # Notify Node Complete
                if kafka and kafka.enabled:
                    status = "SUCCESS" if result.is_success() else "FAILED"
                    kafka.send_event(kafka_topic, "NODE_COMPLETED", {
                        "flow_id": flow.flow_id,
                        "execution_id": execution.execution_id,
                        "node_id": node_id,
                        "status": status,
                        "duration": 0  # TODO: Track duration
                    })

                # Check for failure
                if result.is_failed():
                    error_msg = f"Node {node_id} failed: {result.error}"
                    execution.fail(error_msg)
                    
                    if kafka and kafka.enabled:
                        kafka.send_event(kafka_topic, "FLOW_FAILED", {
                            "flow_id": flow.flow_id,
                            "execution_id": execution.execution_id,
                            "error": error_msg
                        })
                    return execution
            
            except Exception as e:
                error_msg = f"Node {node_id} error: {str(e)}"
                execution.fail(error_msg)
                
                if kafka and kafka.enabled:
                        kafka.send_event(kafka_topic, "FLOW_FAILED", {
                            "flow_id": flow.flow_id,
                            "execution_id": execution.execution_id,
                            "error": error_msg
                        })
                return execution
        
        # Complete
        execution.complete()
        
        if kafka and kafka.enabled:
            kafka.send_event(kafka_topic, "FLOW_COMPLETED", {
                "flow_id": flow.flow_id,
                "execution_id": execution.execution_id,
                "final_state": state.get_all() # Warning: could be large
            })
            kafka.close()
            
        return execution


if __name__ == "__main__":
    print("✅ FlowEngine module loaded")
