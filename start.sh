#!/bin/bash
# Start the iRacing AI Agent server

echo "🏁 Starting iRacing AI Agent..."

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  No .env file found. Creating from example..."
    cp .env.example .env
    echo "📝 Please edit .env with your OpenAI API key before continuing"
    echo "   Then run this script again"
    exit 1
fi

# Check if dependencies are installed
if ! python -c "import fastapi, uvicorn, httpx" 2>/dev/null; then
    echo "📦 Installing dependencies..."
    pip install -r requirements.txt
fi

echo "🚀 Starting server on http://localhost:8000"
echo "📱 Open browser.html in your web browser to connect"
echo "🎤 Make sure to allow microphone access when prompted"
echo ""
echo "Press Ctrl+C to stop the server"

python server.py