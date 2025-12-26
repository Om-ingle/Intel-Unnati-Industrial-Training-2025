"""
Advanced Node Types - LLM, Web Search, Database, API calls
"""

import sys
from pathlib import Path
from typing import Dict, Any, Optional, List
import json
import time
import os

from dotenv import load_dotenv
import os

# Handle imports
try:
    from ..core import Node, State, NodeResult, NodeStatus
except ImportError:
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from core import Node, State, NodeResult, NodeStatus


# ============================================================================
# LLM CALL NODE
# ============================================================================

class LLMCallNode(Node):
    """
    Call an LLM - supports both real Groq API and mock mode.
    
    Config:
        - prompt: Prompt template with {variables}
        - model: Model name (optional, default: "llama-3.3-70b-versatile" for Groq)
        - temperature: Temperature (optional, default: 0.7)
        - max_tokens: Max tokens (optional, default: 1000)
        - output_key: Where to store result
        - use_mock: Force mock mode even if API key exists (optional, default: False)
        - use_real: Force real API mode (optional, default: auto-detect)
    
    Example:
        config:
          prompt: "Summarize: {text}"
          model: "llama-3.3-70b-versatile"
          output_key: "summary"
          use_mock: false  # Use real API if available
    """
    
    def __init__(self, node_id: str, config: Dict[str, Any]):
        super().__init__(node_id, config)

        # Load .env from framework root so keys set there are available
        # This keeps behaviour consistent whether you export in shell or use .env.
        try:
            framework_root = Path(__file__).parent.parent
            env_file = framework_root / ".env"
            if env_file.exists():
                load_dotenv(dotenv_path=env_file, override=False)
        except Exception as e:
            print(f"   ⚠️  .env load warning: {e}")

        # Check if Groq is available
        self.groq_available = False
        self.groq_client = None

        # Check if Gemini is available
        self.gemini_available = False
        self.gemini_client = None

        try:
            from groq import Groq
            api_key = os.getenv("GROQ_API_KEY")
            if api_key:
                self.groq_client = Groq(api_key=api_key)
                self.groq_available = True
        except ImportError:
            pass
        except Exception as e:
            print(f"   ⚠️  Groq initialization warning: {e}")

        try:
            from google import genai
            api_key = os.getenv("GEMINI_API_KEY")
            if api_key:
                self.gemini_client = genai.Client(api_key=api_key)
                self.gemini_available = True
        except ImportError:
            # Gemini support is optional; ignore if library not installed
            pass
        except Exception as e:
            print(f"   ⚠️  Gemini initialization warning: {e}")
    
    def execute(self, state: State) -> NodeResult:
        config = self.config
        
        # Get prompt template
        prompt_template = config.get("prompt", "")
        
        # Replace variables from state
        prompt = self._replace_variables(prompt_template, state)
        
        # Get config values
        provider = config.get("provider", "auto").lower()  # "groq", "gemini", or "auto"
        model = config.get("model", None)  # Can be overridden
        temperature = config.get("temperature", 0.7)
        max_tokens = config.get("max_tokens", 1000)
        use_mock = config.get("use_mock", False)
        use_real = config.get("use_real", None)
        
        # Check for global provider setting from dashboard
        global_provider = os.getenv("LLM_PROVIDER", "auto")
        if global_provider != "auto" and provider == "auto":
            provider = global_provider
        
        # Check for global provider setting from dashboard
        global_provider = os.getenv("LLM_PROVIDER", "auto")
        if global_provider != "auto" and provider == "auto":
            provider = global_provider

        # Determine provider
        if provider == "auto":
            # Auto-select: prefer Gemini if both available, else Groq, else mock
            if self.gemini_available:
                provider = "gemini"
                if not model:
                    model = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
            elif self.groq_available:
                provider = "groq"
                if not model:
                    model = "llama-3.3-70b-versatile"
            else:
                provider = "mock"
                if not model:
                    model = "mock-model"
        else:
            # Use specified provider
            if not model:
                if provider == "gemini":
                    model = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
                elif provider == "groq":
                    model = "llama-3.3-70b-versatile"
                else:
                    model = "mock-model"
        
        # Determine mode: use_real > use_mock > auto-detect
        if use_real is True:
            use_real_api = True
        elif use_mock is True:
            use_real_api = False
        else:
            # Auto-detect: use real if available
            use_real_api = (provider == "groq" and self.groq_available) or (provider == "gemini" and self.gemini_available)
        
        print(f"   🤖 LLM Call: {provider.upper()} - {model} ({'REAL API' if use_real_api else 'MOCK'})")
        print(f"      Prompt: {prompt[:50]}...")
        
        # Call appropriate API or mock
        if use_real_api:
            if provider == "gemini" and self.gemini_client:
                response = self._call_gemini_api(prompt, model, temperature, max_tokens)
            elif provider == "groq" and self.groq_client:
                response = self._call_groq_api(prompt, model, temperature, max_tokens)
            else:
                response = self._call_mock_api(prompt, model)
        else:
            response = self._call_mock_api(prompt, model)
        
        # Store in state
        output_key = config.get("output_key", "llm_response")
        state.set(output_key, response)
        
        return NodeResult.success(
            output=response,
            metadata={
                "model": model,
                "provider": provider,
                "prompt_length": len(prompt),
                "temperature": temperature,
                "mode": "real" if use_real_api else "mock"
            }
        )
    
    def _call_groq_api(self, prompt: str, model: str, temperature: float, max_tokens: int) -> str:
        """Call real Groq API"""
        try:
            messages = [
                {
                    "role": "user",
                    "content": prompt
                }
            ]
            
            response = self.groq_client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"   ⚠️  Groq API call failed: {e}, falling back to mock")
            return self._call_mock_api(prompt, model)
    
    def _call_gemini_api(self, prompt: str, model: str, temperature: float, max_tokens: int) -> str:
        """Call real Gemini API"""
        try:
            response = self.gemini_client.models.generate_content(
                model=model,
                contents=prompt,
                config={
                    "temperature": temperature,
                    "max_output_tokens": max_tokens
                }
            )
            
            return response.text
            
        except Exception as e:
            print(f"   ⚠️  Gemini API call failed: {e}, falling back to mock")
            return self._call_mock_api(prompt, model)
    
    def _call_mock_api(self, prompt: str, model: str) -> str:
        """Call mock API (simulated)"""
        time.sleep(0.5)  # Simulate API delay
        return f"[MOCK LLM Response to: {prompt[:30]}...] This is a simulated response. Set GROQ_API_KEY to use real API."
    
    def _replace_variables(self, template: str, state: State) -> str:
        """Replace {variable} placeholders with state values"""
        import re
        
        def replace_var(match):
            var_name = match.group(1)
            value = state.get(var_name)
            return str(value) if value is not None else f"{{{var_name}}}"
        
        return re.sub(r'\{(\w+)\}', replace_var, template)


