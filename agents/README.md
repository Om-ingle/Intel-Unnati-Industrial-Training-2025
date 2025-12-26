# Agent Learning Scripts

A collection of learning scripts for building AI agents with function calling capabilities using Groq API.

## 📋 Prerequisites

- Python 3.8 or higher
- Windows, macOS, or Linux
- Internet connection for API calls

## 🚀 Quick Start

### Step 1: Install uv (Python Package Manager)

uv is a fast Python package manager that we'll use to manage our environment and dependencies.

#### Windows (PowerShell):
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

#### macOS/Linux:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

#### Alternative (pip):
```bash
pip install uv
```

### Step 2: Create and Activate Virtual Environment

```bash
# Create a new virtual environment
uv venv

# Activate the environment
# Windows (PowerShell):
.venv\Scripts\Activate.ps1

# Windows (CMD):
.venv\Scripts\activate.bat

# macOS/Linux:
source .venv/bin/activate
```

### Step 3: Install Dependencies

```bash
# Install all dependencies from requirements.txt
uv pip install -r requirements.txt

# Or install individually:
uv add groq instructor pydantic

# Or using pip if you prefer:
# pip install -r requirements.txt
```

### Step 4: Set Up Groq API Key

1. **Get your API key**:
   - Visit [Groq Console](https://console.groq.com/)
   - Sign up for a free account
   - Navigate to API Keys section
   - Create a new API key

2. **Set the environment variable**:

   #### Windows (PowerShell):
   ```powershell
   $env:GROQ_API_KEY="your_api_key_here"
   ```

   #### Windows (CMD):
   ```cmd
   set GROQ_API_KEY=your_api_key_here
   ```

   #### macOS/Linux:
   ```bash
   export GROQ_API_KEY="your_api_key_here"
   ```

   #### Alternative: Create a .env file
   ```bash
   # Create .env file in project root
   echo "GROQ_API_KEY=your_api_key_here" > .env
   ```

## 🎯 Running the Learning Script

### Simple Agent (Calculator)

The `simple_agent.py` demonstrates basic function calling with a calculator tool:

```bash
python simple_agent.py
```

**What it does:**
- Uses Groq's Llama 3.3 70B model
- Implements function calling for mathematical calculations
- Shows conversation flow with tool usage
- Demonstrates error handling

**Example interaction:**
```
Input: "What is 25 * 4 + 10?"
Output: "The result of 25 * 4 + 10 is 110."
```

### Agent Structure (Structured Response)

The `agent_structure.py` demonstrates structured agent responses using Pydantic models and the instructor library:

```bash
python agent_structure.py
```

**What it does:**
- Uses instructor library for structured outputs
- Implements Pydantic models for type safety
- Demonstrates tool schema definition
- Shows structured tool call parsing

**Example interaction:**
```
Input: "What's the weather like in San Francisco?"
Output: 
Input: What's the weather like in San Francisco?
Tool: get_weather_info
Parameters: {"location": "San Francisco"}
```

#### Additional Dependencies for Agent Structure

This script requires additional packages:

```bash
# Install additional dependencies
uv add instructor pydantic

# Or using pip:
# pip install instructor pydantic
```

#### Running on WSL (Windows Subsystem for Linux)

If you prefer to run the scripts on WSL for a Linux environment:

1. **Open WSL Terminal**:
```bash
# From Windows Command Prompt or PowerShell
wsl
```

2. **Navigate to your project directory**:
```bash
# If your project is on Windows drive C:
cd /mnt/c/Users/akulshre/OneDrive\ -\ Intel\ Corporation/Desktop/Development/Agents/

# Or copy the project to WSL home directory
cp -r /mnt/c/Users/akulshre/OneDrive\ -\ Intel\ Corporation/Desktop/Development/Agents ~/agents
cd ~/agents
```

3. **Set up Python environment in WSL**:
```bash
# Install uv in WSL (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh
source ~/.bashrc

# Create virtual environment
uv venv

# Activate environment
source .venv/bin/activate

# Install dependencies
uv add groq instructor pydantic
```

4. **Set environment variable in WSL**:
```bash
export GROQ_API_KEY="your_api_key_here"

# Or add to ~/.bashrc for persistence
echo 'export GROQ_API_KEY="your_api_key_here"' >> ~/.bashrc
source ~/.bashrc
```

5. **Run the scripts**:
```bash
python simple_agent.py
python agent_structure.py
```

## 🧠 Understanding the Code

### Simple Agent Components

1. **Groq Client**: Direct connection to Groq API for LLM inference
2. **Function Definition**: `calculate()` function that evaluates math expressions
3. **Tool Schema**: JSON schema defining available functions for the LLM
4. **Conversation Flow**: Multi-turn conversation with function calling
5. **Error Handling**: Graceful handling of invalid expressions

### Agent Structure Components

1. **Instructor Library**: Enables structured outputs from LLMs using Pydantic models
2. **Pydantic Models**: Type-safe data structures for tool calls and responses
3. **BaseModel Classes**: `ToolCall` and `ResponseModel` for structured parsing
4. **JSON Mode**: Forces the LLM to respond in structured JSON format
5. **Tool Schema**: Defines available tools and their parameter requirements

### Comparison: Simple vs Structured Approach

| Feature | Simple Agent | Agent Structure |
|---------|-------------|-----------------|
| **Output Format** | Free text | Structured JSON |
| **Type Safety** | None | Pydantic validation |
| **Tool Parsing** | Manual JSON parsing | Automatic model parsing |
| **Error Handling** | Basic try/catch | Pydantic validation |
| **Complexity** | Lower | Higher |
| **Use Case** | Simple interactions | Production systems |

### Function Calling Flow

1. **Initial Request**: User sends a mathematical query
2. **LLM Analysis**: Model determines if a function call is needed
3. **Function Execution**: Calculator function processes the expression
4. **Result Integration**: Function result is added to conversation
5. **Final Response**: LLM generates human-readable response

## 🔧 Customization

### Adding New Functions

To extend the agent with new capabilities:

1. **Define your function**:
```python
def get_weather(city):
    """Get weather information for a city"""
    # Your implementation here
    return json.dumps({"weather": "sunny", "temperature": "72°F"})
```

2. **Add to tools schema**:
```python
tools = [
    # Existing calculate tool...
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get weather information for a city",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "The city name",
                    }
                },
                "required": ["city"],
            },
        }
    }
]
```

3. **Register in available functions**:
```python
available_functions = {
    "calculate": calculate,
    "get_weather": get_weather,
}
```

### Changing the Model

Groq supports various models. To switch:

```python
MODEL = 'llama-3.1-8b-instant'    # Faster, less capable
MODEL = 'llama-3.3-70b-versatile' # Balanced (default)
MODEL = 'mixtral-8x7b-32768'      # Alternative option
```

## 📚 Learning Path

1. **Start Here**: Run `simple_agent.py` to understand basic function calling
2. **Structure**: Run `agent_structure.py` to learn structured responses with Pydantic
3. **Compare**: Understand the differences between simple and structured approaches
4. **Experiment**: Modify functions or add new math/weather operations
5. **WSL Practice**: Try running scripts on WSL for Linux environment experience
6. **Extend**: Add new tools (web search, file operations, database queries)
7. **Advanced**: Implement multi-step reasoning and complex workflows
8. **Production**: Build type-safe agents for real-world applications

## 🛠️ Troubleshooting

### Common Issues

**API Key Error**:
```
Error: GROQ_API_KEY environment variable not set
```
- Solution: Set your API key as shown in Step 4

**Module Not Found**:
```
ModuleNotFoundError: No module named 'groq'
```
- Solution: Ensure virtual environment is activated and groq is installed

**Rate Limiting**:
```
RateLimitError: Rate limit exceeded
```
- Solution: Wait a moment and try again (free tier has limits)

**Invalid Expression**:
```
{"error": "Invalid expression"}
```
- Solution: This is expected behavior for malformed math expressions

**Pydantic Validation Error**:
```
ValidationError: X validation errors for ResponseModel
```
- Solution: The LLM output doesn't match the expected Pydantic model structure

**WSL Path Issues**:
```
FileNotFoundError: [Errno 2] No such file or directory
```
- Solution: Use proper WSL paths (`/mnt/c/...`) or copy files to WSL filesystem

**WSL Environment Variables**:
```
GROQ_API_KEY not found in WSL
```
- Solution: Set environment variables in WSL separately from Windows

### Getting Help

- **Groq Documentation**: [https://console.groq.com/docs](https://console.groq.com/docs)
- **API Reference**: [https://console.groq.com/docs/api-reference](https://console.groq.com/docs/api-reference)
- **Community**: Groq Discord and forums

## 📈 Next Steps

Once you're comfortable with the basic agent:

1. **Explore Multi-Agent Systems**: Build agents that collaborate
2. **Add Memory**: Implement conversation history and context retention
3. **Web Integration**: Connect to APIs and web services
4. **GUI Interface**: Create a chat interface using Streamlit or Gradio
5. **Production Deployment**: Scale your agent for real-world use

## 🤝 Contributing

Feel free to:
- Add new example agents
- Improve existing scripts
- Share your learning modifications
- Report issues or suggest improvements

## 📄 License

This project is for educational purposes. Please respect Groq's terms of service and API usage guidelines.

---

**Happy Agent Building! 🤖**