"""
Flow Parser - Read and validate YAML workflow definitions
"""

import sys
from pathlib import Path
from typing import Dict, Any, Optional, List
import yaml
import json

# Handle imports
try:
    from ..core import Flow
except ImportError:
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from core import Flow

import jsonschema


# ============================================================================
# FLOW SCHEMA DEFINITION
# ============================================================================

FLOW_SCHEMA = {
    "type": "object",
    "required": ["name", "nodes"],
    "properties": {
        "name": {"type": "string"},
        "description": {"type": "string"},
        "nodes": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["id", "type"],
                "properties": {
                    "id": {"type": "string"},
                    "type": {"type": "string"},
                    "config": {"type": "object"},
                    "timeout": {"type": "number"},
                    "retries": {"type": "number"}
                }
            }
        },
        "edges": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["from", "to"],
                "properties": {
                    "from": {"type": "string"},
                    "to": {"type": "string"},
                    "condition": {"type": "string"}
                }
            }
        },
        "input": {"type": "object"},
        "config": {"type": "object"}
    }
}


# ============================================================================
# FLOW PARSER
# ============================================================================

class FlowParser:
    """
    Parse and validate YAML workflow definitions.
    
    Example YAML:
        name: "My Workflow"
        description: "Does something cool"
        nodes:
          - id: "step1"
            type: "llm_call"
            config:
              prompt: "Hello {input}"
        edges:
          - from: "step1"
            to: "step2"
    """
    
    def __init__(self):
        self.schema = FLOW_SCHEMA
    
    def parse_file(self, file_path: str) -> Flow:
        """
        Parse a YAML file into a Flow object.
        
        Args:
            file_path: Path to YAML file
        
        Returns:
            Flow object
        
        Raises:
            ValueError: If file is invalid
        """
        try:
            with open(file_path, 'r') as f:
                data = yaml.safe_load(f)
            
            return self.parse_dict(data)
            
        except FileNotFoundError:
            raise ValueError(f"Flow file not found: {file_path}")
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML: {str(e)}")
    
    def parse_dict(self, data: Dict[str, Any]) -> Flow:
        """
        Parse a dictionary into a Flow object.
        
        Args:
            data: Flow definition as dictionary
        
        Returns:
            Flow object
        
        Raises:
            ValueError: If data is invalid
        """
        # Validate against schema
        try:
            jsonschema.validate(instance=data, schema=self.schema)
        except jsonschema.ValidationError as e:
            raise ValueError(f"Invalid flow definition: {e.message}")
        
        # Generate flow ID if not provided
        flow_id = data.get("flow_id", self._generate_flow_id(data["name"]))
        
        # Create Flow object
        flow = Flow(
            flow_id=flow_id,
            name=data["name"],
            description=data.get("description", ""),
            nodes=data["nodes"],
            edges=data.get("edges", [])
        )
        
        return flow
    
    def parse_yaml(self, yaml_str: str) -> Flow:
        """
        Parse a YAML string into a Flow object.
        
        Args:
            yaml_str: YAML string
        
        Returns:
            Flow object
        """
        try:
            data = yaml.safe_load(yaml_str)
            return self.parse_dict(data)
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML: {str(e)}")
    
    def _generate_flow_id(self, name: str) -> str:
        """Generate flow ID from name"""
        import re
        import uuid
        # Clean name and add UUID suffix
        clean_name = re.sub(r'[^a-z0-9]+', '-', name.lower()).strip('-')
        return f"{clean_name}-{str(uuid.uuid4())[:8]}"
    
    def validate_flow(self, flow: Flow) -> List[str]:
        """
        Validate a flow for common issues.
        
        Args:
            flow: Flow to validate
        
        Returns:
            List of validation warnings (empty if valid)
        """
        warnings = []
        
        # Check for duplicate node IDs
        node_ids = [n["id"] for n in flow.node_configs]
        if len(node_ids) != len(set(node_ids)):
            warnings.append("Duplicate node IDs found")
        
        # Check edge references
        for edge in flow.edges:
            if edge["from"] not in node_ids:
                warnings.append(f"Edge references non-existent node: {edge['from']}")
            if edge["to"] not in node_ids:
                warnings.append(f"Edge references non-existent node: {edge['to']}")
        
        # Check for unreachable nodes (if edges exist)
        if flow.edges:
            reachable = set()
            if flow.execution_order:
                reachable.add(flow.execution_order[0])
            
            for edge in flow.edges:
                if edge["from"] in reachable:
                    reachable.add(edge["to"])
            
            unreachable = set(node_ids) - reachable
            if unreachable:
                warnings.append(f"Unreachable nodes: {', '.join(unreachable)}")
        
        return warnings


# ============================================================================
# TESTING
# ============================================================================

if __name__ == "__main__":
    print("Testing Flow Parser...\n")
    
    # Test 1: Parse from dictionary
    print("[1/3] Testing dictionary parsing...")
    
    flow_dict = {
        "name": "Test Flow",
        "description": "A test workflow",
        "nodes": [
            {
                "id": "search",
                "type": "web_search",
                "config": {
                    "query": "{topic}",
                    "max_results": 3
                }
            },
            {
                "id": "summarize",
                "type": "llm_call",
                "config": {
                    "prompt": "Summarize: {search}"
                }
            }
        ],
        "edges": [
            {"from": "search", "to": "summarize"}
        ]
    }
    
    parser = FlowParser()
    flow = parser.parse_dict(flow_dict)
    
    print(f"✅ Parsed flow: {flow.name}")
    print(f"   Flow ID: {flow.flow_id}")
    print(f"   Nodes: {len(flow.node_configs)}")
    print(f"   Edges: {len(flow.edges)}")
    
    # Test 2: Validate flow
    print("\n[2/3] Testing flow validation...")
    warnings = parser.validate_flow(flow)
    if warnings:
        print(f"⚠️  Warnings: {warnings}")
    else:
        print("✅ Flow is valid")
    
    # Test 3: Parse YAML string
    print("\n[3/3] Testing YAML string parsing...")
    
    yaml_str = """
name: "YAML Test Flow"
description: "Testing YAML parsing"
nodes:
  - id: "step1"
    type: "transform"
    config:
      operation: "uppercase"
      input_key: "input"
      output_key: "output"
  - id: "step2"
    type: "output"
    config:
      input_key: "output"
      format: "text"
edges:
  - from: "step1"
    to: "step2"
"""
    
    flow2 = parser.parse_yaml(yaml_str)
    print(f"✅ Parsed YAML flow: {flow2.name}")
    print(f"   Nodes: {flow2.execution_order}")
    
    print("\n✅ Flow Parser is working correctly!")