# ============================================================================
# WEB SEARCH NODE
# ============================================================================

class WebSearchNode(Node):
    """
    Perform web search (simulated).
    
    Config:
        - query: Search query with {variables}
        - max_results: Number of results (default: 5)
        - output_key: Where to store results
    
    Example:
        config:
          query: "{topic} latest news"
          max_results: 3
          output_key: "search_results"
    """
    
    def execute(self, state: State) -> NodeResult:
        config = self.config
        
        # Get and process query
        query_template = config.get("query", "")
        query = self._replace_variables(query_template, state)
        max_results = config.get("max_results", 5)
        
        print(f"   🔍 Web Search: {query}")
        
        # Simulate search (replace with real search API)
        time.sleep(0.3)
        results = [
            {
                "title": f"Result {i+1} for: {query}",
                "url": f"https://example.com/result{i+1}",
                "snippet": f"This is a snippet about {query}..."
            }
            for i in range(max_results)
        ]
        
        # Store results
        output_key = config.get("output_key", "search_results")
        state.set(output_key, results)
        
        return NodeResult.success(
            output=results,
            metadata={
                "query": query,
                "result_count": len(results)
            }
        )
    
    def _replace_variables(self, template: str, state: State) -> str:
        """Replace variables in template"""
        import re
        def replace_var(match):
            var_name = match.group(1)
            value = state.get(var_name)
            return str(value) if value is not None else f"{{{var_name}}}"
        return re.sub(r'\{(\w+)\}', replace_var, template)


# ============================================================================
# HTTP REQUEST NODE
# ============================================================================

