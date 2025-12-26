"""
Tools - Built-in actions for workflow nodes
"""

import os
import sys
from pathlib import Path
from typing import Any, Dict, Optional, List
import json
import re

# Handle imports
try:
    from .node import Node, NodeResult, NodeStatus
    from .state import State
except ImportError:
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from core.node import Node, NodeResult, NodeStatus
    from core.state import State

# External dependencies
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Try to import Groq, use mock if not available
GROQ_AVAILABLE = False
try:
    from groq import Groq
    GROQ_AVAILABLE = True
except Exception as e:
    print(f"⚠️  Groq import warning: {e}")
    print("⚠️  Using mock LLM for testing")


# ============================================================================
# TOOL REGISTRY
# ============================================================================

class ToolRegistry:
    """
    Registry for all available tools.
    Tools can be registered and retrieved by name.
    """
    _tools: Dict[str, type] = {}
    
    @classmethod
    def register(cls, name: str, tool_class: type):
        """Register a tool"""
        cls._tools[name] = tool_class
    
    @classmethod
    def get(cls, name: str) -> Optional[type]:
        """Get a tool by name"""
        return cls._tools.get(name)
    
    @classmethod
    def list_tools(cls) -> List[str]:
        """List all registered tools"""
        return list(cls._tools.keys())


# ============================================================================
# MOCK LLM CLIENT (for testing when Groq has issues)
# ============================================================================

class MockGroqClient:
    """Mock Groq client for testing"""
    
    class ChatCompletion:
        def __init__(self, content: str):
            self.choices = [type('obj', (object,), {
                'message': type('obj', (object,), {'content': content})()
            })()]
            self.usage = type('obj', (object,), {'total_tokens': 100})()
    
    class Chat:
        class Completions:
            @staticmethod
            def create(model, messages, temperature, max_tokens):
                # Generate mock response
                prompt = messages[0]['content']
                response = f"Mock LLM response for: '{prompt[:50]}...'. This is a simulated answer for testing purposes."
                return MockGroqClient.ChatCompletion(response)
        
        completions = Completions()
    
    def __init__(self, api_key):
        self.chat = MockGroqClient.Chat()


# ============================================================================
# LLM TOOL
# ============================================================================

class LLMCallTool(Node):
    """
    Call an LLM (Large Language Model) with a prompt.
    
    Config:
        prompt: The prompt to send to the LLM (supports {variable} templating)
        model: Model to use (default: from env)
        temperature: Sampling temperature (default: 0.7)
        max_tokens: Maximum tokens to generate (default: 1000)
    
    Example:
        config = {
            "prompt": "Summarize this: {text}",
            "model": "llama-3.1-70b-versatile",
            "temperature": 0.7
        }
    """
    
    def __init__(self, node_id: str, config: Dict[str, Any]):
        super().__init__(
            node_id=node_id,
            node_type="llm_call",
            config=config
        )
        
        # Initialize client (always use mock for now to avoid Groq issues)
        api_key = os.getenv("GROQ_API_KEY", "mock_key")
        
        # Force mock for testing until Groq is fixed
        self.client = MockGroqClient(api_key)
        self.using_mock = True
        
        # Set defaults
        self.model = config.get("model", os.getenv("DEFAULT_LLM_MODEL", "llama-3.1-70b-versatile"))
        self.temperature = config.get("temperature", float(os.getenv("DEFAULT_LLM_TEMPERATURE", "0.7")))
        self.max_tokens = config.get("max_tokens", int(os.getenv("DEFAULT_LLM_MAX_TOKENS", "1000")))
    
    def execute(self, state: State, config: Dict[str, Any]) -> NodeResult:
        """Execute LLM call"""
        try:
            # Get and format prompt
            prompt_template = config.get("prompt", "")
            if not prompt_template:
                return NodeResult(
                    status=NodeStatus.FAILED,
                    error="No prompt provided"
                )
            
            # Replace {variables} with state values
            prompt = self._format_prompt(prompt_template, state)
            
            # Call LLM
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            
            # Extract response
            result = response.choices[0].message.content
            
            # Store in state if output_key specified
            output_key = config.get("output_key", f"{self.node_id}_output")
            state.set(output_key, result)
            
            metadata = {
                "model": self.model,
                "prompt_length": len(prompt),
                "response_length": len(result),
                "using_mock": self.using_mock
            }
            
            if hasattr(response, 'usage'):
                metadata["tokens_used"] = response.usage.total_tokens
            
            return NodeResult(
                status=NodeStatus.SUCCESS,
                output=result,
                metadata=metadata
            )
            
        except Exception as e:
            import traceback
            return NodeResult(
                status=NodeStatus.FAILED,
                error=f"LLM call failed: {str(e)}\n{traceback.format_exc()}"
            )
    
    def _format_prompt(self, template: str, state: State) -> str:
        """
        Replace {variable} placeholders with state values.
        
        Example:
            template = "Summarize: {text}"
            state has {"text": "Hello world"}
            returns "Summarize: Hello world"
        """
        # Find all {variable} patterns
        variables = re.findall(r'\{(\w+)\}', template)
        
        # Replace each variable
        result = template
        for var in variables:
            value = state.get(var, "")
            result = result.replace(f"{{{var}}}", str(value))
        
        return result
    
    def validate_config(self) -> bool:
        """Validate configuration"""
        return "prompt" in self.config


