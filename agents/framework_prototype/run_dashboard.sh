#!/bin/bash
# Run the Agent Framework Dashboard

echo "🤖 Starting Agent Framework Dashboard..."
echo ""

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    echo "✅ Activating virtual environment..."
    source venv/bin/activate
else
    echo "⚠️  Virtual environment not found. Creating one..."
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
fi

# Check if streamlit is installed
if ! command -v streamlit &> /dev/null; then
    echo "⚠️  Streamlit not found. Installing..."
    pip install streamlit
fi

# Run dashboard
streamlit run dashboard.py --server.port 8501 --server.address 0.0.0.0

