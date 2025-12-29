"""
🎯 Agent Framework Demo - Showcase All Agent Workflows
This script demonstrates the capabilities of your agent framework
"""

import sys
from pathlib import Path

# Handle imports - Add root directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from orchestrator.executor import WorkflowExecutor
import json

def print_header(title):
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)

def print_section(title):
    print(f"\n{'─' * 80}")
    print(f"  {title}")
    print(f"{'─' * 80}")

def demo_research_agent(executor):
    """Demo: Research & Content Generation Agent"""
    print_header("🔬 Research & Content Generation Agent")
    
    topic = "artificial intelligence trends 2024"
    print(f"\n📌 Research Topic: {topic}\n")
    
    execution = executor.execute_flow_file(
        "research_agent_workflow.yaml",
        {"topic": topic}
    )
    
    print_section("Execution Results")
    print(f"Status: {execution.status}")
    print(f"Duration: {execution.get_duration():.2f}s")
    
    if execution.status == "completed":
        summary = execution.state.get("summary")
        insights = execution.state.get("insights")
        
        if summary:
            print_section("📝 Generated Summary")
            print(summary)
        
        if insights:
            print_section("💡 Key Insights")
            print(insights)
        
        print(f"\n💡 Tip: Run 'python view_results.py research' to see ALL results")
    else:
        print(f"❌ Error: {execution.error}")

def demo_content_creator(executor):
    """Demo: Content Creator Agent"""
    print_header("✍️  Content Creator Agent")
    
    topic = "the future of renewable energy"
    print(f"\n📌 Content Topic: {topic}\n")
    
    execution = executor.execute_flow_file(
        "content_creator_agent_workflow.yaml",
        {"topic": topic}
    )
    
    print_section("Execution Results")
    print(f"Status: {execution.status}")
    print(f"Duration: {execution.get_duration():.2f}s")
    
    if execution.status == "completed":
        article = execution.state.get("final_article")
        outline = execution.state.get("outline")
        introduction = execution.state.get("introduction")
        main_content = execution.state.get("main_content")
        conclusion = execution.state.get("conclusion")
        
        if outline:
            print_section("📋 Generated Outline")
            print(outline)
        
        if introduction:
            print_section("📝 Introduction")
            print(introduction)
        
        if main_content:
            print_section("📄 Main Content")
            print(main_content)
        
        if conclusion:
            print_section("🏁 Conclusion")
            print(conclusion)
        
        if article:
            print_section("📚 Final Article")
            import json
            if isinstance(article, dict):
                print(json.dumps(article, indent=2, ensure_ascii=False))
            else:
                print(article)
        
        print(f"\n💡 Tip: Run 'python view_results.py content' to see ALL results")
    else:
        print(f"❌ Error: {execution.error}")

def demo_qa_agent(executor):
    """Demo: Smart Q&A Agent"""
    print_header("❓ Smart Q&A Agent")
    
    question = "What are the latest developments in quantum computing?"
    print(f"\n❓ Question: {question}\n")
    
    execution = executor.execute_flow_file(
        "smart_qa_agent_workflow.yaml",
        {"question": question}
    )
    
    print_section("Execution Results")
    print(f"Status: {execution.status}")
    print(f"Duration: {execution.get_duration():.2f}s")
    
    if execution.status == "completed":
        answer = execution.state.get("enhanced_answer")
        followups = execution.state.get("followup_questions")
        
        if answer:
            print_section("💡 Answer")
            print(answer)
        
        if followups:
            print_section("🔗 Suggested Follow-up Questions")
            print(followups)
        
        print(f"\n💡 Tip: Run 'python view_results.py qa' to see ALL results")
    else:
        print(f"❌ Error: {execution.error}")

def main():
    print("\n" + "=" * 80)
    print("  🤖 AGENT FRAMEWORK DEMONSTRATION")
    print("  Showcasing Real-World Agent Workflows")
    print("=" * 80)
    
    # Initialize executor
    print("\n⚙️  Initializing Workflow Executor...")
    executor = WorkflowExecutor()
    print("✅ Executor ready!\n")
    
    # Run demos
    try:
        demo_research_agent(executor)
        print("\n\n")
        
        demo_content_creator(executor)
        print("\n\n")
        
        demo_qa_agent(executor)
        
    except Exception as e:
        print(f"\n❌ Error during execution: {str(e)}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 80)
    print("  ✅ Demo Complete!")
    print("=" * 80)
    print("\n💡 Tip: You can modify the workflows in the YAML files")
    print("   and test with your own topics/questions!\n")

if __name__ == "__main__":
    main()