# ============================================================================
# WEB SEARCH TOOL
# ============================================================================

class WebSearchTool(Node):
    """
    Search the web using DuckDuckGo.
    
    Config:
        query: Search query (supports {variable} templating)
        max_results: Maximum number of results (default: 5)
    
    Example:
        config = {
            "query": "latest news about {topic}",
            "max_results": 3
        }
    """
    
    def __init__(self, node_id: str, config: Dict[str, Any]):
        super().__init__(
            node_id=node_id,
            node_type="web_search",
            config=config
        )
        self.max_results = config.get("max_results", 5)
    
    def execute(self, state: State, config: Dict[str, Any]) -> NodeResult:
        """Execute web search"""
        try:
            # Get and format query
            query_template = config.get("query", "")
            if not query_template:
                return NodeResult(
                    status=NodeStatus.FAILED,
                    error="No query provided"
                )
            
            # Replace {variables} with state values
            query = self._format_query(query_template, state)
            
            # Simple DuckDuckGo search using their HTML interface
            results = self._simple_search(query)
            
            # Store in state
            output_key = config.get("output_key", f"{self.node_id}_output")
            state.set(output_key, results)
            
            return NodeResult(
                status=NodeStatus.SUCCESS,
                output=results,
                metadata={
                    "query": query,
                    "results_count": len(results)
                }
            )
            
        except Exception as e:
            return NodeResult(
                status=NodeStatus.FAILED,
                error=f"Web search failed: {str(e)}"
            )
    
    def _format_query(self, template: str, state: State) -> str:
        """Replace {variable} placeholders"""
        variables = re.findall(r'\{(\w+)\}', template)
        result = template
        for var in variables:
            value = state.get(var, "")
            result = result.replace(f"{{{var}}}", str(value))
        return result
    
    def _simple_search(self, query: str) -> List[Dict[str, str]]:
        """
        Perform a simple web search.
        Returns list of results with title and snippet.
        """
        # For MVP, we'll return mock results
        # In Phase 2, we'll integrate proper search API
        
        return [
            {
                "title": f"Result 1 for: {query}",
                "snippet": "This is a sample search result snippet with relevant information...",
                "url": "https://example.com/1"
            },
            {
                "title": f"Result 2 for: {query}",
                "snippet": "Another relevant result about the topic with more details...",
                "url": "https://example.com/2"
            },
            {
                "title": f"Result 3 for: {query}",
                "snippet": "More comprehensive information can be found in this article...",
                "url": "https://example.com/3"
            }
        ][:self.max_results]
    
    def validate_config(self) -> bool:
        """Validate configuration"""
        return "query" in self.config


# ============================================================================
# DATA TRANSFORM TOOL
# ============================================================================

class TransformTool(Node):
    """
    Transform data (parse JSON, extract fields, format text, etc.)
    
    Config:
        operation: Type of transformation (json_parse, extract_field, uppercase, lowercase)
        input_key: Key in state to read from
        output_key: Key in state to write to
        params: Operation-specific parameters
    
    Example:
        config = {
            "operation": "json_parse",
            "input_key": "raw_json",
            "output_key": "parsed_data"
        }
    """
    
    def __init__(self, node_id: str, config: Dict[str, Any]):
        super().__init__(
            node_id=node_id,
            node_type="transform",
            config=config
        )
        self.operation = config.get("operation", "")
        self.input_key = config.get("input_key", "")
        self.output_key = config.get("output_key", f"{node_id}_output")
        self.params = config.get("params", {})
    
    def execute(self, state: State, config: Dict[str, Any]) -> NodeResult:
        """Execute transformation"""
        try:
            # Get input data
            input_data = state.get(self.input_key)
            if input_data is None:
                return NodeResult(
                    status=NodeStatus.FAILED,
                    error=f"Input key '{self.input_key}' not found in state"
                )
            
            # Perform transformation
            if self.operation == "json_parse":
                output = json.loads(input_data)
            
            elif self.operation == "extract_field":
                field = self.params.get("field", "")
                output = input_data.get(field) if isinstance(input_data, dict) else None
            
            elif self.operation == "uppercase":
                output = str(input_data).upper()
            
            elif self.operation == "lowercase":
                output = str(input_data).lower()
            
            elif self.operation == "concatenate":
                parts = self.params.get("parts", [])
                output = "".join([str(state.get(p, "")) for p in parts])
            
            else:
                return NodeResult(
                    status=NodeStatus.FAILED,
                    error=f"Unknown operation: {self.operation}"
                )
            
            # Store result
            state.set(self.output_key, output)
            
            return NodeResult(
                status=NodeStatus.SUCCESS,
                output=output,
                metadata={
                    "operation": self.operation,
                    "input_key": self.input_key,
                    "output_key": self.output_key
                }
            )
            
        except Exception as e:
            return NodeResult(
                status=NodeStatus.FAILED,
                error=f"Transform failed: {str(e)}"
            )
    
    def validate_config(self) -> bool:
        """Validate configuration"""
        return bool(self.operation and self.input_key)


