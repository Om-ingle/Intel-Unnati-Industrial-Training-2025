# Intel Training - AI Agent Framework Curriculum

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Framework: Custom](https://img.shields.io/badge/Framework-Custom%20Built-green.svg)](agents/framework_prototype/)

## 🎯 Project Overview

This repository contains a **custom-built AI Agent Framework** developed as part of Intel's training curriculum. The framework enables orchestration of complex agentic workflows from input to output **without relying on existing frameworks** like CrewAI, AutoGen, or n8n.

### Problem Statement

**Build-Your-Own AI Agent Framework** - Create an AI Agent framework (not just an app) that can orchestrate agentic workflows using task flows as DAGs (Directed Acyclic Graphs). The framework must support:
- Definition and execution of agentic workflows
- Monitoring and auditing capabilities
- Integration with Apache components for orchestration, messaging, and storage
- Intel technology optimizations (DevCloud, OpenVINO™)

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    USER INTERFACE LAYER                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐ │
│  │   Web UI     │  │  REST API    │  │   Streamlit App      │ │
│  │              │  │  (FastAPI)   │  │ (Local/Distributed)  │ │
│  └──────┬───────┘  └──────┬───────┘  └──────────┬───────────┘ │
└─────────┼──────────────────┼─────────────────────┼─────────────┘
          │                  │                     │
          ▼                  ▼                     ▼
┌─────────────────────────────────────────────────────────────────┐
│                   APACHE INTEGRATION LAYER                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐ │
│  │   Airflow    │  │    Kafka     │  │     Camel            │ │
│  │ (Scheduler)  │  │ (Message Bus)│  │  (Enterprise GW)     │ │
│  └──────┬───────┘  └──────┬───────┘  └──────────┬───────────┘ │
└─────────┼──────────────────┼─────────────────────┼─────────────┘
          │                  │                     │
┌─────────▼──────────────────▼─────────────────────▼──────────────┐
│                   ORCHESTRATION LAYER                          │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │  Flow Parser (YAML → Python Objects)                    │  │
│  │  • Validates workflow definitions                       │  │
│  │  • Generates execution DAGs                             │  │
│  └─────────────────────┬───────────────────────────────────┘  │
│                        │                                       │
│  ┌─────────────────────▼───────────────────────────────────┐  │
│  │  Flow Executor (State Machine Engine)                   │  │
│  │  • Executes nodes in topological order                  │  │
│  │  • Manages state transitions                            │  │
│  │  • Handles retries, timeouts, and errors                │  │
│  └─────────────────────┬───────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🌟 Core Framework: `agents/framework_prototype`

The heart of this repository is the **AI Agent Framework** located in `agents/framework_prototype/`. This is a production-ready, extensible framework for building and orchestrating AI agents.

### Key Features

#### 🎨 **Flow Definition**
- Define workflows using **YAML/JSON** configuration files
- Support for **DAG (Directed Acyclic Graph)** execution
- Conditional routing and branching logic
- Variable interpolation and templating

#### ⚙️ **Execution Engine**
- **State machine-based** orchestration
- Topological sorting for optimal execution order
- **Shared state management** across workflow nodes
- Async execution support

#### 🛡️ **Guardrails & Reliability**
- Built-in **retry mechanisms** with exponential backoff
- Configurable **timeouts** per node
- Comprehensive **error handling** and recovery
- Circuit breaker patterns

#### 📊 **Observability**
- Complete **audit trail** of all executions
- Node-level execution tracking
- Performance metrics (duration, success rate)
- SQLite-based persistence

#### 🔌 **Extensibility**
- **Plugin system** for custom nodes
- Tool registry for reusable components
- Easy integration with external APIs
- Support for custom data transformations

#### 🎛️ **Visual Interface**
- Interactive **workflow designer** (web-based)
- Real-time **execution monitoring**
- State inspection and debugging
- **Streamlit dashboards** for analytics & distributed control

#### 🌐 **Enterprise Integration (New!)**
- **Distributed Execution**: Scale execution across multiple workers via Kafka
- **Scheduled Workflows**: Automate agent runs with Apache Airflow
- **Universal Connectors**: Integrate with legacy systems via Apache Camel

---

## 📁 Project Structure

```
curriculum/
├── README.md                          # This file
│
├── agents/                            # 🎯 MAIN FRAMEWORK
│   ├── framework_prototype/           # Core agent framework
│   │   │
│   │   ├── core/                      # Framework core
│   │   │   ├── flow_engine.py         # State machine executor
│   │   │   ├── flow.py                # Flow definition models
│   │   │   ├── state.py               # Shared state management
│   │   │   ├── node.py                # Base node class
│   │   │   ├── tools.py               # Tool system & registry
│   │   │   └── guardrails.py          # Retry/timeout/error handling
│   │   │
│   │   ├── orchestrator/              # Orchestration layer
│   │   │   ├── flow_parser.py         # YAML/JSON parser & validator
│   │   │   ├── executor.py            # Workflow execution manager
│   │   │   └── api.py                 # FastAPI REST endpoints
│   │   │
│   │   ├── nodes/                     # Node implementations
│   │   │   ├── basic_nodes.py         # Transform, Output, Delay
│   │   │   ├── advanced_nodes.py      # LLM, WebSearch, Aggregator
│   │   │   └── external_nodes.py      # API integrations
│   │   │
│   │   ├── storage/                   # Persistence layer
│   │   │   ├── sqlite_backend.py      # SQLite implementation
│   │   │   └── models.py              # Database models
│   │   │
│   │   ├── api/                       # REST API
│   │   │   └── server.py              # FastAPI application
│   │   │
│   │   ├── examples/                  # Example workflows
│   │   │   ├── research_agent_workflow.yaml
│   │   │   ├── content_creator_agent_workflow.yaml
│   │   │   ├── smart_qa_agent_workflow.yaml
│   │   │   └── tour_planner_agent_workflow.yaml
│   │   │
│   │   ├── tests/                     # Test suite
│   │   │   ├── test_core.py
│   │   │   ├── test_phase3.py
│   │   │   └── test_api_e2e.py
│   │   │
│   │   ├── dashboard.py               # Streamlit dashboard (Main UI)
│   │   ├── cortex_dashboard.py        # Real-time Kafka monitoring UI
│   │   ├── worker.py                  # Distributed worker node
│   │   ├── dags/                      # Airflow DAGs
│   │   ├── plugins/                   # Airflow Plugins
│   │   ├── requirements.txt           # Python dependencies
│   │   ├── setup.py                   # Package setup
│   │   └── README.md                  # Framework documentation
│   │
│   ├── agent_structure.py             # Agent design patterns
│   └── simple_agent.py                # Simple agent example
│
├── api-tasks-models/                  # API integration tasks
├── database/                          # Database examples
├── infrastructure/                    # Infrastructure configs
├── loadbalancer/                      # Load balancer examples
├── ml/                                # ML model examples
├── text-generation/                   # Text generation examples
└── tmp/                               # Temporary files
```

---

## 🚀 Getting Started with the Agent Framework

### Prerequisites

- **Python 3.9+**
- **pip** or **uv** (recommended)
- API keys for LLM providers (Groq, OpenAI, etc.)

### Installation

#### Option 1: Using `uv` (Recommended)

```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Add to PATH
echo 'eval "$(uv generate-shell-completion bash)"' >> ~/.bashrc
source ~/.bashrc

# Navigate to framework
cd agents/framework_prototype

# Create virtual environment and install dependencies
uv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
uv pip install -r requirements.txt
```

#### Option 2: Using pip

```bash
cd agents/framework_prototype

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Configuration

1. **Copy environment template:**
   ```bash
   cp .env.example .env
   ```

2. **Add your API keys to `.env`:**
   ```bash
   # Groq API (for LLM calls)
   GROQ_API_KEY=your_groq_api_key_here
   
   # Brave Search API (for web search)
   BRAVE_API_KEY=your_brave_api_key_here
   
   # Optional: OpenAI API
   OPENAI_API_KEY=your_openai_api_key_here
   ```

3. **Get API keys:**
   - **Groq:** https://console.groq.com/keys
   - **Brave Search:** https://brave.com/search/api/
   - **OpenAI:** https://platform.openai.com/api-keys

See `agents/framework_prototype/API_KEYS_GUIDE.md` for detailed instructions.

---

## 💡 Quick Start Examples

### 1. Run the Research Agent

```bash
cd agents/framework_prototype
python test_research_agent.py
```

This agent will:
1. Search the web for information about "quantum computing"
2. Analyze the search results using an LLM
3. Generate a comprehensive summary
4. Create actionable insights
5. Compile a complete research report

### 2. Run the Smart Q&A Agent

```bash
python test_qa_agent.py
```

This agent will:
1. Analyze the question
2. Determine if web research is needed
3. Search for current information (if needed)
4. Generate a comprehensive answer
5. Suggest relevant follow-up questions

### 3. Launch the Dashboard

```bash
# On Linux/Mac
./run_dashboard.sh

# On Windows
run_dashboard.bat

# Or directly with Python
streamlit run dashboard.py
```

The dashboard provides:
- Workflow execution interface
- Real-time monitoring
- Execution history and analytics
- Performance metrics visualization

### 4. 🚀 Run Distributed Execution (Production Mode)

This mode allows you to run agents asynchronously across multiple workers.

**Step 1: Start Infrastructure**
```bash
docker compose up -d
```
*Starts Kafka, Zookeeper, and Airflow.*

**Step 2: Start a Worker**
```bash
# Open a NEW terminal
python worker.py
```

**Step 3: Run Dashboard**
```bash
# Open another terminal
streamlit run dashboard.py
```
*Select "Distributed (Kafka)" mode in the sidebar and click "Run".*

### 5. Start the REST API

```bash
# On Linux/Mac
./run_server.sh

# Or directly
python -m uvicorn api.server:app --reload --host 0.0.0.0 --port 8000
```

Access the API at:
- **Swagger UI:** http://localhost:8000/docs
- **Health Check:** http://localhost:8000/health

---

## 🎓 Creating Your First Agent

### Step 1: Define Your Workflow (YAML)

Create `my_agent.yaml`:

```yaml
name: "My First Agent"
description: "A simple agent that processes user input"

nodes:
  # Step 1: Transform input
  - id: "prepare_input"
    type: "transform"
    config:
      operation: "uppercase"
      input_key: "user_message"
      output_key: "processed_message"
  
  # Step 2: Call LLM
  - id: "generate_response"
    type: "llm_call"
    config:
      prompt: "Respond to this message: {processed_message}"
      model: "llama-3.1-70b-versatile"
      temperature: 0.7
      output_key: "llm_response"
  
  # Step 3: Output result
  - id: "output"
    type: "output"
    config:
      input_key: "llm_response"
      format: "json"

edges:
  - from: "prepare_input"
    to: "generate_response"
  - from: "generate_response"
    to: "output"

input:
  user_message: "string"
```

### Step 2: Execute Your Workflow

```python
from orchestrator.executor import WorkflowExecutor

# Initialize executor
executor = WorkflowExecutor()

# Execute workflow
execution = executor.execute_flow_file(
    "my_agent.yaml",
    {"user_message": "Hello, AI agent!"}
)

# Check results
if execution.status == "completed":
    response = execution.state.get("llm_response")
    print(f"Agent Response: {response}")
else:
    print(f"Error: {execution.error}")
```

### Step 3: Monitor Execution

```python
# View execution details
print(f"Execution ID: {execution.execution_id}")
print(f"Duration: {execution.get_duration():.2f}s")
print(f"Status: {execution.status}")

# View individual node results
for node_id, result in execution.node_results.items():
    print(f"{node_id}: {result.status.value}")
```

---

## 🔧 Available Node Types

The framework includes several built-in node types:

| Node Type | Description | Use Case |
|-----------|-------------|----------|
| `transform` | Data transformation | Uppercase, lowercase, passthrough, filtering |
| `llm_call` | Call LLM with prompt | Text generation, summarization, analysis |
| `web_search` | Search the web | Research, fact-checking, current information |
| `data_aggregator` | Combine multiple data sources | Merging results from multiple nodes |
| `output` | Format and output results | Final output formatting (JSON, text) |
| `delay` | Add delays for testing | Simulating long-running operations |
| `filter` | Filter data based on conditions | Conditional data processing |

### Creating Custom Nodes

```python
from core import Node, State, NodeResult

class MyCustomNode(Node):
    """Custom node implementation"""
    
    def execute(self, state: State) -> NodeResult:
        # Get config values
        input_key = self.config.get("input_key", "input")
        output_key = self.config.get("output_key", "output")
        
        # Get input from state
        input_value = state.get(input_key)
        
        # Process data (your logic here)
        result = your_custom_logic(input_value)
        
        # Save to state
        state.set(output_key, result)
        
        # Return success
        return NodeResult.success(result)

# Register your node type
from orchestrator.executor import WorkflowExecutor
executor = WorkflowExecutor()
executor.engine.register_node_type("my_custom_node", MyCustomNode)
```

---

## 📊 Reference Agent Workflows

The framework includes **four reference agent implementations** demonstrating real-world use cases:

### 1. 🔬 Research & Content Generation Agent
**File:** `research_agent_workflow.yaml`

**Workflow:**
```
Input → Prepare Query → Web Search → Analyze Results 
→ Generate Summary → Generate Insights → Aggregate Report → Output
```

**Use Cases:**
- Automated research and analysis
- Market research reports
- Competitive intelligence
- Content preparation for blogs/articles

### 2. ✍️ Content Creator Agent
**File:** `content_creator_agent_workflow.yaml`

**Workflow:**
```
Input → Research Topic → Create Outline → Write Introduction 
→ Write Main Content → Write Conclusion → Compile Article → Output
```

**Use Cases:**
- Blog post generation
- Article writing
- Content marketing
- SEO content creation

### 3. ❓ Smart Q&A Agent
**File:** `smart_qa_agent_workflow.yaml`

**Workflow:**
```
Input → Parse Question → Check Research Need → [Web Search OR Knowledge Base] 
→ Generate Answer → Enhance Explanation → Suggest Follow-ups → Output
```

**Use Cases:**
- Customer support chatbots
- Educational assistants
- Knowledge base systems
- FAQ automation

### 4. 🗺️ Tour Planner Agent
**File:** `tour_planner_agent_workflow.yaml`

**Workflow:**
```
Input → Research Destination → Generate Itinerary → Find Attractions 
→ Plan Activities → Create Travel Guide → Output
```

**Use Cases:**
- Travel planning assistants
- Itinerary generation
- Destination recommendations
- Trip optimization

---

## 🎯 Why This Framework?

### Advantages Over Existing Frameworks

| Feature | Our Framework | CrewAI | AutoGen | LangGraph |
|---------|---------------|--------|---------|-----------|
| **No External Dependencies** | ✅ Minimal | ❌ Heavy | ❌ Heavy | ❌ Heavy |
| **YAML-Based Workflows** | ✅ Yes | ❌ Code-only | ❌ Code-only | ⚠️ Partial |
| **Visual Designer** | ✅ Included | ❌ No | ❌ No | ✅ Yes |
| **Built-in Observability** | ✅ SQLite + Dashboard | ⚠️ Limited | ⚠️ Limited | ✅ Yes |
| **Custom Node Plugins** | ✅ Easy | ⚠️ Complex | ⚠️ Complex | ✅ Yes |
| **Intel Optimization Ready** | ✅ Yes | ❌ No | ❌ No | ❌ No |
| **Learning Curve** | ✅ Low | ⚠️ Medium | ⚠️ High | ⚠️ Medium |
| **Production Ready** | ✅ Yes | ✅ Yes | ⚠️ Partial | ✅ Yes |

### Design Principles

1. **Simplicity First** - Minimal dependencies, easy to understand
2. **Composability** - Build complex workflows from simple nodes
3. **Observability** - Track everything, debug easily
4. **Extensibility** - Plugin architecture for custom components
5. **Reliability** - Built-in guardrails and error handling
6. **Performance** - Intel optimizations, async execution

---

## 🔬 Intel Technology Integration

This framework is designed to leverage Intel technologies:

### Current Integration
- **Intel® DevCloud** - Development and testing environment
- **Python optimizations** - Efficient execution on Intel CPUs

### Planned Optimizations
- **Intel® OpenVINO™** - ML model optimization (LLMs, embeddings, re-rankers)
- **Intel® Extension for PyTorch** - Accelerated inference
- **Intel® Neural Compressor** - Model quantization and compression
- **Performance benchmarking** - Pre/post optimization metrics

---

## 📈 Performance & Benchmarks

### Execution Metrics

The framework tracks comprehensive performance metrics:

- **Execution duration** (total and per-node)
- **Success/failure rates**
- **Retry statistics**
- **Tool usage patterns**
- **State size and memory usage**

### Accessing Metrics

```python
from storage.sqlite_backend import SQLiteBackend

# Initialize storage
storage = SQLiteBackend()

# Get execution statistics
stats = storage.get_statistics()
print(f"Total Executions: {stats['total_executions']}")
print(f"Success Rate: {stats['success_rate']:.2%}")

# Get execution history
executions = storage.list_executions(limit=10, status="completed")
for exec in executions:
    print(f"{exec.flow_name}: {exec.duration_seconds:.2f}s")
```

---

## 🧪 Testing

### Run All Tests

```bash
cd agents/framework_prototype

# Run all tests
pytest tests/

# Run with coverage
pytest --cov=core --cov=orchestrator tests/

# Run specific test file
pytest tests/test_core.py -v
```

### Test Structure

- `test_core.py` - Core engine and state management tests
- `test_phase3.py` - Integration tests for nodes
- `test_api_e2e.py` - End-to-end API tests
- `test_research_agent.py` - Research agent workflow test
- `test_qa_agent.py` - Q&A agent workflow test

---

## 📚 Documentation

### Framework Documentation

Located in `agents/framework_prototype/`:

- **README.md** - Main framework documentation
- **QUICK_START.md** - Getting started guide
- **AGENT_WORKFLOWS_README.md** - Workflow examples and patterns
- **API_KEYS_GUIDE.md** - API key setup instructions
- **LLM_INTEGRATION_GUIDE.md** - LLM integration details
- **DASHBOARD_README.md** - Dashboard usage guide
- **HOW_TO_VIEW_RESULTS.md** - Result viewing utilities
- **TOUR_PLANNER_GUIDE.md** - Tour planner agent guide

### Architecture Documentation

- `plan.md` - Complete architecture breakdown
- `agent_structure.py` - Agent design patterns

---

## 🛣️ Roadmap

### Phase 1: Foundation ✅ (Completed)
- [x] Core engine (state machine, flow parser, executor)
- [x] Basic node types (transform, output, LLM, web search)
- [x] YAML workflow definitions
- [x] State management
- [x] Error handling and retries

### Phase 2: Orchestration & Storage ✅ (Completed)
- [x] REST API (FastAPI)
- [x] SQLite persistence
- [x] Execution history and audit logs
- [x] Performance metrics
- [x] Dashboard (Streamlit)

### Phase 3: Advanced Features ✅ (Completed)
- [x] Reference agent workflows
- [x] Data aggregation nodes
- [x] Web search integration
- [x] LLM integration (Groq, OpenAI)
- [x] Visual workflow designer

### Phase 4: Apache Integration ✅ (Completed)
- [x] Apache Kafka for message queuing (Distributed Execution)
- [x] Apache Airflow for DAG scheduling & orchestration
- [x] Apache Camel for enterprise system integrations
- [x] Distributed Worker Architecture

### Phase 5: Streamlit Integration ✅ (Completed)
- [x] Streamlit Dashboard for Agent Management
- [x] Distributed Job Submission via Dashboard
- [x] Real-time Result Polling & Monitoring

### Phase 6: Intel Optimizations 🔜 (Planned)
- [ ] Intel® OpenVINO™ integration
- [ ] Model optimization and quantization
- [ ] Performance benchmarking suite
- [ ] Intel® DevCloud deployment

### Phase 7: Enterprise Features 🔜 (Planned)
- [ ] Multi-agent collaboration
- [ ] Reflection and self-improvement loops
- [ ] Human-in-the-loop checkpoints
- [ ] Vector database integration for long-term memory
- [ ] Role-based access control
- [ ] Workflow versioning

---

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

1. **Report bugs** - Open an issue with details
2. **Suggest features** - Share your ideas
3. **Improve documentation** - Fix typos, add examples
4. **Submit PRs** - Add new nodes, fix bugs, optimize code

### Development Setup

```bash
# Clone repository
git clone <repo-url>
cd curriculum/agents/framework_prototype

# Install dev dependencies
pip install -r requirements-dev.txt

# Run tests
pytest tests/

# Format code
black .

# Lint code
flake8 .
```

---

## 📄 License

This project is part of Intel's training curriculum. See LICENSE file for details.

---

## 🙏 Acknowledgments

Built from scratch as part of Intel's AI training program, demonstrating:
- Custom agent framework design
- DAG-based workflow orchestration
- Production-ready software engineering practices
- Intel technology integration capabilities

Inspired by the broader AI agent ecosystem (LangGraph, Apache Airflow) but implemented independently.

---

## 📞 Support & Resources

### Getting Help

- **Issues:** Report bugs or ask questions via GitHub Issues
- **Documentation:** Full docs in `agents/framework_prototype/`
- **Examples:** See reference workflows in `agents/framework_prototype/examples/`

### Useful Links

- **Groq API Docs:** https://console.groq.com/docs
- **Brave Search API:** https://brave.com/search/api/
- **Intel® OpenVINO™:** https://docs.openvino.ai/
- **Intel® DevCloud:** https://devcloud.intel.com/

---

## 🚀 Quick Commands Reference

```bash
# Setup
cd agents/framework_prototype
pip install -r requirements.txt

# Run agents
python test_research_agent.py
python test_qa_agent.py
python demo_all_agents.py

# Start services
streamlit run dashboard.py                           # Dashboard
python -m uvicorn api.server:app --reload            # API Server

# Testing
pytest tests/                                         # All tests
pytest tests/test_core.py -v                         # Specific test

# Utilities
# Utilities
python view_results.py                               # View execution results

# Distributed Execution (Apache Stack)
docker compose up -d                                 # Start Kafka & Airflow
python worker.py                                     # Start Agent Worker
streamlit run dashboard.py                           # Run Dashboard (Select "Distributed" mode)
```

---

**Built with ❤️ for Intel's AI Training Program**

*Empowering developers to build production-ready AI agent systems from the ground up.*