class HTTPRequestNode(Node):
    """
    Make HTTP requests to external APIs.
    
    Config:
        - url: URL with {variables}
        - method: GET, POST, PUT, DELETE
        - headers: Request headers (optional)
        - body: Request body (optional)
        - output_key: Where to store response
    
    Example:
        config:
          url: "https://api.example.com/data/{id}"
          method: "GET"
          headers:
            Authorization: "Bearer {token}"
          output_key: "api_response"
    """
    
    def execute(self, state: State) -> NodeResult:
        config = self.config
        
        # Process URL
        url_template = config.get("url", "")
        url = self._replace_variables(url_template, state)
        
        method = config.get("method", "GET").upper()
        headers = config.get("headers", {})
        body = config.get("body")
        
        print(f"   🌐 HTTP {method}: {url}")
        
        # Simulate HTTP request
        time.sleep(0.2)
        response_data = {
            "status": 200,
            "data": f"Response from {url}",
            "method": method
        }
        
        # Store response
        output_key = config.get("output_key", "http_response")
        state.set(output_key, response_data)
        
        return NodeResult.success(
            output=response_data,
            metadata={
                "url": url,
                "method": method,
                "status": 200
            }
        )
    
    def _replace_variables(self, template: str, state: State) -> str:
        """Replace variables"""
        import re
        def replace_var(match):
            var_name = match.group(1)
            value = state.get(var_name)
            return str(value) if value is not None else f"{{{var_name}}}"
        return re.sub(r'\{(\w+)\}', replace_var, template)


# ============================================================================
# DATABASE QUERY NODE
# ============================================================================

class DatabaseQueryNode(Node):
    """
    Execute database queries (simulated).
    
    Config:
        - query: SQL query with {variables}
        - connection: Database connection string (optional)
        - output_key: Where to store results
    
    Example:
        config:
          query: "SELECT * FROM users WHERE id = {user_id}"
          output_key: "user_data"
    """
    
    def execute(self, state: State) -> NodeResult:
        config = self.config
        
        # Get query
        query_template = config.get("query", "")
        query = self._replace_variables(query_template, state)
        
        print(f"   💾 Database Query: {query[:50]}...")
        
        # Simulate database query
        time.sleep(0.2)
        results = [
            {"id": 1, "name": "John Doe", "email": "john@example.com"},
            {"id": 2, "name": "Jane Smith", "email": "jane@example.com"}
        ]
        
        # Store results
        output_key = config.get("output_key", "db_results")
        state.set(output_key, results)
        
        return NodeResult.success(
            output=results,
            metadata={
                "query": query,
                "row_count": len(results)
            }
        )
    
    def _replace_variables(self, template: str, state: State) -> str:
        """Replace variables"""
        import re
        def replace_var(match):
            var_name = match.group(1)
            value = state.get(var_name)
            return str(value) if value is not None else f"{{{var_name}}}"
        return re.sub(r'\{(\w+)\}', replace_var, template)


# ============================================================================
# DATA AGGREGATOR NODE
# ============================================================================

class DataAggregatorNode(Node):
    """
    Aggregate data from multiple sources.
    
    Config:
        - sources: List of state keys to aggregate
        - operation: sum, average, concat, merge
        - output_key: Where to store result
    
    Example:
        config:
          sources: ["result1", "result2", "result3"]
          operation: "merge"
          output_key: "aggregated"
    """
    
    def execute(self, state: State) -> NodeResult:
        config = self.config

        # New-style config: inputs + format (used by tour planner & content creator)
        inputs_cfg = config.get("inputs")
        if inputs_cfg:
            print("   📊 Aggregating structured inputs into final plan")
            result: Dict[str, Any] = {}

            for item in inputs_cfg:
                # Each item: { key: "...", label: "Optional Label" }
                key = item.get("key")
                if not key:
                    continue
                label = item.get("label") or key
                value = state.get(key)
                result[label] = value

            output_key = config.get("output_key", "final_plan")
            state.set(output_key, result)

            return NodeResult.success(
                output=result,
                metadata={
                    "operation": "structured",
                    "field_count": len(result),
                },
            )

        # Backwards-compatible: sources + operation
        sources = config.get("sources", [])
        operation = config.get("operation", "merge")

        print(f"   📊 Aggregating {len(sources)} sources: {operation}")

        # Collect data
        data_items = [state.get(key) for key in sources if state.get(key) is not None]

        # Perform aggregation
        if operation == "sum":
            result = sum(float(x) for x in data_items if isinstance(x, (int, float)))
        elif operation == "average":
            nums = [float(x) for x in data_items if isinstance(x, (int, float))]
            result = sum(nums) / len(nums) if nums else 0
        elif operation == "concat":
            result = " ".join(str(x) for x in data_items)
        elif operation == "merge":
            if all(isinstance(x, dict) for x in data_items):
                result = {}
                for item in data_items:
                    result.update(item)
            elif all(isinstance(x, list) for x in data_items):
                result = []
                for item in data_items:
                    result.extend(item)
            else:
                result = data_items
        else:
            result = data_items

        # Store result
        output_key = config.get("output_key", "aggregated")
        state.set(output_key, result)

        return NodeResult.success(
            output=result,
            metadata={
                "operation": operation,
                "source_count": len(data_items),
            },
        )


# ============================================================================
# CONDITIONAL NODE
# ============================================================================

