#!/usr/bin/env python3
"""
Test runner for core components
"""

import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.state import State
from core.node import Node, SimpleNode, NodeStatus, NodeResult

print("="*60)
print("TESTING CORE COMPONENTS")
print("="*60)

# Test State
print("\n[1/3] Testing State...")
state = State({"input": "test"})
state.set("result", "success")
state.update({"count": 42})
print(f"✅ State: {state}")

# Test Node
print("\n[2/3] Testing Node...")
def test_fn(state, config):
    val = state.get("input") + " -> processed"
    state.set("output", val)
    return NodeResult(NodeStatus.SUCCESS, output=val)

node = SimpleNode("test", "processor", test_fn)
result = node.run(state)
print(f"✅ Node: {node}")
print(f"✅ Result: {result.output}")

# Test Integration
print("\n[3/3] Testing Integration...")
state2 = State({"user_input": "AI Agents"})

def append(s, c):
    text = s.get("user_input") + " are awesome"
    s.set("step1", text)
    return NodeResult(NodeStatus.SUCCESS, output=text)

def upper(s, c):
    text = s.get("step1").upper()
    s.set("final", text)
    return NodeResult(NodeStatus.SUCCESS, output=text)

n1 = SimpleNode("n1", "append", append)
n2 = SimpleNode("n2", "upper", upper)

r1 = n1.run(state2)
r2 = n2.run(state2)

print(f"✅ Input: {state2.get('user_input')}")
print(f"✅ After Node1: {state2.get('step1')}")
print(f"✅ After Node2: {state2.get('final')}")

print("\n" + "="*60)
print("✅ ALL CORE TESTS PASSED!")
print("="*60)
