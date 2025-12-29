import sys
from pathlib import Path
import time
import json
import uuid

# Add root directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from infrastructure.messaging.kafka_service import KafkaService

def send_test_job():
    print("="*60)
    print("TEST: Sending Job to Worker")
    print("="*60)
    
    # Initialize Producer
    kafka = KafkaService(bootstrap_servers='localhost:29092')
    if not kafka.enabled:
        print("[X] Could not connect to Kafka.")
        return

    # Create Job Data
    job_id = str(uuid.uuid4())
    job_data = {
        "job_id": job_id,
        "flow_type": "yaml_file",
        # We use a simple flow that exists in examples/workflows
        # Make sure 'my_workflow.yaml' or similar exists. 
        # I moved 'my_workflow.yaml' earlier, but let's use a virtual one or simpler one if possible.
        # The worker logic expects a file path.
        # Let's create a temporary strict test file.
        "flow_file": "simple_kafka_test.yaml", 
        "input": {"msg": "Hello Kafka World!"}
    }
    
    print(f"\n[Step 1] Sending Job {job_id}...")
    kafka.send_event('agent_jobs', 'JOB_REQUEST', job_data)
    print("✅ Job sent!")
    print("\n[Step 2] Now check the 'worker' terminal window for activity.")
    print("        You should see 'Processing Job...'")
    
    kafka.close()

if __name__ == "__main__":
    send_test_job()
