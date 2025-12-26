# 🤖 LLM Integration Guide

## Overview

The `LLMCallNode` now supports **both mock and real Groq API** modes. You can choose which one to use based on your needs.

---

## 🎯 How It Works

### Auto-Detection (Default)
- **If `GROQ_API_KEY` is set** → Uses **real Groq API**
- **If `GROQ_API_KEY` is NOT set** → Uses **mock/simulated API**

### Manual Control
You can override auto-detection in your workflow YAML:

```yaml
- id: "llm_node"
  type: "llm_call"
  config:
    prompt: "Your prompt here"
    model: "llama-3.3-70b-versatile"
    use_mock: true   # Force mock mode (even if API key exists)
    # OR
    use_real: true   # Force real API (will fail if no API key)
```

---

## 🔧 Configuration Options

### Basic Config
```yaml
config:
  prompt: "Summarize: {topic}"
  model: "llama-3.3-70b-versatile"  # Groq model name
  temperature: 0.7
  max_tokens: 1000
  output_key: "summary"
```

### Mode Control
```yaml
config:
  prompt: "Your prompt"
  use_mock: false    # Use real API if available (default)
  # OR
  use_mock: true     # Force mock mode
  # OR
  use_real: true     # Force real API (requires API key)
```

---

## 🚀 Setup for Real API

### 1. Get Groq API Key
1. Visit [Groq Console](https://console.groq.com/)
2. Sign up/login
3. Go to API Keys section
4. Create a new API key

### 2. Set Environment Variable

**Linux/WSL:**
```bash
export GROQ_API_KEY="your_api_key_here"
```

**Windows PowerShell:**
```powershell
$env:GROQ_API_KEY="your_api_key_here"
```

**Windows CMD:**
```cmd
set GROQ_API_KEY=your_api_key_here
```

**Make it permanent (Linux/WSL):**
```bash
echo 'export GROQ_API_KEY="your_api_key_here"' >> ~/.bashrc
source ~/.bashrc
```

### 3. Install Groq Package
```bash
pip install groq
# OR
uv pip install groq
```

---

## 📋 Available Groq Models

- `llama-3.3-70b-versatile` (default, recommended)
- `llama-3.1-8b-instant` (faster, less capable)
- `llama-3.1-70b-versatile` (alternative)
- `mixtral-8x7b-32768` (alternative)

---

## 🎭 Use Cases

### Development/Testing (Mock Mode)
```yaml
config:
  prompt: "Test prompt"
  use_mock: true  # Fast, no API costs
```

**Benefits:**
- ✅ Fast execution
- ✅ No API costs
- ✅ Works offline
- ✅ Good for testing workflows

### Production (Real API)
```yaml
config:
  prompt: "Real prompt"
  model: "llama-3.3-70b-versatile"
  # use_mock not set = auto-detect (uses real if API key exists)
```

**Benefits:**
- ✅ Real LLM responses
- ✅ Actual intelligence
- ✅ Production-ready

---

## 🔍 How to Check Which Mode Is Running

When you run a workflow, you'll see in the output:
```
🤖 LLM Call: llama-3.3-70b-versatile (REAL API)
```
or
```
🤖 LLM Call: llama-3.3-70b-versatile (MOCK)
```

---

## ⚠️ Troubleshooting

### "Real API call failed, falling back to mock"
- Check your `GROQ_API_KEY` is set correctly
- Verify API key is valid
- Check internet connection
- Review API quota/limits

### Mock responses when you want real
- Ensure `GROQ_API_KEY` environment variable is set
- Don't set `use_mock: true` in config
- Check that `groq` package is installed

### Real API not working
- Verify API key: `echo $GROQ_API_KEY`
- Test with simple script:
  ```python
  from groq import Groq
  client = Groq()
  response = client.chat.completions.create(
      model="llama-3.3-70b-versatile",
      messages=[{"role": "user", "content": "Hello"}]
  )
  print(response.choices[0].message.content)
  ```

---

## 💡 Best Practices

1. **Development**: Use mock mode for fast iteration
2. **Testing**: Use real API to test actual responses
3. **Production**: Always use real API with proper error handling
4. **Cost Control**: Use mock for non-critical workflows
5. **Environment Variables**: Store API keys securely, never commit them

---

## 📝 Example Workflows

### Mock Mode Workflow
```yaml
- id: "test_llm"
  type: "llm_call"
  config:
    prompt: "Test: {input}"
    use_mock: true
    output_key: "test_result"
```

### Real API Workflow
```yaml
- id: "real_llm"
  type: "llm_call"
  config:
    prompt: "Analyze: {data}"
    model: "llama-3.3-70b-versatile"
    temperature: 0.7
    output_key: "analysis"
    # use_mock not set = uses real API if available
```

---

**Now you have the flexibility to use either mode as needed! 🎉**

