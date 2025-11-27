#!/bin/bash
# Start FinBot Backend Server
# This script activates your virtual environment and starts the backend

echo "========================================"
echo "   Starting FinBot Backend Server"
echo "========================================"
echo ""

# Check if virtual environment exists
if [ ! -f "/home/rajiv07/Chatbots/myenv/bin/activate" ]; then
    echo "ERROR: Virtual environment not found at /home/rajiv07/Chatbots/myenv"
    echo "Please create it first with: python3 -m venv myenv"
    exit 1
fi

# Activate virtual environment
echo "Activating virtual environment..."
source /home/rajiv07/Chatbots/myenv/bin/activate

# Check if we're in the right directory
if [ ! -f "backend/api.py" ]; then
    echo "ERROR: backend/api.py not found"
    echo "Please run this script from the FinBot directory"
    exit 1
fi

# Install FastAPI if needed
echo ""
echo "Checking dependencies..."
python -c "import fastapi" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "FastAPI not installed. Installing required packages..."
    pip install fastapi uvicorn[standard] pydantic
fi

# Check Qdrant status
echo ""
echo "Checking Qdrant connection..."
if python -c "
from qdrant_client import QdrantClient
import sys
try:
    client = QdrantClient(host='localhost', port=6333, timeout=2)
    collections = client.get_collections()
    print('✓ Qdrant: Connected (Port 6333)')
    sys.exit(0)
except Exception as e:
    print('✗ Qdrant: NOT RUNNING')
    print('  Error:', str(e))
    print('')
    print('  Start Qdrant with:')
    print('    docker run -d -p 6333:6333 -p 6334:6334 qdrant/qdrant')
    print('')
    print('  Or check if container exists:')
    print('    docker ps -a | grep qdrant')
    sys.exit(1)
" 2>&1; then
    echo ""
else
    echo ""
    echo "❌ QDRANT IS NOT RUNNING - Backend will fail!"
    echo ""
    read -p "Do you want to continue anyway? (y/N) " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Exiting..."
        exit 1
    fi
fi

# Start the backend
echo ""
echo "========================================"
echo "Starting backend on http://localhost:8000"
echo "API Documentation: http://localhost:8000/docs"
echo "Press CTRL+C to stop"
echo "========================================"
echo ""

# Start with uvicorn
cd /home/rajiv07/Chatbots/FinBot
python -m uvicorn backend.api:app --reload --host 0.0.0.0 --port 8000
