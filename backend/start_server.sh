#!/bin/bash

# Script to start the Assist Stack backend server

echo "Starting Assist Stack Backend Server..."
echo "============================================"

# Check if we're in the right directory
if [ ! -f "main.py" ]; then
    echo "Error: main.py not found. Please run this script from the backend directory."
    exit 1
fi

# Check if requirements are installed
python -c "import fastapi, uvicorn, pydantic, openai" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "Installing dependencies..."
    pip install -r requirements.txt
fi

# Check for OpenAI API key
if [ -z "$OPENAI_API_KEY" ]; then
    echo "⚠️  Warning: OPENAI_API_KEY environment variable is not set."
    echo "   The server will run but AI conversion will not work."
    echo "   To enable AI features:"
    echo "   export OPENAI_API_KEY='your-openai-api-key'"
    echo ""
fi

echo "Starting server on http://localhost:5001"
echo "API documentation: http://localhost:5001/docs"
echo "Health check: http://localhost:5001/health"
echo ""
echo "Press Ctrl+C to stop the server"
echo "============================================"

python main.py