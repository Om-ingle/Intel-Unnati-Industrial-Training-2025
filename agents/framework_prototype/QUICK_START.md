# 🚀 Quick Start - Test Your Agent Framework

## ✅ What I've Created For You

I've built **3 sophisticated agent workflows** that demonstrate your framework's real-world capabilities:

### 1. 🔬 Research & Content Generation Agent
- Researches topics, analyzes data, generates summaries and insights
- **File:** `research_agent_workflow.yaml`
- **Test:** `python test_research_agent.py`

### 2. ✍️ Content Creator Agent  
- Creates complete articles: research → outline → writing → compilation
- **File:** `content_creator_agent_workflow.yaml`
- **Test:** Use in code or see `demo_all_agents.py`

### 3. ❓ Smart Q&A Agent
- Answers questions with research, reasoning, and follow-up suggestions
- **File:** `smart_qa_agent_workflow.yaml`
- **Test:** `python test_qa_agent.py`

---

## 🎯 Fastest Way to Test

### Option 1: Run All Demos (Recommended)
```bash
cd agents/framework_prototype
python demo_all_agents.py
```

This will run all three agents and show you their full capabilities!

### Option 2: Test Individual Agents
```bash
# Research Agent
python test_research_agent.py

# Q&A Agent  
python test_qa_agent.py
```

### Option 3: Quick Test Script
```bash
python 1.py  # Your original test (now fixed!)
```

---

## 📝 Example Usage

```python
from orchestrator.executor import WorkflowExecutor

# Initialize
executor = WorkflowExecutor()

# Run Research Agent
execution = executor.execute_flow_file(
    "research_agent_workflow.yaml",
    {"topic": "quantum computing"}
)

# Get results
if execution.status == "completed":
    summary = execution.state.get("summary")
    insights = execution.state.get("insights")
    print(f"Summary: {summary}")
    print(f"Insights: {insights}")
```

---

## 🔧 What Was Fixed

1. **Your original issue:** Changed `execution.state.get('summarize')` → `execution.state.get('summary')` (use `output_key`, not node `id`)

2. **Flow Engine:** Now respects DAG execution order (topological sort) instead of just sequential

3. **YAML prompt:** Fixed typo `{cs world}` → `{name}`

---

## 📚 Key Concepts

- **Node ID** (`"summarize"`) = Just an identifier
- **Output Key** (`"summary"`) = Where results are stored in state
- **Always use `output_key` to retrieve results!**

---

## 🎓 Next Steps

1. **Run the demos** to see everything working
2. **Read the workflows** in the YAML files to understand structure
3. **Modify them** to create your own agents
4. **Build new workflows** for your specific use cases

---

## 📖 Full Documentation

See `AGENT_WORKFLOWS_README.md` for detailed documentation on all workflows.

---

**Your framework is ready to showcase! 🎉**

