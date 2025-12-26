"""
API Client - Python client for the agent framework API
"""

import requests
from typing import Dict, Any, Optional, List


class AgentFrameworkClient:
    """
    Python client for AI Agent Framework API.
    
    Example:
        client = AgentFrameworkClient("http://localhost:8000")
        result = client.execute_flow(yaml_str, {"input": "data"})
    """
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        """
        Initialize client.
        
        Args:
            base_url: Base URL of API server
        """
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
    
    def health_check(self) -> Dict[str, Any]:
        """Check API health"""
        response = self.session.get(f"{self.base_url}/health")
        response.raise_for_status()
        return response.json()
    
    def execute_flow(
        self,
        flow_yaml: str,
        input_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute a workflow.
        
        Args:
            flow_yaml: YAML flow definition
            input_data: Input data
        
        Returns:
            Execution results
        """
        response = self.session.post(
            f"{self.base_url}/execute",
            json={
                "flow_yaml": flow_yaml,
                "input_data": input_data
            }
        )
        response.raise_for_status()
        return response.json()
    
    def execute_flow_file(
        self,
        file_path: str,
        input_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute a workflow from file.
        
        Args:
            file_path: Path to YAML file
            input_data: Input data
        
        Returns:
            Execution results
        """
        response = self.session.post(
            f"{self.base_url}/execute/file",
            json={
                "file_path": file_path,
                "input_data": input_data
            }
        )
        response.raise_for_status()
        return response.json()
    
    def get_execution(self, execution_id: str) -> Dict[str, Any]:
        """Get execution by ID"""
        response = self.session.get(
            f"{self.base_url}/executions/{execution_id}"
        )
        response.raise_for_status()
        return response.json()
    
    def list_executions(
        self,
        flow_id: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """List executions"""
        params = {"limit": limit}
        if flow_id:
            params["flow_id"] = flow_id
        if status:
            params["status"] = status
        
        response = self.session.get(
            f"{self.base_url}/executions",
            params=params
        )
        response.raise_for_status()
        return response.json()["executions"]
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get execution statistics"""
        response = self.session.get(f"{self.base_url}/statistics")
        response.raise_for_status()
        return response.json()
    
    def validate_flow(self, flow_yaml: str) -> Dict[str, Any]:
        """Validate a flow"""
        response = self.session.post(
            f"{self.base_url}/validate",
            params={"flow_yaml": flow_yaml}
        )
        response.raise_for_status()
        return response.json()


# ============================================================================
# CLI TESTING
# ============================================================================

if __name__ == "__main__":
    print("Testing API Client...\n")
    
    client = AgentFrameworkClient()
    
    # Test health
    print("[1/2] Testing health check...")
    try:
        health = client.health_check()
        print(f"✅ API Status: {health['status']}")
    except:
        print("❌ API server not running. Start it with: python3 api/server.py")
        exit(1)
    
    # Test execution
    print("\n[2/2] Testing flow execution...")
    yaml_flow = """
name: "API Test Flow"
nodes:
  - id: "test"
    type: "transform"
    config:
      operation: "uppercase"
      input_key: "input"
      output_key: "output"
"""
    
    result = client.execute_flow(yaml_flow, {"input": "hello"})
    print(f"✅ Execution ID: {result['execution_id']}")
    print(f"   Status: {result['status']}")
    
    print("\n✅ API Client is working!")
