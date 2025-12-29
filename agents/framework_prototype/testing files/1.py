from orchestrator.executor import WorkflowExecutor

executor = WorkflowExecutor()
execution = executor.execute_flow_file(
    "my_workflow.yaml",
    {"name": "world"}
)

print(f"Status: {execution.status}")
print(f"Result: {execution.state.get('summary')}")  # Use 'summary' (output_key), not 'summarize' (node ID)
print(f"\nAll state keys: {list(execution.state.get_all().keys())}")
print(f"Full state: {execution.state.get_all()}")