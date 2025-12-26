"""
📊 View Full Results - See all agent outputs clearly
This script shows complete results without truncation
"""

from orchestrator.executor import WorkflowExecutor
import json

def print_full_result(title, content):
    """Print a result section with full content"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)
    if content:
        if isinstance(content, dict):
            print(json.dumps(content, indent=2, ensure_ascii=False))
        else:
            print(str(content))
    else:
        print("(No content available)")
    print("=" * 80)

def show_all_state(execution):
    """Show everything in the state"""
    print("\n" + "🔍" * 40)
    print("  COMPLETE STATE CONTENTS")
    print("🔍" * 40)
    
    all_data = execution.state.get_all()
    
    if not all_data:
        print("State is empty!")
        return
    
    for key, value in all_data.items():
        print_full_result(f"📌 Key: '{key}'", value)

def test_research_agent():
    """Test Research Agent and show full results"""
    print("\n" + "🤖" * 40)
    print("  RESEARCH & CONTENT GENERATION AGENT")
    print("🤖" * 40)
    
    executor = WorkflowExecutor()
    
    topic = "artificial intelligence trends 2024"
    print(f"\n📌 Topic: {topic}\n")
    print("⏳ Executing workflow...\n")
    
    execution = executor.execute_flow_file(
        "research_agent_workflow.yaml",
        {"topic": topic}
    )
    
    print(f"✅ Status: {execution.status}")
    print(f"⏱️  Duration: {execution.get_duration():.2f}s\n")
    
    if execution.status == "completed":
        # Show individual results
        search_results = execution.state.get("search_results")
        analysis = execution.state.get("analysis")
        summary = execution.state.get("summary")
        insights = execution.state.get("insights")
        final_report = execution.state.get("final_report")
        
        if search_results:
            print_full_result("🔍 Search Results", search_results)
        
        if analysis:
            print_full_result("📊 Analysis", analysis)
        
        if summary:
            print_full_result("📝 Summary", summary)
        
        if insights:
            print_full_result("💡 Key Insights", insights)
        
        if final_report:
            print_full_result("📋 Final Report", final_report)
        
        # Show everything
        show_all_state(execution)
    else:
        print(f"❌ Error: {execution.error}")

def test_qa_agent():
    """Test Q&A Agent and show full results"""
    print("\n" + "🤖" * 40)
    print("  SMART Q&A AGENT")
    print("🤖" * 40)
    
    executor = WorkflowExecutor()
    
    question = "What are the latest developments in quantum computing?"
    print(f"\n❓ Question: {question}\n")
    print("⏳ Executing workflow...\n")
    
    execution = executor.execute_flow_file(
        "smart_qa_agent_workflow.yaml",
        {"question": question}
    )
    
    print(f"✅ Status: {execution.status}")
    print(f"⏱️  Duration: {execution.get_duration():.2f}s\n")
    
    if execution.status == "completed":
        # Show individual results
        research_data = execution.state.get("research_data")
        answer = execution.state.get("answer")
        enhanced_answer = execution.state.get("enhanced_answer")
        followups = execution.state.get("followup_questions")
        final_response = execution.state.get("final_response")
        
        if research_data:
            print_full_result("🔍 Research Data", research_data)
        
        if answer:
            print_full_result("💬 Answer", answer)
        
        if enhanced_answer:
            print_full_result("✨ Enhanced Answer", enhanced_answer)
        
        if followups:
            print_full_result("🔗 Follow-up Questions", followups)
        
        if final_response:
            print_full_result("📋 Final Response", final_response)
        
        # Show everything
        show_all_state(execution)
    else:
        print(f"❌ Error: {execution.error}")

def test_content_creator():
    """Test Content Creator Agent and show full results"""
    print("\n" + "🤖" * 40)
    print("  CONTENT CREATOR AGENT")
    print("🤖" * 40)
    
    executor = WorkflowExecutor()
    
    topic = "the future of renewable energy"
    print(f"\n📌 Topic: {topic}\n")
    print("⏳ Executing workflow...\n")
    
    execution = executor.execute_flow_file(
        "content_creator_agent_workflow.yaml",
        {"topic": topic}
    )
    
    print(f"✅ Status: {execution.status}")
    print(f"⏱️  Duration: {execution.get_duration():.2f}s\n")
    
    if execution.status == "completed":
        # Show individual results
        research_findings = execution.state.get("research_findings")
        outline = execution.state.get("outline")
        introduction = execution.state.get("introduction")
        main_content = execution.state.get("main_content")
        conclusion = execution.state.get("conclusion")
        final_article = execution.state.get("final_article")
        
        if research_findings:
            print_full_result("🔍 Research Findings", research_findings)
        
        if outline:
            print_full_result("📋 Outline", outline)
        
        if introduction:
            print_full_result("📝 Introduction", introduction)
        
        if main_content:
            print_full_result("📄 Main Content", main_content)
        
        if conclusion:
            print_full_result("🏁 Conclusion", conclusion)
        
        if final_article:
            print_full_result("📚 Final Article", final_article)
        
        # Show everything
        show_all_state(execution)
    else:
        print(f"❌ Error: {execution.error}")

def main():
    import sys
    
    print("\n" + "=" * 80)
    print("  📊 AGENT RESULTS VIEWER")
    print("  View complete outputs from all agent workflows")
    print("=" * 80)
    
    if len(sys.argv) > 1:
        agent = sys.argv[1].lower()
        if agent == "research":
            test_research_agent()
        elif agent == "qa" or agent == "qa_agent":
            test_qa_agent()
        elif agent == "content" or agent == "creator":
            test_content_creator()
        else:
            print(f"Unknown agent: {agent}")
            print("Usage: python view_results.py [research|qa|content]")
    else:
        # Run all
        print("\n💡 Tip: Run specific agent with: python view_results.py [research|qa|content]")
        print("   Example: python view_results.py research\n")
        
        test_research_agent()
        print("\n\n")
        test_qa_agent()
        print("\n\n")
        test_content_creator()
    
    print("\n" + "=" * 80)
    print("  ✅ Complete!")
    print("=" * 80 + "\n")

if __name__ == "__main__":
    main()

