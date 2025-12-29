import json
import time
import logging
from typing import Dict, Any, Optional
try:
    from kafka import KafkaProducer
    from kafka.errors import KafkaError
    KAFKA_AVAILABLE = True
except ImportError:
    KAFKA_AVAILABLE = False

logger = logging.getLogger(__name__)

class KafkaService:
    """
    Wrapper for Apache Kafka Producer to send workflow events.
    Handles connection errors gracefully so the agent doesn't crash if Kafka is down.
    """
    
    def __init__(self, bootstrap_servers: str = 'localhost:29092'):
        self.producer = None
        self.enabled = False
        
        if not KAFKA_AVAILABLE:
            logger.warning("⚠️ kafka-python not installed. Kafka integration disabled.")
            return

        try:
            self.producer = KafkaProducer(
                bootstrap_servers=bootstrap_servers,
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                # Reduce timeout so we don't block main thread too long if Kafka is down
                request_timeout_ms=2000,
                api_version_auto_timeout_ms=2000
            )
            self.enabled = True
            logger.info(f"✅ Connected to Kafka at {bootstrap_servers}")
        except Exception as e:
            logger.error(f"❌ Failed to connect to Kafka: {e}")
            self.enabled = False

    def send_event(self, topic: str, event_type: str, data: Dict[str, Any]):
        """
        Send a standardized event to Kafka.
        """
        if not self.enabled or not self.producer:
            return

        message = {
            "type": event_type,
            "timestamp": time.time(),
            "payload": data
        }

        try:
            future = self.producer.send(topic, message)
            # Fire and forget - don't wait for result to keep execution fast
        except Exception as e:
            logger.error(f"Failed to send Kafka event: {e}")

    def close(self):
        if self.producer:
            self.producer.close()
