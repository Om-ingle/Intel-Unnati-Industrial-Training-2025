import json
import os
import sys
import time
import logging
from pathlib import Path
from typing import Dict, Any

# Add root directory to path so we can import core and orchestrator
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from kafka import KafkaConsumer
    KAFKA_AVAILABLE = True
except ImportError:
    KAFKA_AVAILABLE = False

from orchestrator.executor import WorkflowExecutor
from infrastructure.messaging.kafka_service import KafkaService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("Worker")

class AgentWorker:
    """
    Distributed Worker that listens for Agent execution jobs.
    """
    
    def __init__(self, bootstrap_servers: str = 'localhost:29092'):
        self.bootstrap_servers = bootstrap_servers
        self.jobs_topic = 'agent_jobs'
        self.results_topic = 'agent_job_results'
        
        # We need a producer to send back results
        self.result_producer = KafkaService(bootstrap_servers)
        
        if not KAFKA_AVAILABLE:
            logger.error("kafka-python not installed. Worker cannot start.")
            sys.exit(1)
            
    def start(self):
        """Start the worker loop"""
        logger.info(f"🚀 Worker starting. Connecting to {self.bootstrap_servers}...")
        logger.info(f"📥 Listening on topic: {self.jobs_topic}")
        
        try:
            consumer = KafkaConsumer(
                self.jobs_topic,
                bootstrap_servers=self.bootstrap_servers,
                auto_offset_reset='latest',
                enable_auto_commit=True,
                group_id='agent_worker_group',
                value_deserializer=lambda x: json.loads(x.decode('utf-8'))
            )
        except Exception as e:
            logger.error(f"Failed to create consumer: {e}")
            return

        logger.info("✅ Worker connected and ready for jobs!")

        for message in consumer:
            # KafkaService wraps data in {"type":..., "payload":...}
            # We need to unwrap it
            event = message.value
            if event.get('type') == 'JOB_REQUEST':
                payload = event.get('payload', {})
                self._process_job(payload)
            else:
                logger.warning(f"Ignoring unknown event type: {event.get('type')}")
            
    def _process_job(self, job_data: Dict[str, Any]):
        """Execute a single job"""
        job_id = job_data.get('job_id')
        flow_file = job_data.get('flow_file')
        inputs = job_data.get('input', {})
        
        logger.info(f"⚙️ Processing Job {job_id}: Flow={flow_file}")
        
        # Initialize executor
        executor = WorkflowExecutor()
        
        try:
            # Determine path to flow file (assume it's in examples/workflows if not absolute)
            if not os.path.isabs(flow_file):
                # We are in framework_prototype/worker.py
                # Examples are in framework_prototype/examples
                base_path = Path(__file__).parent / "examples" / "workflows"
                flow_path = base_path / flow_file
            else:
                flow_path = Path(flow_file)
                
            if not flow_path.exists():
                raise FileNotFoundError(f"Flow file not found: {flow_path}")

            # Execute
            execution = executor.execute_flow_file(str(flow_path), inputs)
            
            # Prepare Result
            result_data = {
                "job_id": job_id,
                "status": execution.status,
                "execution_id": execution.execution_id,
                "output": execution.state.get_all(), # Send full state or specific output
                "error": execution.error
            }
            
            # Send Result
            self.result_producer.send_event(self.results_topic, "JOB_COMPLETED", result_data)
            logger.info(f"✅ Job {job_id} completed. Result sent.")
            
        except Exception as e:
            logger.error(f"❌ Job {job_id} failed: {e}")
            error_data = {
                "job_id": job_id,
                "status": "failed",
                "error": str(e)
            }
            self.result_producer.send_event(self.results_topic, "JOB_FAILED", error_data)

if __name__ == "__main__":
    worker = AgentWorker()
    worker.start()
