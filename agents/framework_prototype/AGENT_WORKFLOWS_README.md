# 🤖 Agent Workflows - Real-World Examples

This directory contains **three sophisticated agent workflows** that demonstrate the full capabilities of your agent framework.

## 📋 Available Workflows

### 1. 🔬 Research & Content Generation Agent
**File:** `research_agent_workflow.yaml`

**What it does:**
- Takes a research topic
- Performs web search to gather information
- Analyzes results using LLM
- Generates comprehensive summary
- Creates actionable insights
- Compiles everything into a structured report

**Use Case:** Research assistant, content preparation, market analysis

**Test it:**
```bash
python test_research_agent.py
```

---

### 2. ✍️ Content Creator Agent
**File:** `content_creator_agent_workflow.yaml`

**What it does:**
- Researches a topic
- Creates a detailed content outline
- Writes introduction, main content, and conclusion
- Compiles a complete article

**Use Case:** Blog writing, article generation, content marketing

**Test it:**
```python
from orchestrator.executor import WorkflowExecutor

executor = WorkflowExecutor()
execution = executor.execute_flow_file(
    "content_creator_agent_workflow.yaml",
    {"topic": "the future of AI"}
)

print(execution.state.get("final_article"))
```

---

### 3. ❓ Smart Q&A Agent
**File:** `smart_qa_agent_workflow.yaml`

**What it does:**
- Analyzes questions
- Determines if research is needed
- Searches for current information when needed
- Generates comprehensive answers
- Suggests follow-up questions

**Use Case:** Customer support, knowledge base, educational assistant

**Test it:**
```python
from orchestrator.executor import WorkflowExecutor

executor = WorkflowExecutor()
execution = executor.execute_flow_file(
    "smart_qa_agent_workflow.yaml",
    {"question": "What is quantum computing?"}
)

print(execution.state.get("enhanced_answer"))
```

---

## 🚀 Quick Start

### Run All Demos
```bash
python demo_all_agents.py
```

This will run all three agents and show their capabilities.

### Run Individual Tests
```bash
# Research Agent
python test_research_agent.py

# Q&A Agent
python test_qa_agent.py
```

### Use in Your Code
```python
from orchestrator.executor import WorkflowExecutor

# Initialize
executor = WorkflowExecutor()

# Execute any workflow
execution = executor.execute_flow_file(
    "research_agent_workflow.yaml",
    {"topic": "your topic here"}
)

# Check results
if execution.status == "completed":
    result = execution.state.get("summary")  # or whatever output_key you need
    print(result)
```

---

## 🏗️ Workflow Structure

Each workflow follows this pattern:

1. **Input Processing** - Transform/prepare input data
2. **Research/Data Gathering** - Web search, API calls, etc.
3. **Analysis** - LLM processing, data transformation
4. **Generation** - Create content, summaries, answers
5. **Aggregation** - Combine results
6. **Output** - Format and return final result

### Node Types Used

- **`transform`** - Data transformation (uppercase, lowercase, passthrough)
- **`web_search`** - Search the web for information
- **`llm_call`** - Call LLM with prompts (uses Groq API)
- **`data_aggregator`** - Combine multiple data sources
- **`output`** - Format and output results

---

## 🎯 Key Features Demonstrated

✅ **Multi-step workflows** - Complex agentic reasoning  
✅ **DAG execution** - Nodes execute in proper order based on dependencies  
✅ **State management** - Data flows between nodes seamlessly  
✅ **LLM integration** - Multiple LLM calls in sequence  
✅ **Data aggregation** - Combining results from multiple steps  
✅ **Real-world use cases** - Practical agent applications  

---

## 🔧 Customization

### Change Topics/Questions
Edit the test files or pass different inputs:

```python
execution = executor.execute_flow_file(
    "research_agent_workflow.yaml",
    {"topic": "your custom topic"}
)
```

### Modify Workflows
Edit the YAML files to:
- Add more steps
- Change prompts
- Adjust node configurations
- Add new node types

### Add Your Own Workflow
1. Create a new `.yaml` file
2. Define nodes and edges
3. Test with `execute_flow_file()`

---

## 📊 Understanding Results

Each workflow stores results in the `State` object. Common output keys:

**Research Agent:**
- `summary` - Generated summary
- `insights` - Key insights
- `final_report` - Complete report

**Content Creator:**
- `outline` - Content outline
- `introduction` - Article introduction
- `main_content` - Main body
- `conclusion` - Conclusion
- `final_article` - Complete article

**Q&A Agent:**
- `enhanced_answer` - Comprehensive answer
- `followup_questions` - Suggested questions
- `final_response` - Complete response

Access them via:
```python
execution.state.get("key_name")
```

---

## 🐛 Troubleshooting

**Result is None?**
- Check the `output_key` in the node config (not the node `id`)
- Verify the node executed successfully
- Check `execution.status` - should be "completed"

**Workflow fails?**
- Check that all required node types are registered
- Verify YAML syntax is correct
- Ensure input data matches the workflow's expected format

**LLM not working?**
- Make sure `GROQ_API_KEY` environment variable is set
- Check your API quota/limits

---

## 🎓 Learning Path

1. **Start Simple** - Run `demo_all_agents.py` to see everything work
2. **Understand Structure** - Read one YAML file to see how workflows are defined
3. **Modify** - Change prompts or add nodes to existing workflows
4. **Create** - Build your own workflow for your specific use case

---

**Happy Agent Building! 🚀**

