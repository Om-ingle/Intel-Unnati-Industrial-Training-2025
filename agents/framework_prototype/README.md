# AI Agent Framework

## 🎯 Overview

A lightweight, extensible AI agent orchestration framework for defining, executing, and monitoring agentic workflows. Built with simplicity and observability in mind, this framework allows developers to create complex multi-step agent workflows without heavy dependencies on existing platforms.

---

## 🏗️ Architecture

```
┌─────────────┐
│   Input     │ (REST API / CLI)
└──────┬──────┘
       │
┌──────▼──────────────────────────┐
│   Flow Orchestrator             │
│  (State Machine Engine)         │
└──────┬──────────────────────────┘
       │
┌──────▼──────┬──────────┬────────┐
│   Node      │  Node    │  Node  │ (Agent Tasks)
│  Executor   │ Executor │Executor│
└──────┬──────┴──────┬───┴────┬───┘
       │             │        │
┌──────▼─────────────▼────────▼───┐
│      Shared State / Memory      │
└──────┬──────────────────────────┘
       │
┌──────▼──────┬───────────────────┐
│  Storage    │   Observability   │
│  (SQLite)   │   (Logs/Metrics)  │
└─────────────┴───────────────────┘
```

---

## ✨ Features

### Core Capabilities
- **Flow Definition**: Define workflows using YAML/JSON configuration
- **State Machine Execution**: Execute nodes sequentially, conditionally, or in parallel
- **Built-in Tools**: Pre-built integrations for LLM calls, web search, data transformation
- **Shared Memory**: Persistent state management across workflow nodes
- **Guardrails**: Built-in timeout, retry, and error handling mechanisms
- **Observability**: Comprehensive logging, metrics, and execution tracking
- **Visual Interface**: Interactive flow designer and real-time execution monitor
- **REST API**: Full programmatic access to framework capabilities

### Advanced Features
- **Custom Tool Integration**: Plugin system for adding custom tools and actions
- **Conditional Routing**: Dynamic workflow paths based on node outputs
- **Error Recovery**: Automatic retries and fallback mechanisms
- **Audit Trail**: Complete execution history and state snapshots
- **Extensible Architecture**: Modular design for easy customization

---

## 📁 Project Structure

```
agents/framework_prototype/
├── README.md
├── requirements.txt
├── setup.py
│
├── core/                       # Framework Core
│   ├── __init__.py
│   ├── flow_engine.py         # State machine executor
│   ├── node.py                # Base node/agent class
│   ├── state.py               # Shared state management
│   ├── tools.py               # Built-in tool library
│   └── guardrails.py          # Retry/timeout/error handling
│
├── orchestrator/              # Orchestration Layer
│   ├── __init__.py
│   ├── api.py                 # FastAPI REST endpoints
│   ├── executor.py            # Flow execution manager
│   └── flow_parser.py         # YAML/JSON parser
│
├── storage/                   # Persistence Layer
│   ├── __init__.py
│   ├── sqlite_backend.py      # SQLite implementation
│   └── models.py              # Data models
│
├── ui/                        # Visualization Layer
│   ├── index.html             # Flow designer UI
│   └── assets/                # UI resources
│
├── examples/                  # Reference Implementations
│   ├── flows/
│   │   ├── research_agent.yaml
│   │   └── data_pipeline.yaml
│   └── custom_tools/
│       └── example_tool.py
│
├── tests/                     # Test Suite
│   ├── test_core.py
│   ├── test_orchestrator.py
│   └── test_integration.py
│
└── docs/                      # Documentation
    ├── architecture.md
    ├── api_reference.md
    ├── flow_definition.md
    └── custom_tools.md
```

---

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd agents/framework_prototype

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Running Your First Agent

#### 1. Define a Flow (YAML)

```yaml
# examples/flows/hello_agent.yaml
name: "Hello Agent"
description: "Simple greeting agent"

nodes:
  - id: "greet"
    type: "llm_call"
    config:
      prompt: "Generate a friendly greeting for {user_name}"
      model: "llama-3.1-70b-versatile"
    
  - id: "output"
    type: "output"
    config:
      format: "json"

edges:
  - from: "greet"
    to: "output"

input:
  user_name: "string"
```

#### 2. Execute via CLI

```bash
python -m orchestrator.cli execute examples/flows/hello_agent.yaml --input '{"user_name": "Alice"}'
```

#### 3. Execute via API

