#!/bin/bash
# Start FinBot Frontend (Modern HTML/CSS/JS)
# This script runs the modern web interface using Python HTTP server

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

# Navigate to frontend directory
cd /home/rajiv07/Chatbots/FinBot/frontend

# Kill any existing process on port 5000
if lsof -Pi :5000 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "Stopping existing server on port 5000..."
    kill -9 $(lsof -Pi :5000 -sTCP:LISTEN -t) 2>/dev/null
    sleep 1
fi

# Start Python HTTP server
echo ""
echo "========================================"
echo "🚀 Frontend starting on:"
echo ""
echo "   Local:    http://localhost:5000"
echo "   Network:  http://$(hostname -I | awk '{print $1}'):5000"
echo ""
echo "📱 Pages:"
echo "   Home:       http://localhost:5000/"
echo "   Chatbot:    http://localhost:5000/pages/chatbot.html"
echo "   Learning:   http://localhost:5000/pages/learning.html"
echo "   Summariser: http://localhost:5000/pages/summariser.html"
echo ""
echo "Press CTRL+C to stop"
echo "========================================"
echo ""

python3 -m http.server 5000
