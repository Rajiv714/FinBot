#!/bin/bash
# Start FinBot Frontend (Streamlit)
# This script runs the Streamlit web interface

echo "========================================"
echo "   Starting FinBot Frontend"
echo "========================================"
echo ""

# Check if backend is running
echo "Checking if backend is running..."
if ! curl -s http://localhost:8000/api/health >/dev/null 2>&1; then
    echo "⚠️  WARNING: Backend API not detected on port 8000"
    echo "Please start backend first: ./backend.sh"
    echo ""
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Activate virtual environment
echo "Activating virtual environment..."
source /home/rajiv07/Chatbots/myenv/bin/activate

# Navigate to FinBot directory
cd /home/rajiv07/Chatbots/FinBot

# Check if streamlit is installed
if ! command -v streamlit &> /dev/null; then
    echo "Streamlit not installed. Installing..."
    pip install streamlit
fi

# Start Streamlit frontend
echo ""
echo "========================================"
echo "Starting frontend on http://localhost:8501"
echo "Press CTRL+C to stop"
echo "========================================"
echo ""

streamlit run frontend/streamlit_app.py --server.port 8501