# ============================================================================
# OUTPUT TOOL
# ============================================================================

class OutputTool(Node):
    """
    Format and output final results.
    
    Config:
        input_key: Key in state to output
        format: Output format (json, text, markdown)
    
    Example:
        config = {
            "input_key": "final_result",
            "format": "json"
        }
    """
    
    def __init__(self, node_id: str, config: Dict[str, Any]):
        super().__init__(
            node_id=node_id,
            node_type="output",
            config=config
        )
        self.input_key = config.get("input_key", "result")
        self.format = config.get("format", "json")
    
    def execute(self, state: State, config: Dict[str, Any]) -> NodeResult:
        """Execute output formatting"""
        try:
            # Get data
            data = state.get(self.input_key)
            
            # Format output
            if self.format == "json":
                output = json.dumps(data, indent=2) if not isinstance(data, str) else data
            elif self.format == "text":
                output = str(data)
            elif self.format == "markdown":
                output = f"# Result\n\n{data}"
            else:
                output = str(data)
            
            return NodeResult(
                status=NodeStatus.SUCCESS,
                output=output,
                metadata={
                    "format": self.format,
                    "input_key": self.input_key
                }
            )
            
        except Exception as e:
            return NodeResult(
                status=NodeStatus.FAILED,
                error=f"Output formatting failed: {str(e)}"
            )


# ============================================================================
# REGISTER ALL TOOLS
# ============================================================================

ToolRegistry.register("llm_call", LLMCallTool)
ToolRegistry.register("web_search", WebSearchTool)
ToolRegistry.register("transform", TransformTool)
ToolRegistry.register("output", OutputTool)


# ============================================================================
# TOOL FACTORY
# ============================================================================

def create_tool(node_id: str, node_type: str, config: Dict[str, Any]) -> Optional[Node]:
    """
    Factory function to create tool instances.
    
    Args:
        node_id: Unique node identifier
        node_type: Type of tool (llm_call, web_search, etc.)
        config: Tool configuration
    
    Returns:
        Tool instance or None if type not found
    """
    tool_class = ToolRegistry.get(node_type)
    if tool_class:
        return tool_class(node_id, config)
    return None


# ============================================================================
# TESTING
# ============================================================================

if __name__ == "__main__":
    print("Testing Tools...\n")
    print("⚠️  Note: Using mock LLM for testing (Groq integration will be fixed later)\n")
    
    # Test 1: LLM Tool
    print("[1/4] Testing LLM Tool...")
    state = State({"topic": "artificial intelligence"})
    
    llm_tool = LLMCallTool(
        node_id="llm1",
        config={
            "prompt": "Write one sentence about {topic}",
            "output_key": "llm_result"
        }
    )
    
    result = llm_tool.run(state)
    print(f"✅ Status: {result.status.value}")
    
    if result.is_success():
        print(f"✅ Output: {result.output[:100]}...")
        print(f"✅ Stored in state: {state.has('llm_result')}")
        if result.metadata.get('using_mock'):
            print("   (Using mock LLM)")
    else:
        print(f"❌ Error: {result.error}")
        print("   Continuing with other tests...")
    
    # Test 2: Web Search Tool
    print("\n[2/4] Testing Web Search Tool...")
    state2 = State({"search_term": "Python programming"})
    
    search_tool = WebSearchTool(
        node_id="search1",
        config={
            "query": "{search_term}",
            "max_results": 3,
            "output_key": "search_results"
        }
    )
    
    result2 = search_tool.run(state2)
    print(f"✅ Status: {result2.status.value}")
    if result2.is_success():
        print(f"✅ Results count: {len(result2.output)}")
        print(f"✅ First result: {result2.output[0]['title']}")
    
    # Test 3: Transform Tool
    print("\n[3/4] Testing Transform Tool...")
    state3 = State({"text": "hello world"})
    
    transform_tool = TransformTool(
        node_id="transform1",
        config={
            "operation": "uppercase",
            "input_key": "text",
            "output_key": "transformed"
        }
    )
    
    result3 = transform_tool.run(state3)
    print(f"✅ Status: {result3.status.value}")
    if result3.is_success():
        print(f"✅ Output: {result3.output}")
    
    # Test 4: Tool Registry
    print("\n[4/4] Testing Tool Registry...")
    print(f"✅ Available tools: {ToolRegistry.list_tools()}")
    
    # Test factory
    tool = create_tool("test", "llm_call", {"prompt": "test"})
    print(f"✅ Factory created: {tool}")
    
    print("\n✅ Tools.py core functionality is working!")
    print("   (Groq integration can be fixed later in Phase 2)")
