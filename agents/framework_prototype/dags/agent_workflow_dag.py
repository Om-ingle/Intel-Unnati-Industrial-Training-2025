from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import sys
import os

# Add plugins folder to path so we can import the operator
# (If mapped correctly in docker-compose, this might be auto-discoverable, but explicit import helps)
sys.path.append('/opt/airflow/plugins')

try:
    from agent_framework_plugin import AgentFrameworkOperator
except ImportError:
    # Fallback to verify logic if plugin not found yet
    AgentFrameworkOperator = None
    print("AgentFrameworkOperator plugin not found. Make sure plugins are mounted.")

default_args = {
    'owner': 'cortex_agent',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email_on_failure': False,
    'retries': 0,
}

# Define the YAML flow inline for testing
SIMPLE_FLOW_YAML = """
name: "Scheduled Airflow Task"
nodes:
  - id: "scheduler_greet"
    type: "transform"
    config:
      operation: "passthrough"
      input_key: "msg"
      output_key: "result"
  
  - id: "log_output"
    type: "output"
    config:
      input_key: "result"
      format: "text"

edges:
  - from: "scheduler_greet"
    to: "log_output"
"""

with DAG(
    '02_agent_schedule_demo',
    default_args=default_args,
    description='Triggers an Agent Workflow via API',
    schedule_interval=None, # Manual trigger for now
    catchup=False,
    tags=['agent', 'integration']
) as dag:

    start_task = PythonOperator(
        task_id='start_check',
        python_callable=lambda: print("Starting Agent Workflow Trigger...")
    )

    if AgentFrameworkOperator:
        trigger_agent = AgentFrameworkOperator(
            task_id='trigger_simple_flow',
            api_url='http://agent-api:8000',
            workflow_data=SIMPLE_FLOW_YAML,
            input_data={"msg": "Hello from Airflow!"},
            poll_interval=2
        )
        
        start_task >> trigger_agent
    else:
        print("Skipping AgentFrameworkOperator task due to import error")
