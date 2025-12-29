# 🔑 API Keys & Model Selection Guide

## Overview

The dashboard now supports **multiple LLM providers** with API key management and model selection!

## 🚀 Features

### ✅ Supported Providers
- **Groq** - Fast inference with Llama models
- **Gemini** - Google's Gemini models with model selection
- **Auto** - Automatically selects available provider

### ✅ Key Features
- API key input in dashboard sidebar
- Secure password fields
- Model selection for Gemini
- Real-time API status indicators
- Auto-detection of available providers

---

## 📋 How to Use

### Step 1: Set API Keys

1. **Open the Dashboard Sidebar**
   - Look for "🔑 API Keys" section

2. **Enter Groq API Key** (Optional)
   - Get key from: https://console.groq.com/
   - Paste in "Groq API Key" field
   - Status will show "✅ Groq Ready"

3. **Enter Gemini API Key** (Optional)
   - Get key from: https://aistudio.google.com/
   - Paste in "Gemini API Key" field
   - Status will show "✅ Gemini Ready"
   - **Model selection dropdown will appear**

### Step 2: Select Provider

In the main "Run Agent" page:

1. **LLM Configuration Section**
   - Choose provider: **Auto**, **Groq**, or **Gemini**

2. **If Gemini Selected:**
   - Model dropdown appears
   - Select from available models:
     - `gemini-2.0-flash` (recommended, fastest)
     - `gemini-1.5-pro` (most capable)
     - `gemini-1.5-flash` (balanced)
     - `gemini-1.5-pro-latest`
     - `gemini-1.5-flash-latest`

3. **If Auto Selected:**
   - System automatically uses available APIs
   - Prefers Gemini if both are available
   - Falls back to Groq if only Groq available
   - Uses mock if no APIs available

### Step 3: Execute Workflow

- Click "▶️ Execute Workflow"
- System uses selected provider/model
- Results show which provider was used

---

## 🎯 Provider Selection Logic

### Auto Mode (Default)
```
If Gemini API key exists → Use Gemini
Else if Groq API key exists → Use Groq
Else → Use Mock mode
```

### Manual Selection
- **Groq**: Uses Groq API (requires Groq key)
- **Gemini**: Uses Gemini API (requires Gemini key + model selection)

---

## 📊 API Status Indicators

### Sidebar Status
- **✅ Groq Ready** - Groq API key is set
- **⚠️ Groq Not Set** - No Groq key
- **✅ Gemini Ready** - Gemini API key is set
- **ℹ️ Gemini Not Set** - No Gemini key

### Execution Page Status
- Shows which provider will be used
- Warns if selected provider not available
- Shows available providers in auto mode

---

## 🔧 Getting API Keys

### Groq API Key
1. Visit: https://console.groq.com/
2. Sign up/Login
3. Go to API Keys
4. Create new key
5. Copy and paste in dashboard

### Gemini API Key
1. Visit: https://aistudio.google.com/
2. Sign in with Google account
3. Click "Get API Key"
4. Create key in project
5. Copy and paste in dashboard

---

## 💡 Tips

1. **Both Keys**: Set both for maximum flexibility
2. **Auto Mode**: Best for testing - automatically uses what's available
3. **Model Selection**: Gemini models differ in speed/capability
   - `gemini-2.0-flash` - Fastest, good for most tasks
   - `gemini-1.5-pro` - Most capable, slower
4. **Security**: API keys are stored in session (not saved to disk)
5. **Mock Mode**: Works without API keys for testing workflows

---

## 🐛 Troubleshooting

### "Selected provider not available"
- Check API key is entered correctly
- Verify key is valid (not expired)
- Try refreshing the page

### "Gemini model selection not showing"
- Make sure Gemini API key is set
- Check you selected "Gemini" as provider

### "Still using mock mode"
- Verify API key is set in sidebar
- Check provider selection in execution page
- Look for error messages in terminal

### API calls failing
- Verify API key is correct
- Check internet connection
- Review API quota/limits
- Check terminal for detailed errors

---

## 🔄 Workflow Integration

### Using in Workflows

Your workflows automatically use the selected provider. No changes needed to YAML files!

**Example:**
```yaml
- id: "llm_node"
  type: "llm_call"
  config:
    prompt: "Answer: {question}"
    # Provider/model selected in dashboard
    # Or specify in config:
    # provider: "gemini"  # Optional override
    # model: "gemini-2.0-flash"  # Optional override
```

### Override in Workflow

You can still override in workflow YAML:
```yaml
config:
  provider: "groq"  # Force Groq
  model: "llama-3.3-70b-versatile"  # Specific model
```

---

## 📝 Environment Variables

The dashboard sets these automatically:
- `GROQ_API_KEY` - Groq API key
- `GEMINI_API_KEY` - Gemini API key
- `GEMINI_MODEL` - Selected Gemini model
- `LLM_PROVIDER` - Selected provider (auto/groq/gemini)

---

**Enjoy flexible LLM provider selection! 🎉**

