"""
🤖 Agent Framework Dashboard
Generic UI that automatically discovers and runs all agents
"""

import streamlit as st
import yaml
import json
from pathlib import Path
from datetime import datetime
from orchestrator.executor import WorkflowExecutor
import sys
import os
import uuid
import json
import time

try:
    from kafka import KafkaConsumer
except ImportError:
    pass # Handled later via flag or try/except blocks

# Add infrastructure imports
try:
    from infrastructure.messaging.kafka_service import KafkaService
except ImportError:
    # If custom pathing needed
    sys.path.insert(0, str(Path(__file__).parent))
    from infrastructure.messaging.kafka_service import KafkaService

# Page config
st.set_page_config(
    page_title="Agent Framework Dashboard",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        padding: 1rem 0;
    }
    .agent-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        border-left: 4px solid #1f77b4;
    }
    .result-box {
        background-color: #ffffff;
        padding: 1.5rem;
        border-radius: 8px;
        border: 1px solid #e0e0e0;
        margin: 1rem 0;
    }
    .status-success {
        color: #28a745;
        font-weight: bold;
    }
    .status-error {
        color: #dc3545;
        font-weight: bold;
    }
    .status-running {
        color: #ffc107;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'execution_history' not in st.session_state:
    st.session_state.execution_history = []
if 'current_execution' not in st.session_state:
    st.session_state.current_execution = None
if 'groq_api_key' not in st.session_state:
    st.session_state.groq_api_key = os.getenv("GROQ_API_KEY", "")
if 'gemini_api_key' not in st.session_state:
    st.session_state.gemini_api_key = os.getenv("GEMINI_API_KEY", "")
if 'selected_provider' not in st.session_state:
    st.session_state.selected_provider = "groq"
if 'selected_gemini_model' not in st.session_state:
    st.session_state.selected_gemini_model = "gemini-2.0-flash"

def discover_workflows():
    """Automatically discover all YAML workflow files"""
    workflows = []
    current_dir = Path(__file__).parent
    
    # Search in current directory and examples
    search_paths = [
        current_dir,
        current_dir / "examples" / "workflows",
        current_dir / "examples" / "flows"
    ]
    
    for search_path in search_paths:
        if search_path.exists():
            for yaml_file in search_path.glob("*.yaml"):
                try:
                    with open(yaml_file, 'r') as f:
                        workflow_data = yaml.safe_load(f)
                        workflows.append({
                            'file': str(yaml_file),
                            'name': workflow_data.get('name', yaml_file.stem),
                            'description': workflow_data.get('description', ''),
                            'path': yaml_file
                        })
                except Exception as e:
                    st.warning(f"Could not load {yaml_file}: {e}")
    
    return sorted(workflows, key=lambda x: x['name'])

def get_workflow_inputs(workflow_path):
    """Extract input schema from workflow YAML"""
    try:
        with open(workflow_path, 'r') as f:
            workflow_data = yaml.safe_load(f)
            inputs = workflow_data.get('input', {})
            return inputs
    except Exception as e:
        return {}

def format_result(value, max_length=20000):
    """Format result for display"""
    if value is None:
        return "*(No value)*"
    
    if isinstance(value, dict):
        return json.dumps(value, indent=2, ensure_ascii=False)
    elif isinstance(value, list):
        if len(value) > 0 and isinstance(value[0], dict):
            return json.dumps(value, indent=2, ensure_ascii=False)
        else:
            return "\n".join(str(v) for v in value)
    else:
        str_value = str(value)
        # Allow much longer responses before truncation so itineraries and summaries are readable
        if len(str_value) > max_length:
            return str_value[:max_length] + f"\n\n... (truncated, {len(str_value)} chars total)"
        return str_value

def main():
    # Header
    st.markdown('<h1 class="main-header">🤖 Agent Framework Dashboard</h1>', unsafe_allow_html=True)
    st.markdown("---")
    
    # Sidebar
    with st.sidebar:
        st.header("📋 Navigation")
        page = st.radio(
            "Choose a page:",
            ["🏠 Run Agent", "📊 Execution History", "ℹ️ About"]
        )
        
        st.markdown("---")
        st.header("⚙️ Settings")
        
        # Execution Mode
        st.subheader("🚀 Execution Mode")
        execution_mode = st.radio(
            "Mode:",
            ["Local (In-Process)", "Distributed (Kafka)"],
            index=0,
            help="Local runs in this dashboard. Distributed sends to Worker nodes via Kafka."
        )
        st.session_state.execution_mode = "distributed" if "Distributed" in execution_mode else "local"
        
        show_debug = st.checkbox("Show Debug Info", value=False)
        
        # API Keys Management
        st.markdown("---")
        st.header("🔑 API Keys")
        
        # Provider Selection
        provider = st.radio(
            "Select LLM Provider:",
            ["Groq", "Gemini"],
            index=0 if st.session_state.selected_provider == "groq" else 1,
            key="provider_radio"
        )
        st.session_state.selected_provider = provider.lower()
        
        # Groq API Key
        st.subheader("🔵 Groq API Key")
        groq_key = st.text_input(
            "Groq API Key:",
            value=st.session_state.groq_api_key,
            type="password",
            help="Get your key from https://console.groq.com/",
            key="groq_key_input"
        )
        st.session_state.groq_api_key = groq_key
        
        if groq_key:
            st.success("✅ Groq API key set")
            os.environ["GROQ_API_KEY"] = groq_key
        else:
            if "GROQ_API_KEY" in os.environ:
                del os.environ["GROQ_API_KEY"]
            st.info("💡 Leave empty to use mock mode")
        
        # Gemini API Key
        st.subheader("🟢 Gemini API Key")
        gemini_key = st.text_input(
            "Gemini API Key:",
            value=st.session_state.gemini_api_key,
            type="password",
            help="Get your key from https://aistudio.google.com/",
            key="gemini_key_input"
        )
        st.session_state.gemini_api_key = gemini_key
        
        if gemini_key:
            st.success("✅ Gemini API key set")
            os.environ["GEMINI_API_KEY"] = gemini_key
            
            # Gemini Model Selection
            st.markdown("---")
            st.subheader("🤖 Gemini Model Selection")
            gemini_models = [
                "gemini-2.0-flash",
                "gemini-1.5-pro",
                "gemini-1.5-flash",
                "gemini-1.5-pro-latest",
                "gemini-1.5-flash-latest"
            ]
            selected_model = st.selectbox(
                "Choose Gemini Model:",
                gemini_models,
                index=gemini_models.index(st.session_state.selected_gemini_model) if st.session_state.selected_gemini_model in gemini_models else 0,
                key="gemini_model_select"
            )
            st.session_state.selected_gemini_model = selected_model
            st.caption(f"Selected: {selected_model}")
        else:
            if "GEMINI_API_KEY" in os.environ:
                del os.environ["GEMINI_API_KEY"]
            st.info("💡 Leave empty to disable Gemini")
        
        # API Status Summary
        st.markdown("---")
        st.header("📊 API Status")
        status_col1, status_col2 = st.columns(2)
        with status_col1:
            if st.session_state.groq_api_key:
                st.success("✅ Groq Ready")
            else:
                st.warning("⚠️ Groq Not Set")
        with status_col2:
            if st.session_state.gemini_api_key:
                st.success("✅ Gemini Ready")
            else:
                st.info("ℹ️ Gemini Not Set")
    
    # Main content based on page
    if page == "🏠 Run Agent":
        run_agent_page(show_debug)
    elif page == "📊 Execution History":
        history_page()
    elif page == "ℹ️ About":
        about_page()

def run_agent_page(show_debug):
    """Main page to run agents"""
    st.header("🚀 Run Agent Workflow")
    
    # Discover workflows
    workflows = discover_workflows()
    
    if not workflows:
        st.error("No workflow files found! Please add YAML workflow files to the project.")
        return
    
    # Workflow selection
    workflow_names = [f"{w['name']} ({Path(w['file']).name})" for w in workflows]
    selected_index = st.selectbox(
        "Select an Agent Workflow:",
        range(len(workflows)),
        format_func=lambda x: workflow_names[x]
    )
    
    selected_workflow = workflows[selected_index]
    
    # Display workflow info
    with st.expander("📄 Workflow Details", expanded=False):
        st.write(f"**Name:** {selected_workflow['name']}")
        st.write(f"**Description:** {selected_workflow['description']}")
        st.write(f"**File:** `{selected_workflow['file']}`")
        
        if show_debug:
            with open(selected_workflow['path'], 'r') as f:
                st.code(f.read(), language='yaml')
    
    st.markdown("---")
    
    # Get input schema
    input_schema = get_workflow_inputs(selected_workflow['path'])
    
    # Input form
    st.subheader("📥 Input Parameters")
    input_data = {}
    
    if input_schema:
        for key, value_type in input_schema.items():
            if isinstance(value_type, str):
                if value_type.lower() == "string":
                    input_data[key] = st.text_input(
                        f"{key.replace('_', ' ').title()}:",
                        key=key,
                        help=f"Type: {value_type}"
                    )
                elif value_type.lower() == "number" or value_type.lower() == "int":
                    input_data[key] = st.number_input(
                        f"{key.replace('_', ' ').title()}:",
                        key=key,
                        value=0
                    )
                else:
                    input_data[key] = st.text_input(
                        f"{key.replace('_', ' ').title()}:",
                        key=key
                    )
            else:
                input_data[key] = st.text_input(
                    f"{key.replace('_', ' ').title()}:",
                    key=key
                )
    else:
        st.info("No input schema defined. Using default inputs.")
        # Try to infer from common patterns
        if 'topic' in selected_workflow['name'].lower() or 'research' in selected_workflow['name'].lower():
            input_data['topic'] = st.text_input("Topic:", value="artificial intelligence")
        elif 'question' in selected_workflow['name'].lower() or 'qa' in selected_workflow['name'].lower():
            input_data['question'] = st.text_input("Question:", value="What is machine learning?")
        else:
            input_data['input'] = st.text_input("Input:", value="test input")
    
    st.markdown("---")
    
    # Execute button
    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        execute_btn = st.button("▶️ Execute Workflow", type="primary", use_container_width=True)
    with col2:
        clear_btn = st.button("🗑️ Clear Results", use_container_width=True)
    
    if clear_btn:
        st.session_state.current_execution = None
        st.rerun()
    
    # Provider/Model Selection for LLM nodes
    st.markdown("---")
    st.subheader("🤖 LLM Configuration")
    col1, col2 = st.columns(2)
    with col1:
        provider_options = ["auto", "groq", "gemini"]
        current_provider = st.session_state.selected_provider
        if current_provider == "groq":
            default_index = 1
        elif current_provider == "gemini":
            default_index = 2
        else:
            default_index = 0
        
        llm_provider = st.selectbox(
            "LLM Provider:",
            provider_options,
            index=default_index,
            help="Auto will use available API keys (prefers Gemini if both available)"
        )
        st.session_state.selected_provider = llm_provider
    with col2:
        if llm_provider == "gemini":
            if st.session_state.gemini_api_key:
                gemini_models = ["gemini-2.0-flash", "gemini-1.5-pro", "gemini-1.5-flash", "gemini-1.5-pro-latest", "gemini-1.5-flash-latest"]
                current_model = st.session_state.selected_gemini_model
                default_idx = gemini_models.index(current_model) if current_model in gemini_models else 0
                selected_gemini_model = st.selectbox(
                    "Gemini Model:",
                    gemini_models,
                    index=default_idx,
                    help="Select Gemini model to use"
                )
                st.session_state.selected_gemini_model = selected_gemini_model
                os.environ["GEMINI_MODEL"] = selected_gemini_model
            else:
                st.warning("⚠️ Gemini API key not set")
        elif llm_provider == "groq":
            if st.session_state.groq_api_key:
                st.info("✅ Using Groq (models configured in workflow)")
            else:
                st.warning("⚠️ Groq API key not set")
        else:  # auto
            available = []
            if st.session_state.groq_api_key:
                available.append("Groq")
            if st.session_state.gemini_api_key:
                available.append("Gemini")
            if available:
                st.info(f"🔍 Auto mode: Will use {', '.join(available)}")
            else:
                st.warning("⚠️ No API keys available - will use mock mode")
    
    st.markdown("---")
    
    if execute_btn:
        # Validate inputs
        if not input_data or all(not v for v in input_data.values()):
            st.warning("⚠️ Please provide input values before executing.")
        else:
            # Set provider/model environment variables
            if llm_provider != "auto":
                os.environ["LLM_PROVIDER"] = llm_provider
            
            # Execute workflow
            with st.spinner(f"🔄 Executing {selected_workflow['name']}..."):
                try:
                    if st.session_state.execution_mode == "local":
                        executor = WorkflowExecutor()
                        execution = executor.execute_flow_file(
                            selected_workflow['path'],
                            input_data
                        )
                        
                        # Store in session state
                        st.session_state.current_execution = {
                            'workflow': selected_workflow['name'],
                            'execution': execution,
                            'timestamp': datetime.now(),
                            'inputs': input_data,
                            'mode': 'local'
                        }
                    else:
                        # Distributed Mode
                        job_id = str(uuid.uuid4())
                        kafka = KafkaService()
                        
                        if not kafka.enabled:
                            st.error("❌ Kafka not available. Is Docker running?")
                            return

                        payload = {
                            "job_id": job_id,
                            "flow_file": str(Path(selected_workflow['path']).name), # Worker expects filename in examples/workflows
                            "input": input_data
                        }
                        
                        kafka.send_event('agent_jobs', 'JOB_REQUEST', payload)
                        kafka.close()
                        
                        st.success(f"✅ Job {job_id} sent to Distributed Worker!")
                        
                        # Polling for result
                        with st.spinner("⏳ Waiting for remote worker to finish... (This may take a few seconds)"):
                            # Create consumer
                            consumer = KafkaConsumer(
                                'agent_job_results',
                                bootstrap_servers=['localhost:29092'],
                                auto_offset_reset='earliest', # Changed from latest to catch fast responses
                                group_id=f'dashboard_poller_{job_id}',
                                value_deserializer=lambda x: json.loads(x.decode('utf-8')),
                                consumer_timeout_ms=30000  # Wait up to 30s
                            )
                            
                            start_time = time.time()
                            job_result = None
                            
                            # Simple polling loop
                            # We poll until we find OUR job_id or timeout
                            while (time.time() - start_time) < 60:
                                msg_batch = consumer.poll(timeout_ms=1000)
                                for tp, messages in msg_batch.items():
                                    for msg in messages:
                                        data = msg.value
                                        # checkpoint: is this our job?
                                        if data.get('payload', {}).get('job_id') == job_id:
                                            job_result = data
                                            break
                                    if job_result: break
                                if job_result: break
                                
                            consumer.close()
                        
                        if job_result:
                            payload = job_result.get('payload', {})
                            status = payload.get('status')
                            output_state = payload.get('output', {})
                            error_msg = payload.get('error')
                            
                            # Construct a mock execution object for display_results
                            class MockExecution:
                                def __init__(self, s, state_dict, err):
                                    self.status = s
                                    self.error = err
                                    self.execution_id = job_id
                                    self.node_results = {} # Detailed node results might be missing in simple payload
                                    
                                    # Create a mock State object
                                    class MockState:
                                        def __init__(self, d): self._d = d
                                        def get_all(self): return self._d
                                        def set(self, k, v): self._d[k] = v
                                    self.state = MockState(state_dict)
                                
                                def get_duration(self): return 0.0 # Unknown duration
                                
                            mock_exec = MockExecution(status, output_state, error_msg)

                            st.session_state.current_execution = {
                                'workflow': selected_workflow['name'],
                                'execution': mock_exec,
                                'status': status,
                                'job_id': job_id,
                                'timestamp': datetime.now(),
                                'inputs': input_data,
                                'mode': 'distributed_completed' # Mark as completed distributed
                            }
                            st.success("✅ Remote execution completed!")
                            
                        else:
                            st.warning("⏳ Timeout waiting for result. The worker is still running.")
                            st.info(f"Job ID: {job_id}")
                            st.session_state.current_execution = {
                                'workflow': selected_workflow['name'],
                                'status': 'queued',
                                'job_id': job_id,
                                'timestamp': datetime.now(),
                                'inputs': input_data,
                                'mode': 'distributed'
                            }

                    # Add to history
                    st.session_state.execution_history.insert(0, st.session_state.current_execution.copy())
                    
                    # Limit history size
                    if len(st.session_state.execution_history) > 50:
                        st.session_state.execution_history = st.session_state.execution_history[:50]
                    
                except Exception as e:
                    st.error(f"❌ Execution failed: {str(e)}")
                    if show_debug:
                        st.exception(e)
    
    # Display results
    if st.session_state.current_execution:
        display_results(st.session_state.current_execution, show_debug)

def display_results(execution_data, show_debug):
    """Display execution results"""
    # Handle Distributed Mode
    if execution_data.get('mode') == 'distributed':
        st.markdown("---")
        st.header("📊 Distributed Execution Queued")
        st.success(f"✅ Job sent to worker queue")
        st.markdown(f"**Job ID:** `{execution_data.get('job_id')}`")
        st.info("ℹ️ Switch to the 'Cortex Live Dashboard' to monitor the execution status in real-time.")
        return

    execution = execution_data['execution']
    workflow_name = execution_data['workflow']
    
    st.markdown("---")
    st.header("📊 Execution Results")
    
    # Status and metadata
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        if execution.status == "completed":
            st.markdown('<p class="status-success">✅ Status: Completed</p>', unsafe_allow_html=True)
        elif execution.status == "failed":
            st.markdown('<p class="status-error">❌ Status: Failed</p>', unsafe_allow_html=True)
        else:
            st.markdown(f'<p class="status-running">⏳ Status: {execution.status}</p>', unsafe_allow_html=True)
    
    with col2:
        st.metric("Duration", f"{execution.get_duration():.2f}s")
    
    with col3:
        st.metric("Execution ID", execution.execution_id[:8])
    
    with col4:
        st.metric("Timestamp", execution_data['timestamp'].strftime("%H:%M:%S"))
    
    if execution.status == "failed":
        st.error(f"**Error:** {execution.error}")
    
    st.markdown("---")
    
    # Check for notifications and external actions
    all_state = execution.state.get_all()
    notifications = all_state.get("notifications", [])
    external_actions = []
    
    # Find all external actions that need confirmation
    for key, value in all_state.items():
        if isinstance(value, dict):
            if value.get("requires_confirmation") and value.get("status") == "pending_confirmation":
                external_actions.append({
                    "key": key,
                    "data": value,
                    "type": value.get("action_type", "external_action")
                })
    
    # Display notifications and external actions
    if notifications or external_actions:
        st.subheader("🔔 Notifications & External Actions")
        
        # Show notifications
        if notifications:
            for idx, notif in enumerate(notifications):
                with st.expander(f"📢 {notif.get('message', 'Notification')}", expanded=True):
                    st.write(f"**Type:** {notif.get('type', 'unknown')}")
                    st.write(f"**Time:** {notif.get('timestamp', 'N/A')}")
                    if notif.get('requires_action'):
                        st.warning("⚠️ Action requires confirmation")
        
        # Show external actions requiring confirmation
        if external_actions:
            st.markdown("### ⚠️ Actions Requiring Confirmation")
            
            for idx, action in enumerate(external_actions):
                action_data = action["data"]
                action_type = action["type"]
                
                st.markdown(f"#### {idx + 1}. {action_type.replace('_', ' ').title()}")
                
                # Display action details
                if action_type == "google_calendar" or action_type == "calendar_booking":
                    st.write(f"**Event:** {action_data.get('title', 'N/A')}")
                    st.write(f"**Date:** {action_data.get('start_date', 'N/A')} - {action_data.get('end_date', 'N/A')}")
                    st.write(f"**Location:** {action_data.get('location', 'N/A')}")
                    if action_data.get('description'):
                        st.write(f"**Description:** {action_data.get('description')[:200]}...")
                else:
                    # Generic action display
                    st.json(action_data)
                
                # Confirmation buttons
                col1, col2 = st.columns(2)
                with col1:
                    if st.button(f"✅ Confirm & Execute", key=f"confirm_{action['key']}_{idx}", type="primary"):
                        # Mark as confirmed (in real implementation, this would trigger actual execution)
                        st.success(f"✅ {action_type} action confirmed!")
                        # Update state
                        action_data["status"] = "confirmed"
                        action_data["confirmed_at"] = datetime.now().isoformat()
                        execution.state.set(action["key"], action_data)
                        st.rerun()
                
                with col2:
                    if st.button(f"❌ Cancel", key=f"cancel_{action['key']}_{idx}"):
                        action_data["status"] = "cancelled"
                        action_data["cancelled_at"] = datetime.now().isoformat()
                        execution.state.set(action["key"], action_data)
                        st.info(f"❌ {action_type} action cancelled")
                        st.rerun()
                
                st.markdown("---")
    
    st.markdown("---")
    
    # State contents
    st.subheader("📦 Output Data")
    
    if not all_state:
        st.info("No output data available.")
    else:
        # Create tabs for different views
        tab1, tab2, tab3 = st.tabs(["📋 Key Results", "🔍 All State", "📄 JSON View"])
        
        with tab1:
            # Show important keys first
            important_keys = ['summary', 'answer', 'enhanced_answer', 'insights', 
                            'final_report', 'final_response', 'final_article',
                            'outline', 'introduction', 'main_content', 'conclusion',
                            'itinerary', 'tour_summary', 'final_plan']
            
            found_important = False
            
            # Show plan/itinerary first if available
            if 'final_plan' in all_state:
                found_important = True
                plan = all_state['final_plan']
                st.markdown("### 📋 Complete Plan")
                if isinstance(plan, dict):
                    # Display structured plan
                    for key, value in plan.items():
                        if key not in ['morning_event', 'afternoon_event', 'evening_event']:
                            st.markdown(f"**{key.replace('_', ' ').title()}:**")
                            st.markdown(f'<div class="result-box">{format_result(value)}</div>', unsafe_allow_html=True)
                            st.markdown("---")
                else:
                    st.markdown(f'<div class="result-box">{format_result(plan)}</div>', unsafe_allow_html=True)
                    st.markdown("---")
            
            # Show itinerary if available
            if 'itinerary' in all_state:
                found_important = True
                st.markdown("### 🗺️ Tour Itinerary")
                st.markdown(f'<div class="result-box">{format_result(all_state["itinerary"])}</div>', unsafe_allow_html=True)
                st.markdown("---")
            
            # Show other important keys
            for key in important_keys:
                if key in all_state and key not in ['final_plan', 'itinerary']:
                    found_important = True
                    
                    # Special handling for final_article to display structured content
                    if key == 'final_article' and isinstance(all_state[key], dict):
                        st.markdown(f"### {key.replace('_', ' ').title()}")
                        article = all_state[key]
                        
                        # Display each section of the article nicely
                        for section_key in ['Topic', 'Outline', 'Introduction', 'Main Content', 'Conclusion']:
                            if section_key in article:
                                st.markdown(f"#### {section_key}")
                                st.markdown(f'<div class="result-box">{format_result(article[section_key])}</div>', unsafe_allow_html=True)
                        st.markdown("---")
                    else:
                        st.markdown(f"### {key.replace('_', ' ').title()}")
                        st.markdown(f'<div class="result-box">{format_result(all_state[key])}</div>', unsafe_allow_html=True)
                        st.markdown("---")
            
            if not found_important:
                st.info("No standard output keys found. Check 'All State' tab.")
        
        with tab2:
            for key, value in all_state.items():
                with st.expander(f"🔑 {key}", expanded=(key in important_keys if 'important_keys' in locals() else False)):
                    st.markdown(f'<div class="result-box">{format_result(value)}</div>', unsafe_allow_html=True)
        
        with tab3:
            st.json(all_state)
    
    # Debug info
    if show_debug:
        st.markdown("---")
        with st.expander("🐛 Debug Information"):
            st.write("**Node Results:**")
            st.json(execution.node_results if hasattr(execution, 'node_results') else {})
            st.write("**Input Data:**")
            st.json(execution_data['inputs'])

def history_page():
    """Display execution history"""
    st.header("📊 Execution History")
    
    if not st.session_state.execution_history:
        st.info("No execution history yet. Run some workflows to see history here.")
        return
    
    # Filter and search
    col1, col2 = st.columns([3, 1])
    with col1:
        search_term = st.text_input("🔍 Search history:", placeholder="Search by workflow name...")
    with col2:
        clear_history = st.button("🗑️ Clear History")
    
    if clear_history:
        st.session_state.execution_history = []
        st.rerun()
    
    # Filter history
    filtered_history = st.session_state.execution_history
    if search_term:
        filtered_history = [
            h for h in filtered_history
            if search_term.lower() in h['workflow'].lower()
        ]
    
    # Display history
    for idx, hist in enumerate(filtered_history):
        with st.expander(
            f"🕐 {hist['timestamp'].strftime('%Y-%m-%d %H:%M:%S')} - {hist['workflow']}",
            expanded=False
        ):
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Status:** {hist['execution'].status}")
                st.write(f"**Duration:** {hist['execution'].get_duration():.2f}s")
            with col2:
                st.write(f"**Execution ID:** {hist['execution'].execution_id[:8]}")
                if st.button("View Details", key=f"view_{idx}"):
                    st.session_state.current_execution = hist
                    st.rerun()
            
            if hist['execution'].status == "completed":
                # Show key results
                state = hist['execution'].state.get_all()
                key_results = {k: v for k, v in state.items() 
                             if k in ['summary', 'answer', 'enhanced_answer', 'insights', 
                                     'final_report', 'final_response'] and v}
                if key_results:
                    st.write("**Key Results:**")
                    for key, value in list(key_results.items())[:3]:  # Show first 3
                        st.text_area(f"{key}:", format_result(value, 200), height=100, key=f"{idx}_{key}")

def about_page():
    """About page"""
    st.header("ℹ️ About Agent Framework Dashboard")
    
    st.markdown("""
    ### 🎯 Features
    
    - **🔍 Auto-Discovery**: Automatically finds all YAML workflow files
    - **🚀 Generic Execution**: Runs any agent without special code
    - **📊 Results Display**: Shows all outputs in organized format
    - **📜 Execution History**: Tracks all workflow runs
    - **🎨 Clean UI**: Easy-to-use interface
    
    ### 📝 How It Works
    
    1. **Discovery**: Scans for `.yaml` workflow files
    2. **Selection**: Choose an agent from the dropdown
    3. **Input**: Provide required parameters
    4. **Execution**: Runs the workflow and displays results
    5. **History**: All executions are saved for review
    
    ### 🔧 Adding New Agents
    
    Simply create a new YAML workflow file! The dashboard will automatically:
    - Discover it
    - Parse the input schema
    - Allow execution
    - Display results
    
    No frontend code needed!
    
    ### 📚 Workflow Format
    
    Your YAML files should have:
    ```yaml
    name: "Agent Name"
    description: "Description"
    nodes: [...]
    edges: [...]
    input:
      key: "type"
    ```
    
    ### 🚀 Getting Started
    
    1. Make sure you have workflow YAML files
    2. Run: `streamlit run dashboard.py`
    3. Select an agent and execute!
    """)
    
    # Show discovered workflows
    st.markdown("---")
    st.subheader("📋 Discovered Workflows")
    workflows = discover_workflows()
    if workflows:
        for wf in workflows:
            st.write(f"- **{wf['name']}**: {wf['description']}")
    else:
        st.warning("No workflows found!")

if __name__ == "__main__":
    main()

