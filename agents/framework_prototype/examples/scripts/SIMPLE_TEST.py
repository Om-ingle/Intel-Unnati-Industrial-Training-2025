"""
🎯 SIMPLE TEST - See agent results quickly
Just run this to see what the agents produce!
"""

from pathlib import Path
import sys

# Add root to python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from orchestrator.executor import WorkflowExecutor

print("\n" + "="*80)
print("  🤖 SIMPLE AGENT TEST")
print("="*80)

executor = WorkflowExecutor()

# Test 1: Research Agent
print("\n" + "-"*80)
print("  TEST 1: Research Agent")
print("-"*80)
print("\n⏳ Running...")

execution = executor.execute_flow_file(
    "research_agent_workflow.yaml",
    {"topic": "artificial intelligence"}
)

print(f"✅ Status: {execution.status}\n")

if execution.status == "completed":
    summary = execution.state.get("summary")
    insights = execution.state.get("insights")
    
    print("📝 SUMMARY:")
    print(summary if summary else "(No summary)")
    
    print("\n💡 INSIGHTS:")
    print(insights if insights else "(No insights)")
else:
    print(f"❌ Error: {execution.error}")

# Test 2: Q&A Agent
print("\n\n" + "-"*80)
print("  TEST 2: Q&A Agent")
print("-"*80)
print("\n⏳ Running...")

execution = executor.execute_flow_file(
    "smart_qa_agent_workflow.yaml",
    {"question": "What is machine learning?"}
)

print(f"✅ Status: {execution.status}\n")

if execution.status == "completed":
    answer = execution.state.get("enhanced_answer")
    
    print("💡 ANSWER:")
    print(answer if answer else "(No answer)")
else:
    print(f"❌ Error: {execution.error}")

print("\n" + "="*80)
print("  ✅ Done! Check the outputs above.")
print("="*80)
print("\n💡 For detailed results, run: python view_results.py")
print()

