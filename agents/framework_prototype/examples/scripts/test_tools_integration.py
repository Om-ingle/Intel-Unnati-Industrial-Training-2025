#!/usr/bin/env python3
"""
Integration test: Build a mini workflow with tools
"""

import sys
from pathlib import Path
# Handle imports - Add root directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core import State, LLMCallTool, TransformTool, OutputTool

print("="*60)
print("TESTING TOOLS INTEGRATION - Mini Workflow")
print("="*60)

# Create a workflow: Input → LLM → Transform → Output
state = State({"user_query": "machine learning"})

print("\n[Step 1] LLM generates description...")
llm = LLMCallTool("llm", {
    "prompt": "Write a brief one-sentence description of {user_query}",
    "output_key": "description"
})
result1 = llm.run(state)
print(f"✅ LLM output: {result1.output[:80]}...")

print("\n[Step 2] Transform to uppercase...")
transform = TransformTool("transform", {
    "operation": "uppercase",
    "input_key": "description",
    "output_key": "final_text"
})
result2 = transform.run(state)
print(f"✅ Transformed: {result2.output[:80]}...")

print("\n[Step 3] Format output...")
output = OutputTool("output", {
    "input_key": "final_text",
    "format": "text"
})
result3 = output.run(state)
print(f"✅ Final output: {result3.output[:80]}...")

print("\n" + "="*60)
print("✅ MINI WORKFLOW COMPLETED SUCCESSFULLY!")
print("="*60)
print(f"\nState contents: {list(state.get_all().keys())}")
