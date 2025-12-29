from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults
import requests
import json
import time

class AgentFrameworkOperator(BaseOperator):
    """
    Airflow Operator to trigger workflows in the Agent Framework via REST API.
    """
    
    @apply_defaults
    def __init__(
        self,
        api_url: str,
        workflow_data: dict = None,
        workflow_file: str = None,
        input_data: dict = None,
        poll_interval: int = 5,
        timeout: int = 3600,
        *args,
        **kwargs
    ):
        """
        :param api_url: Base URL of the Agent API (e.g., http://agent-api:8000)
        :param workflow_data: Dictionary containing workflow definition (YAML string or dict)
        :param workflow_file: Path to workflow file (if using /execute/file endpoint)
        :param input_data: Input parameters for the workflow
        :param poll_interval: Seconds to wait between status checks
        :param timeout: Maximum seconds to wait for completion
        """
        super().__init__(*args, **kwargs)
        self.api_url = api_url.rstrip('/')
        self.workflow_data = workflow_data
        self.workflow_file = workflow_file
        self.input_data = input_data or {}
        self.poll_interval = poll_interval
        self.timeout = timeout

    def execute(self, context):
        self.log.info(f"Triggering Agent Workflow at {self.api_url}")
        
        # 1. Trigger Execution
        execution_id = self._trigger_workflow()
        self.log.info(f"Workflow triggered successfully. Execution ID: {execution_id}")
        
        # 2. Wait for Completion
        final_status = self._wait_for_completion(execution_id)
        
        if final_status == 'completed':
            self.log.info("Workflow completed successfully.")
            return execution_id
        else:
            raise Exception(f"Workflow failed with status: {final_status}")

    def _trigger_workflow(self):
        url = f"{self.api_url}/execute"
        
        if self.workflow_file:
            # If using file endpoint
            url = f"{self.api_url}/execute/file"
            payload = {
                "file_path": self.workflow_file,
                "input_data": self.input_data
            }
        else:
            # Assume YAML content is passed
            # If workflow_data is a dict, convert to likely expected format or just pass as is?
            # API expects ExecuteFlowRequest: { "flow_yaml": str, "input_data": ... }
            flow_yaml = self.workflow_data
            if not isinstance(flow_yaml, str):
                # If user passed dict, dump to yaml? For now assume string needs to be passed for flow_yaml
                # But if it's just the name, maybe we need to fetch it? 
                # The API expects raw YAML string.
                pass
                
            payload = {
                "flow_yaml": flow_yaml,
                "input_data": self.input_data
            }

        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()
            return response.json().get("execution_id")
        except requests.exceptions.RequestException as e:
            self.log.error(f"Failed to trigger workflow: {e}")
            if response is not None:
                self.log.error(f"Response: {response.text}")
            raise

    def _wait_for_completion(self, execution_id):
        url = f"{self.api_url}/executions/{execution_id}"
        start_time = time.time()
        
        while (time.time() - start_time) < self.timeout:
            try:
                response = requests.get(url)
                response.raise_for_status()
                data = response.json()
                status = data.get("status")
                
                self.log.info(f"Workflow Status: {status}")
                
                if status in ['completed', 'failed', 'error']:
                    return status
                
                time.sleep(self.poll_interval)
                
            except requests.exceptions.RequestException as e:
                self.log.warning(f"Failed to fetch status: {e}. Retrying...")
                time.sleep(self.poll_interval)
                
        raise TimeoutError(f"Workflow execution timed out after {self.timeout} seconds")
