@echo off
REM Run the Agent Framework Dashboard (Windows)

echo 🤖 Starting Agent Framework Dashboard...
echo.

REM Check if streamlit is installed
where streamlit >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ⚠️  Streamlit not found. Installing...
    pip install streamlit
)

REM Run dashboard
streamlit run dashboard.py --server.port 8501

pause

