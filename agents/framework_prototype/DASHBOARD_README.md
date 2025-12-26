# 🤖 Agent Framework Dashboard

A **generic UI dashboard** that automatically discovers and runs all your agents without requiring any special frontend code for each agent.

## 🚀 Quick Start

### Option 1: Using the script
```bash
chmod +x run_dashboard.sh
./run_dashboard.sh
```

### Option 2: Direct command
```bash
streamlit run dashboard.py
```

### Option 3: With custom port
```bash
streamlit run dashboard.py --server.port 8501
```

Then open your browser to: **http://localhost:8501**

---

## ✨ Features

### 🔍 Auto-Discovery
- **Automatically finds** all `.yaml` workflow files
- No manual registration needed
- Scans current directory and `examples/` folders

### 🎯 Generic Execution
- **Works with ANY agent** - no special code needed
- Automatically parses input schema from YAML
- Handles all node types transparently

### 📊 Rich Results Display
- **Key Results Tab**: Shows important outputs (summary, answer, insights, etc.)
- **All State Tab**: Browse all state variables
- **JSON View**: Raw data view for debugging

### 📜 Execution History
- Tracks all workflow executions
- Search and filter history
- Quick access to previous results

### 🎨 Clean UI
- Modern, responsive design
- Color-coded status indicators
- Organized result display
- Debug mode for developers

---

## 📋 How It Works

### 1. Discovery Phase
The dashboard automatically scans for YAML files:
- `*.yaml` files in current directory
- `examples/workflows/*.yaml`
- `examples/flows/*.yaml`

### 2. Workflow Selection
- Dropdown shows all discovered workflows
- Displays name and description
- Shows file path for reference

### 3. Input Collection
- Automatically extracts `input:` schema from YAML
- Creates appropriate input fields (text, number, etc.)
- Falls back to common patterns if no schema defined

### 4. Execution
- Runs workflow using `WorkflowExecutor`
- Shows real-time status
- Displays progress spinner

### 5. Results Display
- **Status**: Success/Failed/Running
- **Duration**: Execution time
- **Outputs**: All state variables organized in tabs
- **History**: Saved for later review

---

## 🎯 Adding New Agents

### It's Automatic! ✨

Just create a YAML workflow file:

```yaml
name: "My New Agent"
description: "Does something cool"
nodes:
  - id: "step1"
    type: "llm_call"
    config:
      prompt: "Process: {input}"
      output_key: "result"
edges: []
input:
  input: "string"
```

**That's it!** The dashboard will:
- ✅ Discover it automatically
- ✅ Show it in the dropdown
- ✅ Parse inputs
- ✅ Execute it
- ✅ Display results

**No frontend code needed!**

---

## 📊 Dashboard Pages

### 🏠 Run Agent
- Select workflow
- Provide inputs
- Execute and view results
- Main working page

### 📊 Execution History
- View all past executions
- Search and filter
- Quick access to results
- Clear history option

### ℹ️ About
- Dashboard information
- List of discovered workflows
- Usage instructions

---

## ⚙️ Settings

### Show Debug Info
- Enable in sidebar
- Shows node results
- Displays raw execution data
- Useful for troubleshooting

### API Status
- Shows GROQ_API_KEY status
- Indicates mock vs real API mode
- Quick health check

---

## 🎨 Result Display

### Key Results Tab
Shows important outputs like:
- `summary` - Generated summaries
- `answer` / `enhanced_answer` - Q&A responses
- `insights` - Key insights
- `final_report` - Complete reports
- `final_article` - Full articles

### All State Tab
- Browse all state variables
- Expandable sections
- Full content display

### JSON View
- Raw JSON format
- Copy-paste friendly
- For debugging/integration

---

## 🔧 Configuration

### Custom Port
```bash
streamlit run dashboard.py --server.port 8080
```

### Custom Address
```bash
streamlit run dashboard.py --server.address 0.0.0.0
```

### Theme
Edit `.streamlit/config.toml`:
```toml
[theme]
primaryColor = "#1f77b4"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f0f2f6"
```

---

## 🐛 Troubleshooting

### "No workflow files found"
- Check that YAML files exist
- Verify file extensions are `.yaml` (not `.yml`)
- Check file permissions

### "Execution failed"
- Check terminal for error messages
- Enable "Show Debug Info" in sidebar
- Verify workflow YAML syntax

### Dashboard won't start
- Install streamlit: `pip install streamlit`
- Check Python version (3.8+)
- Verify all dependencies installed

### Results not showing
- Check execution status (should be "completed")
- Look in "All State" tab for data
- Enable debug mode to see node results

---

## 💡 Tips

1. **Use descriptive workflow names** - They appear in the dropdown
2. **Define input schema** - Makes input collection easier
3. **Use standard output keys** - They appear in "Key Results" tab
4. **Check execution history** - Useful for comparing runs
5. **Enable debug mode** - When troubleshooting issues

---

## 🎯 Standard Output Keys

For best results display, use these keys:
- `summary` - Summaries
- `answer` / `enhanced_answer` - Answers
- `insights` - Insights
- `final_report` - Reports
- `final_response` - Responses
- `final_article` - Articles
- `outline` - Outlines
- `introduction` - Introductions
- `main_content` - Main content
- `conclusion` - Conclusions

---

## 🚀 Advanced Usage

### Multiple Workflows
The dashboard handles multiple workflows automatically. Just add more YAML files!

### Custom Input Types
The dashboard infers input types from your schema:
- `"string"` → Text input
- `"number"` / `"int"` → Number input
- Others → Text input (fallback)

### Integration
Results are in JSON format - easy to integrate with other tools!

---

**Enjoy your agent dashboard! 🎉**