```bash
# Start the server
python -m orchestrator.api

# Execute flow
curl -X POST http://localhost:8000/flows/execute \
  -H "Content-Type: application/json" \
  -d '{
    "flow_file": "examples/flows/hello_agent.yaml",
    "input": {"user_name": "Alice"}
  }'
```

#### 4. Visual Interface

```bash
# Start the web UI
python -m orchestrator.api

# Open browser
open http://localhost:8000/ui
```

---

## 📖 Flow Definition

### Basic Structure

```yaml
name: "Flow Name"
description: "Flow description"

# Define workflow nodes
nodes:
  - id: "unique_node_id"
    type: "node_type"  # llm_call, web_search, transform, condition, output
    config:
      # Node-specific configuration
    timeout: 30  # Optional: node timeout in seconds
    retries: 3   # Optional: retry attempts

# Define connections between nodes
edges:
  - from: "node_id_1"
    to: "node_id_2"
    condition: "optional_condition"  # For conditional routing

# Define expected inputs
input:
  param_name: "type"

# Optional: Global configuration
config:
  max_execution_time: 300
  error_handling: "continue"  # or "stop"
```

### Available Node Types

| Node Type | Description | Example Use Case |
|-----------|-------------|------------------|
| `llm_call` | Call LLM with prompt | Text generation, summarization |
| `web_search` | Search the web | Research, fact-checking |
| `transform` | Data transformation | Parse, filter, format data |
| `condition` | Conditional branching | Decision logic |
| `tool_call` | Execute custom tool | API calls, database queries |
| `output` | Format and return results | Final output formatting |

---

## 🔧 Built-in Tools

### LLM Call
```yaml
- id: "summarize"
  type: "llm_call"
  config:
    prompt: "Summarize: {text}"
    model: "llama-3.1-70b-versatile"
    temperature: 0.7
    max_tokens: 500
```

### Web Search
```yaml
- id: "search"
  type: "web_search"
  config:
    query: "{search_term}"
    max_results: 5
```

### Data Transform
```yaml
- id: "parse"
  type: "transform"
  config:
    operation: "json_parse"
    input_field: "raw_data"
    output_field: "parsed_data"
```

### Conditional Routing
```yaml
- id: "check"
  type: "condition"
  config:
    expression: "state.confidence > 0.8"
    true_path: "node_a"
    false_path: "node_b"
```

---

## 🎨 Visual Interface

The framework includes a web-based visual interface for:

- **Flow Designer**: Drag-and-drop interface for building workflows
- **Execution Monitor**: Real-time visualization of running flows
- **State Inspector**: View shared state and memory at each step
- **Audit Logs**: Browse execution history and debug issues

Access the UI at `http://localhost:8000/ui` after starting the API server.

---

## 📡 REST API

### Core Endpoints

#### Create Flow
```http
POST /flows/create
Content-Type: application/json

{
  "name": "My Flow",
  "definition": { ... }
}
```

#### Execute Flow
```http
POST /flows/execute
Content-Type: application/json

{
  "flow_id": "flow-123",
  "input": { ... }
}
```

#### Get Execution Status
```http
GET /executions/{execution_id}/status
```

#### List Executions
```http
GET /executions?flow_id=flow-123&status=completed
```

Full API documentation available at `http://localhost:8000/docs` (Swagger UI).

---

## 🛠️ Creating Custom Tools

### Define a Custom Tool

```python
# examples/custom_tools/email_sender.py

from core.tools import BaseTool

class EmailSenderTool(BaseTool):
    """Send emails via SMTP"""
    
    def __init__(self):
        super().__init__(
            name="email_sender",
            description="Send email notifications"
        )
    
    def execute(self, state, config):
        recipient = config.get("to")
        subject = config.get("subject")
        body = config.get("body")
        
        # Your email sending logic here
        result = send_email(recipient, subject, body)
        
        return {
            "success": result.success,
            "message_id": result.id
        }
    
    def validate_config(self, config):
        required = ["to", "subject", "body"]
        return all(k in config for k in required)
```

### Register Custom Tool

```python
from core.tools import ToolRegistry
from examples.custom_tools.email_sender import EmailSenderTool

# Register tool
ToolRegistry.register(EmailSenderTool())
```

### Use in Flow

```yaml
nodes:
  - id: "send_notification"
    type: "tool_call"
    config:
      tool: "email_sender"
      to: "user@example.com"
      subject: "Agent Notification"
      body: "{result_summary}"
```

