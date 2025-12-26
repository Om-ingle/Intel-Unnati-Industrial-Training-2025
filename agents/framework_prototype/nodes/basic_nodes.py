"""
Basic node types - Simple operations
"""

import sys
from pathlib import Path
from typing import Dict, Any
import time

# Handle imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from core import Node, State, NodeResult, NodeStatus


class TransformNode(Node):
    """
    Transform data (uppercase, lowercase, etc.)
    
    Config:
        - operation: uppercase, lowercase, passthrough
        - input_key: Key to read from state
        - output_key: Key to write to state
    """
    
    def execute(self, state: State) -> NodeResult:
        operation = self.config.get("operation", "passthrough")
        input_key = self.config.get("input_key", "input")
        output_key = self.config.get("output_key", "output")
        
        input_value = state.get(input_key)
        
        if operation == "uppercase":
            result = str(input_value).upper()
        elif operation == "lowercase":
            result = str(input_value).lower()
        elif operation == "passthrough":
            result = input_value
        else:
            return NodeResult.failure(f"Unknown operation: {operation}")
        
        state.set(output_key, result)
        return NodeResult.success(result)


class DelayNode(Node):
    """
    Delay execution for testing parallel flows
    
    Config:
        - seconds: Delay in seconds
        - input_key: Pass through this value
        - output_key: Where to write output
    """
    
    def execute(self, state: State) -> NodeResult:
        seconds = self.config.get("seconds", 1.0)
        input_key = self.config.get("input_key", "input")
        output_key = self.config.get("output_key", "output")
        
        # Get input
        value = state.get(input_key)
        
        # Delay
        time.sleep(seconds)
        
        # Pass through
        state.set(output_key, value)
        
        return NodeResult.success(
            value,
            metadata={"delay_seconds": seconds}
        )


class OutputNode(Node):
    """
    Output node - formats final output
    
    Config:
        - input_key: Key to output
        - format: json, text
    """
    
    def execute(self, state: State) -> NodeResult:
        import json
        
        input_key = self.config.get("input_key", "result")
        format_type = self.config.get("format", "json")
        
        value = state.get(input_key)
        
        if format_type == "json":
            output = json.dumps(value, indent=2) if not isinstance(value, str) else value
        else:
            output = str(value)
        
        return NodeResult.success(output)


class FilterNode(Node):
    """
    Filter data based on condition
    
    Config:
        - condition: Python expression
        - input_key: Data to filter
        - output_key: Filtered data
    """
    
    def execute(self, state: State) -> NodeResult:
        condition = self.config.get("condition", "True")
        input_key = self.config.get("input_key", "input")
        output_key = self.config.get("output_key", "output")
        
        data = state.get(input_key)
        
        # For now, just pass through
        # In real implementation, filter based on condition
        state.set(output_key, data)
        
        return NodeResult.success(data)


# Registry
BASIC_NODE_TYPES = {
    "transform": TransformNode,
    "delay": DelayNode,
    "output": OutputNode,
    "filter": FilterNode,
}
