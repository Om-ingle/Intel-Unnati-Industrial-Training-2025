"""
End-to-end API test
"""

import time
import subprocess
import requests
from api.client import AgentFrameworkClient


def test_complete_workflow():
    """Test the complete API workflow"""
    
    print("="*60)
    print("END-TO-END API TEST")
    print("="*60)
    
    client = AgentFrameworkClient()
    
    # Test 1: Health check
    print("\n[1/5] Health Check...")
    health = client.health_check()
    assert health["status"] == "healthy"
    print("✅ API is healthy")
    
    # Test 2: Execute simple flow
    print("\n[2/5] Execute Simple Flow...")
    yaml_flow = """
name: "E2E Test Flow"
description: "End-to-end test"
nodes:
  - id: "transform"
    type: "transform"
    config:
      operation: "uppercase"
      input_key: "message"
      output_key: "result"
"""
    
    result = client.execute_flow(yaml_flow, {"message": "hello world"})
    assert result["status"] == "completed"
    print(f"✅ Execution ID: {result['execution_id']}")
    print(f"   Status: {result['status']}")
    
    # Test 3: Retrieve execution
    print("\n[3/5] Retrieve Execution...")
    execution_id = result["execution_id"]
    retrieved = client.get_execution(execution_id)
    assert retrieved["execution_id"] == execution_id
    print(f"✅ Retrieved execution: {retrieved['flow_name']}")
    
    # Test 4: List executions
    print("\n[4/5] List Executions...")
    executions = client.list_executions(limit=10)
    assert len(executions) > 0
    print(f"✅ Found {len(executions)} executions")
    
    # Test 5: Statistics
    print("\n[5/5] Get Statistics...")
    stats = client.get_statistics()
    print(f"✅ Total executions: {stats['total_executions']}")
    print(f"   Success rate: {stats['success_rate']:.1f}%")
    
    print("\n" + "="*60)
    print("✅ ALL TESTS PASSED!")
    print("="*60)


if __name__ == "__main__":
    print("\nMake sure the API server is running!")
    print("Start it with: python3 api/server.py")
    print("\nPress Enter when ready...")
    input()
    
    test_complete_workflow()
