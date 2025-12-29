import streamlit as st
import json
import time
import pandas as pd
from datetime import datetime
import sys
from pathlib import Path

# Add root path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from kafka import KafkaConsumer
    from kafka.errors import NoBrokersAvailable
    KAFKA_AVAILABLE = True
except ImportError:
    KAFKA_AVAILABLE = False

st.set_page_config(
    page_title="Cortex Live Dashboard",
    page_icon="🧠",
    layout="wide",
)

# Custom CSS for "Vibrant & Premium" look
st.markdown("""
<style>
    .metric-card {
        background-color: #1E1E1E;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #4CAF50;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    .metric-value {
        font-size: 2em;
        font-weight: bold;
        color: #FFFFFF;
    }
    .metric-label {
        font-size: 1em;
        color: #AAAAAA;
    }
    .stDataFrame {
        border-radius: 10px;
        overflow: hidden;
    }
</style>
""", unsafe_allow_html=True)

st.title("🧠 Cortex Agent Ecosystem")
st.caption("Real-time distributed execution monitoring")

# Session State for Event Log and Jobs
if "events" not in st.session_state:
    st.session_state.events = []
if "jobs" not in st.session_state:
    st.session_state.jobs = {}

# Kafka Connection
@st.cache_resource
def get_kafka_consumer():
    if not KAFKA_AVAILABLE:
        return None
    try:
        consumer = KafkaConsumer(
            'agent_workflow_events', 'agent_jobs', 'agent_job_results',
            bootstrap_servers=['localhost:29092'],
            auto_offset_reset='earliest',
            enable_auto_commit=True,
            group_id='cortex_dashboard_group',
            value_deserializer=lambda x: json.loads(x.decode('utf-8'))
        )
        return consumer
    except NoBrokersAvailable:
        return None

consumer = get_kafka_consumer()

if not KAFKA_AVAILABLE:
    st.error("⚠️ kafka-python not installed.")
elif not consumer:
    st.warning("⚠️ Kafka broker not found. Is Docker running?")
else:
    # Sidebar: connection status
    st.sidebar.success("🟢 Connected to Kafka")
    
    # Poll for messages (limit to 50 per refresh to avoid freezing)
    msg_count = 0
    raw_messages = consumer.poll(timeout_ms=500, max_records=50)
    
    for topic_partition, messages in raw_messages.items():
        for msg in messages:
            msg_count += 1
            data = msg.value
            event_type = data.get('type')
            
            # Add to raw event log
            st.session_state.events.insert(0, {
                "Time": datetime.fromtimestamp(data.get('timestamp', time.time()) if isinstance(data.get('timestamp'), (int, float)) else time.time()).strftime('%H:%M:%S'),
                "Topic": msg.topic,
                "Type": event_type,
                "Data": str(data.get('payload', data))
            })
            
            # Process Job Updates
            if msg.topic == 'agent_jobs' and event_type == 'JOB_REQUEST':
                payload = data.get('payload', {})
                job_id = payload.get('job_id')
                if job_id:
                    st.session_state.jobs[job_id] = {
                        "id": job_id,
                        "flow": payload.get('flow_file'),
                        "status": "QUEUED",
                        "updated": datetime.now().strftime('%H:%M:%S')
                    }
                    
            elif msg.topic == 'agent_job_results' and event_type == 'JOB_COMPLETED':
                payload = data.get('payload', {})
                job_id = payload.get('job_id')
                if job_id in st.session_state.jobs:
                    st.session_state.jobs[job_id]['status'] = "COMPLETED"
                    st.session_state.jobs[job_id]['updated'] = datetime.now().strftime('%H:%M:%S')
                    st.session_state.jobs[job_id]['result'] = payload.get('output')

            elif msg.topic == 'agent_job_results' and event_type == 'JOB_FAILED':
                payload = data.get('payload', {})
                job_id = payload.get('job_id')
                if job_id in st.session_state.jobs:
                    st.session_state.jobs[job_id]['status'] = "FAILED"
                    st.session_state.jobs[job_id]['updated'] = datetime.now().strftime('%H:%M:%S')

    # Keep log manageable
    if len(st.session_state.events) > 1000:
        st.session_state.events = st.session_state.events[:1000]

    # Metrics
    col1, col2, col3 = st.columns(3)
    active_jobs = sum(1 for j in st.session_state.jobs.values() if j['status'] == 'QUEUED')
    completed_jobs = sum(1 for j in st.session_state.jobs.values() if j['status'] == 'COMPLETED')
    failed_jobs = sum(1 for j in st.session_state.jobs.values() if j['status'] == 'FAILED')

    with col1:
        st.metric("Running Jobs", str(active_jobs), delta=None)
    with col2:
        st.metric("Completed", str(completed_jobs), delta=None)
    with col3:
        metric_val = f"{failed_jobs}"
        st.metric("Failed", metric_val, delta_color="inverse")

    # Layout
    tab1, tab2 = st.tabs(["📊 Active Jobs", "📜 Event Stream"])

    with tab1:
        if st.session_state.jobs:
            df_jobs = pd.DataFrame(st.session_state.jobs.values())
            # Reorder cols
            cols = ["id", "flow", "status", "updated"]
            df_jobs = df_jobs[cols]
            st.dataframe(df_jobs, use_container_width=True)
            
            # Show details of selected job (Mock implementation for now)
            # st.json(st.session_state.jobs.values()) # Debug raw
        else:
            st.info("No jobs tracked yet. Send a job via worker to see it here!")

    with tab2:
        if st.session_state.events:
            st.dataframe(pd.DataFrame(st.session_state.events), use_container_width=True)
        else:
            st.text("Waiting for events...")

    # Auto-refresh logic (Simple rerunning)
    time.sleep(1)
    st.rerun()
