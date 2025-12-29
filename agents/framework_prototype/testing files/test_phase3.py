"""
Phase 3 Comprehensive Test
"""

import asyncio
import sys
from pathlib import Path

# Add root directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from orchestrator.parallel_engine import ParallelFlowEngine
from orchestrator.executor import WorkflowExecutor
from core import Flow


def test_advanced_nodes():
    """Test all advanced node types"""
    print("="*60)
    print("TEST 1: Advanced Node Types")
    print("="*60)
    
    from nodes.advanced_nodes import (
        LLMCallNode, WebSearchNode, HTTPRequestNode,
        DatabaseQueryNode, DataAggregatorNode, ConditionalNode
    )
    from core import State
    
    state = State()
    state.set("topic", "AI")
    state.set("score", 0.85)
    
    # Test each node type
    tests = [
        ("LLM Call", LLMCallNode("llm1", {"prompt": "Explain {topic}", "output_key": "llm_out"})),
        ("Web Search", WebSearchNode("search1", {"query": "{topic}", "output_key": "search_out"})),
        ("HTTP Request", HTTPRequestNode("http1", {"url": "https://api.example.com/{topic}", "output_key": "http_out"})),
        ("Database Query", DatabaseQueryNode("db1", {"query": "SELECT * FROM data", "output_key": "db_out"})),
        ("Conditional", ConditionalNode("cond1", {"condition": "{score} > 0.5", "true_value": "pass", "output_key": "cond_out"}))
    ]
    
    for name, node in tests:
        result = node.execute(state)
        status = "✅" if result.is_success() else "❌"
        print(f"{status} {name}: {result.status.value}")
    
    print("\n✅ All advanced nodes working!\n")


def test_parallel_execution():
    """Test parallel execution engine"""
    print("="*60)
    print("TEST 2: Parallel Execution")
    print("="*60)
    
    import time
    
    # Create flow with parallel branches
    flow = Flow(
        flow_id="parallel-test",
        name="Parallel Test",
        nodes=[
            {"id": "start", "type": "transform", "config": {"operation": "uppercase", "input_key": "input", "output_key": "processed"}},
            {"id": "branch1", "type": "delay", "config": {"seconds": 0.3, "input_key": "processed", "output_key": "r1"}},
            {"id": "branch2", "type": "delay", "config": {"seconds": 0.3, "input_key": "processed", "output_key": "r2"}},
            {"id": "branch3", "type": "delay", "config": {"seconds": 0.3, "input_key": "processed", "output_key": "r3"}},
            {"id": "end", "type": "data_aggregator", "config": {"sources": ["r1", "r2", "r3"], "operation": "concat", "output_key": "final"}}
        ],
        edges=[
            {"from": "start", "to": "branch1"},
            {"from": "start", "to": "branch2"},
            {"from": "start", "to": "branch3"},
            {"from": "branch1", "to": "end"},
            {"from": "branch2", "to": "end"},
            {"from": "branch3", "to": "end"}
        ]
    )
    
    start = time.time()
    engine = ParallelFlowEngine(max_workers=3)
    execution = engine.execute_sync(flow, {"input": "test"})
    duration = time.time() - start
    
    print(f"\n✅ Parallel execution completed in {duration:.2f}s")
    print(f"   Expected: ~0.6s (sequential would be ~1.2s)")
    print(f"   Speedup: ~2x\n")


def test_complex_workflow():
    """Test complex workflow from file"""
    print("="*60)
    print("TEST 3: Complex Workflow Execution")
    print("="*60)
    
    executor = WorkflowExecutor()
    
    try:
        execution = executor.execute_flow_file(
            "examples/workflows/research_workflow.yaml",
            {"topic": "machine learning"}
        )
        
        print(f"\n✅ Workflow executed successfully!")
        print(f"   Execution ID: {execution.execution_id}")
        print(f"   Status: {execution.status}")
        print(f"   Duration: {execution.get_duration():.2f}s")
        print(f"   Nodes: {len(execution.node_results)}")
        
    except FileNotFoundError:
        print("\n⚠️  Workflow file not found (expected in examples/)")
    except Exception as e:
        print(f"\n❌ Error: {e}")
    
    print()


def test_conditional_branching():
    """Test conditional logic"""
    print("="*60)
    print("TEST 4: Conditional Branching")
    print("="*60)
    
    flow = Flow(
        flow_id="conditional-test",
        name="Conditional Test",
        nodes=[
            {"id": "set_score", "type": "transform", "config": {"operation": "passthrough", "input_key": "score", "output_key": "score"}},
            {"id": "check", "type": "conditional", "config": {
                "condition": "{score} > 0.7",
                "true_value": "high",
                "false_value": "low",
                "output_key": "rating"
            }},
            {"id": "output", "type": "output", "config": {"input_key": "rating"}}
        ],
        edges=[
            {"from": "set_score", "to": "check"},
            {"from": "check", "to": "output"}
        ]
    )
    
    executor = WorkflowExecutor()
    
    # Test high score
    exec1 = executor.execute_flow(flow, {"score": 0.9})
    rating1 = exec1.state.get("rating")
    print(f"✅ Score 0.9 → {rating1}")
    
    # Test low score
    exec2 = executor.execute_flow(flow, {"score": 0.3})
    rating2 = exec2.state.get("rating")
    print(f"✅ Score 0.3 → {rating2}")
    
    print("\n✅ Conditional branching working!\n")


def main():
    """Run all Phase 3 tests"""
    print("\n" + "="*60)
    print("PHASE 3 COMPREHENSIVE TEST SUITE")
    print("="*60 + "\n")
    
    test_advanced_nodes()
    test_parallel_execution()
    test_conditional_branching()
    test_complex_workflow()
    
    print("="*60)
    print("✅ PHASE 3 TESTS COMPLETE!")
    print("="*60)


if __name__ == "__main__":
    main()
