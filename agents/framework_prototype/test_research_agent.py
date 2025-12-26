"""
Test script for the Research & Content Generation Agent
This demonstrates a real-world agent workflow with multiple steps
"""

from orchestrator.executor import WorkflowExecutor

def main():
    print("=" * 70)
    print("🔬 Research & Content Generation Agent")
    print("=" * 70)
    print()
    
    # Initialize executor
    executor = WorkflowExecutor()
    
    # Test with different topics
    topics = [
        "artificial intelligence trends 2024",
        "quantum computing breakthroughs",
        "sustainable energy solutions"
    ]
    
    for i, topic in enumerate(topics, 1):
        print(f"\n{'='*70}")
        print(f"📊 Research Run #{i}: {topic}")
        print(f"{'='*70}\n")
        
        # Execute workflow
        execution = executor.execute_flow_file(
            "research_agent_workflow.yaml",
            {"topic": topic}
        )
        
        # Display results
        print(f"\n✅ Execution Status: {execution.status}")
        print(f"⏱️  Duration: {execution.get_duration():.2f}s")
        
        if execution.status == "completed":
            print("\n" + "=" * 70)
            print("📋 RESULTS")
            print("=" * 70)
            
            # Show summary
            summary = execution.state.get("summary")
            if summary:
                print("\n📝 SUMMARY:")
                print("-" * 70)
                print(summary)
                print("-" * 70)
            
            # Show insights
            insights = execution.state.get("insights")
            if insights:
                print("\n💡 KEY INSIGHTS:")
                print("-" * 70)
                print(insights)
                print("-" * 70)
            
            # Show analysis
            analysis = execution.state.get("analysis")
            if analysis:
                print("\n📊 ANALYSIS:")
                print("-" * 70)
                print(analysis)
                print("-" * 70)
            
            # Show final report
            final_report = execution.state.get("final_report")
            if final_report:
                print("\n📋 FINAL REPORT:")
                print("-" * 70)
                import json
                if isinstance(final_report, dict):
                    print(json.dumps(final_report, indent=2, ensure_ascii=False))
                else:
                    print(final_report)
                print("-" * 70)
            
            # Show all state keys for debugging
            print(f"\n🔑 All Available Keys: {list(execution.state.get_all().keys())}")
            print("\n💡 Tip: Use 'python view_results.py research' to see ALL results in detail")
        else:
            print(f"\n❌ Execution failed: {execution.error}")
        
        print("\n" + "=" * 70)

if __name__ == "__main__":
    main()

