#!/bin/bash

# FinBot Startup Script
# This script helps start the FinBot application with proper environment setup

set -e

echo "🤖 FinBot - Financial Literacy Chatbot"
echo "====================================="

# Check if we're in the correct directory
if [[ ! -f "main.py" ]]; then
    echo "❌ Error: main.py not found. Please run this script from the FinBot directory."
    exit 1
fi

# Check if virtual environment exists
if [[ ! -d "venv" ]] && [[ ! -d "../myenv" ]]; then
    echo "⚠️  No virtual environment found. Creating one..."
    python3 -m venv venv
    source venv/bin/activate
    pip install --upgrade pip
else
    # Activate existing virtual environment
    if [[ -d "venv" ]]; then
        source venv/bin/activate
    elif [[ -d "../myenv" ]]; then
        source ../myenv/bin/activate
    fi
fi

echo "✅ Virtual environment activated"

# Check if requirements are installed
if ! python -c "import streamlit, transformers, qdrant_client" 2>/dev/null; then
    echo "📦 Installing requirements..."
    pip install -r requirements.txt
fi

# Check if Qdrant is running
echo "🔍 Checking Qdrant connection..."
if ! curl -f http://localhost:6333/health >/dev/null 2>&1; then
    echo "⚠️  Qdrant is not running on localhost:6333"
    echo "   Please start Qdrant with: docker run -p 6333:6333 qdrant/qdrant"
    echo "   Or use the included docker-compose.yml"
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
else
    echo "✅ Qdrant is running"
fi

# Parse command line arguments
MODE="web"
INGEST_DATA=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --cli)
            MODE="cli"
            shift
            ;;
        --web)
            MODE="web"
            shift
            ;;
        --ingest)
            INGEST_DATA=true
            shift
            ;;
        --help)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --web       Start web interface (default)"
            echo "  --cli       Start command line interface"
            echo "  --ingest    Ingest data before starting"
            echo "  --help      Show this help message"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Ingest data if requested
if [[ "$INGEST_DATA" == true ]]; then
    echo "📚 Ingesting documents..."
    python ingest_data.py --ingest-all
fi

# Start the application
echo "🚀 Starting FinBot in $MODE mode..."

if [[ "$MODE" == "web" ]]; then
    echo "Opening web interface at http://localhost:8501"
    streamlit run main.py -- --mode web
else
    python main.py --mode cli
fi