import sys
from pathlib import Path
import time
import json

# Add root directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from orchestrator.executor import WorkflowExecutor
from infrastructure.messaging.kafka_service import KafkaService

def test_kafka_events():
    """
    Run a simple flow and manually check if Kafka Service initializes.
    Note: To fully verify, we'd need to run a consumer in parallel.
    For now, we rely on the logs from KafkaService.
    """
    print("="*60)
    print("TEST: Kafka Event Emission")
    print("="*60)
    
    # 1. Initialize Kafka to see if it connects
    print("\n[Step 1] Testing Connection...")
    kafka = KafkaService()
    if not kafka.enabled:
        print("[X] Could not connect to Kafka. Is Docker running?")
        print("Run: docker compose up -d")
        return
    else:
        print("[OK] Kafka Connection Successful")
        kafka.close()

    # 2. Run a simple workflow
    print("\n[Step 2] Execution Flow...")
    executor = WorkflowExecutor()
    
    simple_flow = """
name: "Kafka Test Flow"
nodes:
  - id: "hello"
    type: "transform"
    config:
      operation: "passthrough"
      input_key: "msg"
      output_key: "out"
"""
    
    print("Running flow... (Watch for Kafka logs)")
    execution = executor.execute_flow_yaml(simple_flow, {"msg": "kafka_check"})
    
    print(f"\n[OK] Execution Status: {execution.status}")
    print("="*60)
    print("If you verified the 'Connected to Kafka' log above, integration is working.")

if __name__ == "__main__":
    test_kafka_events()