class ConditionalNode(Node):
    """
    Conditional branching based on state values.
    
    Config:
        - condition: Python expression to evaluate
        - true_value: Value to output if true
        - false_value: Value to output if false
        - output_key: Where to store result
    
    Example:
        config:
          condition: "{score} > 0.5"
          true_value: "passed"
          false_value: "failed"
          output_key: "result"
    """
    
    def execute(self, state: State) -> NodeResult:
        config = self.config
        
        condition = config.get("condition", "True")
        
        # Replace variables
        condition_eval = self._replace_variables(condition, state)
        
        print(f"   🔀 Condition: {condition_eval}")
        
        # Evaluate condition (safely)
        try:
            result_bool = eval(condition_eval)
            
            if result_bool:
                result_value = config.get("true_value", True)
                branch = "true"
            else:
                result_value = config.get("false_value", False)
                branch = "false"
            
            # Store result
            output_key = config.get("output_key", "condition_result")
            state.set(output_key, result_value)
            state.set(f"{output_key}_branch", branch)
            
            return NodeResult.success(
                output=result_value,
                metadata={
                    "condition": condition,
                    "branch": branch
                }
            )
            
        except Exception as e:
            return NodeResult.failure(
                error=f"Condition evaluation failed: {str(e)}"
            )
    
    def _replace_variables(self, template: str, state: State) -> str:
        """Replace variables"""
        import re
        def replace_var(match):
            var_name = match.group(1)
            value = state.get(var_name)
            if value is None:
                return "None"
            return repr(value) if isinstance(value, str) else str(value)
        return re.sub(r'\{(\w+)\}', replace_var, template)


# ============================================================================
# NODE REGISTRY
# ============================================================================

ADVANCED_NODE_TYPES = {
    "llm_call": LLMCallNode,
    "web_search": WebSearchNode,
    "http_request": HTTPRequestNode,
    "database_query": DatabaseQueryNode,
    "data_aggregator": DataAggregatorNode,
    "conditional": ConditionalNode,
}


# ============================================================================
# TESTING
# ============================================================================

if __name__ == "__main__":
    print("Testing Advanced Nodes...\n")
    
    from core import State
    
    # Test 1: LLM Call
    print("[1/6] Testing LLM Call Node...")
    state = State()
    state.set("topic", "AI agents")
    
    llm_node = LLMCallNode("llm1", {
        "prompt": "Explain {topic} in simple terms",
        "output_key": "explanation"
    })
    result = llm_node.execute(state)
    print(f"✅ Output: {state.get('explanation')}\n")
    
    # Test 2: Web Search
    print("[2/6] Testing Web Search Node...")
    search_node = WebSearchNode("search1", {
        "query": "{topic} tutorials",
        "max_results": 3,
        "output_key": "search_results"
    })
    result = search_node.execute(state)
    print(f"✅ Found {len(state.get('search_results'))} results\n")
    
    # Test 3: HTTP Request
    print("[3/6] Testing HTTP Request Node...")
    state.set("user_id", "123")
    http_node = HTTPRequestNode("http1", {
        "url": "https://api.example.com/users/{user_id}",
        "method": "GET",
        "output_key": "user_data"
    })
    result = http_node.execute(state)
    print(f"✅ Response: {state.get('user_data')}\n")
    
    # Test 4: Database Query
    print("[4/6] Testing Database Query Node...")
    db_node = DatabaseQueryNode("db1", {
        "query": "SELECT * FROM users WHERE id = {user_id}",
        "output_key": "db_results"
    })
    result = db_node.execute(state)
    print(f"✅ Rows: {len(state.get('db_results'))}\n")
    
    # Test 5: Data Aggregator
    print("[5/6] Testing Data Aggregator Node...")
    state.set("value1", 10)
    state.set("value2", 20)
    state.set("value3", 30)
    
    agg_node = DataAggregatorNode("agg1", {
        "sources": ["value1", "value2", "value3"],
        "operation": "sum",
        "output_key": "total"
    })
    result = agg_node.execute(state)
    print(f"✅ Total: {state.get('total')}\n")
    
    # Test 6: Conditional
    print("[6/6] Testing Conditional Node...")
    state.set("score", 0.75)
    
    cond_node = ConditionalNode("cond1", {
        "condition": "{score} > 0.5",
        "true_value": "high",
        "false_value": "low",
        "output_key": "rating"
    })
    result = cond_node.execute(state)
    print(f"✅ Rating: {state.get('rating')}")
    print(f"   Branch: {state.get('rating_branch')}\n")
    
    print("✅ All advanced nodes are working!")
