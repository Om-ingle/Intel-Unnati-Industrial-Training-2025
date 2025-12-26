"""
REST API Server - HTTP interface for the agent framework
"""

import sys
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
import uvicorn
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import yaml

# Handle imports
try:
    from ..orchestrator.executor import WorkflowExecutor
    from ..orchestrator.flow_parser import FlowParser
except ImportError:
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from orchestrator.executor import WorkflowExecutor
    from orchestrator.flow_parser import FlowParser


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class ExecuteFlowRequest(BaseModel):
    """Request to execute a flow"""
    flow_yaml: str
    input_data: Dict[str, Any]
    
    class Config:
        json_schema_extra = {
            "example": {
                "flow_yaml": "name: Test\nnodes:\n  - id: step1\n    type: llm_call",
                "input_data": {"query": "Hello"}
            }
        }


class ExecuteFlowFileRequest(BaseModel):
    """Request to execute a flow from file"""
    file_path: str
    input_data: Dict[str, Any]


class ExecutionResponse(BaseModel):
    """Execution result response"""
    execution_id: str
    flow_id: str
    flow_name: str
    status: str
    duration_seconds: Optional[float]
    input_data: Dict[str, Any]
    final_state: Dict[str, Any]
    node_results: Dict[str, Any]
    error: Optional[str] = None


class ExecutionListResponse(BaseModel):
    """List of executions"""
    executions: list
    total: int


class StatisticsResponse(BaseModel):
    """Statistics response"""
    total_executions: int
    completed: int
    failed: int
    success_rate: float


# ============================================================================
# API APPLICATION
# ============================================================================

app = FastAPI(
    title="AI Agent Framework API",
    description="REST API for orchestrating agentic workflows",
    version="1.0.0"
)

# Initialize executor
executor = WorkflowExecutor()


# ============================================================================
# HEALTH & INFO ENDPOINTS
# ============================================================================

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "AI Agent Framework API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "health": "/health",
            "docs": "/docs",
            "execute": "/execute",
            "executions": "/executions",
            "statistics": "/statistics"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "database": "connected"
    }


# ============================================================================
# EXECUTION ENDPOINTS
# ============================================================================

@app.post("/execute", response_model=ExecutionResponse)
async def execute_flow(request: ExecuteFlowRequest):
    """
    Execute a workflow from YAML string.
    
    Args:
        request: Flow YAML and input data
    
    Returns:
        Execution results
    """
    try:
        # Execute flow
        execution = executor.execute_flow_yaml(
            request.flow_yaml,
            request.input_data
        )
        
        # Build response
        return ExecutionResponse(
            execution_id=execution.execution_id,
            flow_id=execution.flow_id,
            flow_name=execution.flow_name,
            status=execution.status,
            duration_seconds=execution.get_duration(),
            input_data=execution.input_data,
            final_state=execution.state.get_all(),
            node_results={
                node_id: {
                    "status": result.status.value,
                    "output": result.output,
                    "error": result.error,
                    "timestamp": result.timestamp.isoformat()
                }
                for node_id, result in execution.node_results.items()
            },
            error=execution.error
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Execution failed: {str(e)}")


@app.post("/execute/file", response_model=ExecutionResponse)
async def execute_flow_file(request: ExecuteFlowFileRequest):
    """
    Execute a workflow from YAML file.
    
    Args:
        request: File path and input data
    
    Returns:
        Execution results
    """
    try:
        execution = executor.execute_flow_file(
            request.file_path,
            request.input_data
        )
        
        return ExecutionResponse(
            execution_id=execution.execution_id,
            flow_id=execution.flow_id,
            flow_name=execution.flow_name,
            status=execution.status,
            duration_seconds=execution.get_duration(),
            input_data=execution.input_data,
            final_state=execution.state.get_all(),
            node_results={
                node_id: {
                    "status": result.status.value,
                    "output": result.output,
                    "error": result.error
                }
                for node_id, result in execution.node_results.items()
            },
            error=execution.error
        )
        
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Flow file not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/execute/upload")
async def execute_flow_upload(
    file: UploadFile = File(...),
    input_data: str = "{}"
):
    """
    Upload and execute a YAML workflow file.
    
    Args:
        file: YAML file
        input_data: JSON string of input data
    
    Returns:
        Execution results
    """
    try:
        import json
        
        # Read file
        content = await file.read()
        yaml_str = content.decode('utf-8')
        
        # Parse input data
        input_dict = json.loads(input_data)
        
        # Execute
        execution = executor.execute_flow_yaml(yaml_str, input_dict)
        
        return {
            "execution_id": execution.execution_id,
            "status": execution.status,
            "flow_name": execution.flow_name,
            "message": "Flow executed successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# QUERY ENDPOINTS
# ============================================================================

@app.get("/executions/{execution_id}")
async def get_execution(execution_id: str):
    """
    Get execution details by ID.
    
    Args:
        execution_id: Execution ID
    
    Returns:
        Execution details
    """
    execution = executor.get_execution(execution_id)
    
    if not execution:
        raise HTTPException(status_code=404, detail="Execution not found")
    
    return execution


@app.get("/executions", response_model=ExecutionListResponse)
async def list_executions(
    flow_id: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 100
):
    """
    List executions with optional filters.
    
    Args:
        flow_id: Filter by flow ID
        status: Filter by status
        limit: Maximum results
    
    Returns:
        List of executions
    """
    executions = executor.list_executions(
        flow_id=flow_id,
        status=status,
        limit=limit
    )
    
    return ExecutionListResponse(
        executions=executions,
        total=len(executions)
    )


@app.get("/statistics", response_model=StatisticsResponse)
async def get_statistics():
    """
    Get execution statistics.
    
    Returns:
        Statistics summary
    """
    stats = executor.get_statistics()
    return StatisticsResponse(**stats)


# ============================================================================
# VALIDATION ENDPOINTS
# ============================================================================

@app.post("/validate")
async def validate_flow(flow_yaml: str):
    """
    Validate a flow without executing it.
    
    Args:
        flow_yaml: YAML flow definition
    
    Returns:
        Validation results
    """
    try:
        parser = FlowParser()
        flow = parser.parse_yaml(flow_yaml)
        warnings = parser.validate_flow(flow)
        
        return {
            "valid": len(warnings) == 0,
            "flow_name": flow.name,
            "node_count": len(flow.node_configs),
            "edge_count": len(flow.edges),
            "warnings": warnings
        }
        
    except Exception as e:
        return {
            "valid": False,
            "error": str(e)
        }


# ============================================================================
# SERVER STARTUP
# ============================================================================

def start_server(host: str = "0.0.0.0", port: int = 8000):
    """
    Start the API server.
    
    Args:
        host: Host address
        port: Port number
    """
    print(f"""
╔══════════════════════════════════════════════════════════════╗
║          AI Agent Framework API Server                        ║
╚══════════════════════════════════════════════════════════════╝

🚀 Server starting...
   Host: {host}
   Port: {port}
   Docs: http://{host}:{port}/docs
   
Ready to orchestrate agentic workflows! 🤖
    """)
    
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    start_server()
