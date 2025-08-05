#!/bin/bash
# Test Real Agent Execution System

echo "🚀 Starting Sentinel Real Agent Execution Test"
echo "=============================================="

# Navigate to the desktop-app directory
cd "$(dirname "$0")"

echo "📍 Current directory: $(pwd)"

# Check if Python environment is activated
if [[ -z "$VIRTUAL_ENV" ]]; then
    echo "⚠️  No virtual environment detected. Consider activating one."
fi

echo "🔧 Installing required dependencies..."
pip install -q fastapi uvicorn loguru python-dotenv asyncio pathlib

echo "🌟 Starting FastAPI server with real agent execution..."
echo "🌐 Server will be available at: http://localhost:8001"
echo "📁 Mission workspaces will be created in: ./sentinel_workspace/"
echo ""
echo "🎯 Try these test missions:"
echo "   - 'Create a simple website for my portfolio'"
echo "   - 'Write a Python script to organize my files'"
echo "   - 'Set up a new Python project called MyApp'"
echo ""
echo "Press Ctrl+C to stop the server"
echo "=============================================="

# Start the server
python -m uvicorn src.main:app --host 0.0.0.0 --port 8001 --reload
