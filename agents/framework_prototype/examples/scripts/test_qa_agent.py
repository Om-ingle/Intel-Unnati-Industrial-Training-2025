"""
Test script for the Smart Q&A Agent
Demonstrates multi-step reasoning and conditional workflows
"""

import sys
from pathlib import Path

# Handle imports - Add root directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from orchestrator.executor import WorkflowExecutor

def main():
    print("=" * 70)
    print("❓ Smart Q&A Agent with Multi-Step Reasoning")
    print("=" * 70)
    print()
    
    # Initialize executor
    executor = WorkflowExecutor()
    
    # Test questions
    questions = [
        "What are the latest developments in quantum computing?",
        "Explain how neural networks work",
        "What is the current state of renewable energy adoption?"
    ]
    
    for i, question in enumerate(questions, 1):
        print(f"\n{'='*70}")
        print(f"💬 Question #{i}: {question}")
        print(f"{'='*70}\n")
        
        # Execute workflow
        execution = executor.execute_flow_file(
            "smart_qa_agent_workflow.yaml",
            {"question": question}
        )
        
        # Display results
        print(f"\n✅ Execution Status: {execution.status}")
        print(f"⏱️  Duration: {execution.get_duration():.2f}s")
        
        if execution.status == "completed":
            print("\n📋 Final Response:")
            print("-" * 70)
            
            # Get final response
            final_response = execution.state.get("final_response")
            if final_response:
                import json
                if isinstance(final_response, dict):
                    print(json.dumps(final_response, indent=2))
                else:
                    print(final_response)
            else:
                # Fallback: show components
                answer = execution.state.get("enhanced_answer")
                followups = execution.state.get("followup_questions")
                
                if answer:
                    print("\n💡 Answer:")
                    print(answer)
                
                if followups:
                    print("\n🔗 Follow-up Questions:")
                    print(followups)
            
            print("\n" + "-" * 70)
            
            # Show all state keys
            print(f"\n🔑 All Available Keys: {list(execution.state.get_all().keys())}")
            print("\n💡 Tip: Use 'python view_results.py qa' to see ALL results in detail")
        else:
            print(f"\n❌ Execution failed: {execution.error}")
        
        print("\n" + "=" * 70)

if __name__ == "__main__":
    main()