---

## 📊 Observability

### Logging

All executions are logged to SQLite with:
- Execution ID and timestamps
- Node-level execution details
- State snapshots at each step
- Error traces and retry attempts

### Metrics

Track key performance indicators:
- Execution duration (total and per-node)
- Success/failure rates
- Retry statistics
- Tool usage patterns

### Query Logs

```python
from storage.sqlite_backend import get_execution_logs

# Get all logs for an execution
logs = get_execution_logs(execution_id="exec-123")

# Query by status
failed = get_execution_logs(status="failed", limit=10)

# Export for analysis
export_logs_to_csv(execution_id="exec-123", output="logs.csv")
```

---

## 🎯 Example Agents

### 1. Research Assistant Agent

**Use Case**: Search the web, summarize findings, generate report

```yaml
name: "Research Assistant"
description: "Automated research and summarization"

nodes:
  - id: "search"
    type: "web_search"
    config:
      query: "{research_topic}"
      max_results: 5
  
  - id: "summarize_each"
    type: "llm_call"
    config:
      prompt: "Summarize this article: {article_text}"
      iterate_over: "search.results"
  
  - id: "combine"
    type: "llm_call"
    config:
      prompt: "Create a comprehensive report from these summaries: {summaries}"
  
  - id: "output"
    type: "output"
    config:
      format: "markdown"

edges:
  - from: "search"
    to: "summarize_each"
  - from: "summarize_each"
    to: "combine"
  - from: "combine"
    to: "output"

input:
  research_topic: "string"
```

### 2. Data Validation Pipeline

**Use Case**: Validate CSV data, generate insights, alert on errors

```yaml
name: "Data Validator"
description: "Validate and analyze data files"

nodes:
  - id: "parse"
    type: "transform"
    config:
      operation: "csv_parse"
      input_field: "file_path"
  
  - id: "validate"
    type: "transform"
    config:
      operation: "validate_schema"
      schema: "{validation_rules}"
  
  - id: "check_errors"
    type: "condition"
    config:
      expression: "state.validation.error_count > 0"
      true_path: "alert"
      false_path: "analyze"
  
  - id: "alert"
    type: "tool_call"
    config:
      tool: "email_sender"
      to: "{admin_email}"
      subject: "Data Validation Errors"
  
  - id: "analyze"
    type: "llm_call"
    config:
      prompt: "Analyze this data and provide insights: {parsed_data}"
  
  - id: "output"
    type: "output"

edges:
  - from: "parse"
    to: "validate"
  - from: "validate"
    to: "check_errors"
  - from: "check_errors"
    to: "alert"
    condition: "errors_found"
  - from: "check_errors"
    to: "analyze"
    condition: "no_errors"
  - from: "alert"
    to: "output"
  - from: "analyze"
    to: "output"

input:
  file_path: "string"
  validation_rules: "object"
  admin_email: "string"
```

---

## 🔄 Future Roadmap

### Phase 1: Apache Integration
- Apache Kafka for message queuing
- Apache Airflow for DAG scheduling
- Apache Camel for enterprise integrations

### Phase 2: Advanced Features
- Multi-agent collaboration
- Reflection and self-improvement loops
- Human-in-the-loop checkpoints
- Vector database integration for long-term memory

### Phase 3: Enterprise Features
- Distributed execution
- Advanced monitoring (Prometheus/Grafana)
- Role-based access control
- Workflow versioning

### Phase 4: Optimizations
- Intel AI acceleration
- Parallel node execution
- Caching and memoization
- Performance benchmarking suite

---

## 🧪 Testing

```bash
# Run all tests
pytest tests/

# Run specific test suite
pytest tests/test_core.py

# Run with coverage
pytest --cov=core --cov=orchestrator tests/
```

---

## 📚 Documentation

- [Architecture Guide](docs/architecture.md)
- [API Reference](docs/api_reference.md)
- [Flow Definition Guide](docs/flow_definition.md)
- [Custom Tools Development](docs/custom_tools.md)
- [Performance Tuning](docs/performance.md)

---

## 🤝 Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

## 📄 License

[Your License Here]

---

## 🆘 Support

- **Issues**: Report bugs via GitHub Issues
- **Discussions**: Join community discussions
- **Documentation**: Full docs at `/docs`

---

## 🙏 Acknowledgments

Built with inspiration from LangGraph, Apache Airflow, and the broader AI agent ecosystem.