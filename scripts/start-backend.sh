#!/bin/bash

# Start Flask backend server
# Run this from WSL: ./scripts/start-backend.sh or npm run start:backend

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$( cd "$SCRIPT_DIR/.." && pwd )"

cd "$PROJECT_DIR"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "❌ Failed to create virtual environment"
        exit 1
    fi
fi

# Activate virtual environment
source venv/bin/activate

# Upgrade pip first
echo "⬆️  Upgrading pip..."
pip install --upgrade pip setuptools wheel -q

# Install/update dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "❌ Failed to install dependencies"
    echo "Try: pip install --upgrade pip setuptools wheel"
    exit 1
fi
echo "✅ Dependencies installed"

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  Warning: .env file not found!"
    echo "Creating default .env with Ollama configuration..."
    cat > .env << EOF
# Ollama Configuration (Free, Local - No API Key Needed)
USE_OLLAMA=true
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2
EOF
    echo "✅ Created .env file"
fi

# Check if backend is already running
if [ -f "backend.pid" ]; then
    OLD_PID=$(cat backend.pid)
    if ps -p $OLD_PID > /dev/null 2>&1; then
        echo "⚠️  Backend already running (PID: $OLD_PID)"
        echo "Stop it first with: npm run stop:backend"
        exit 1
    else
        rm -f backend.pid
    fi
fi

# Start Flask server in background using venv python
echo "🚀 Starting Flask backend on http://localhost:5000 (running in background)"
cd "$PROJECT_DIR"
nohup "$PROJECT_DIR/venv/bin/python" app.py > backend.log 2>&1 &
BACKEND_PID=$!
echo $BACKEND_PID > backend.pid
sleep 2

# Verify it started
if ps -p $BACKEND_PID > /dev/null 2>&1; then
    echo "✅ Backend started (PID: $BACKEND_PID)"
    echo "📝 Logs: tail -f backend.log"
    echo "🌐 API: http://localhost:5000/api/health"
    echo ""
    echo "To stop: npm run stop:backend"
else
    echo "❌ Failed to start backend. Check backend.log for errors:"
    tail -5 backend.log
    rm -f backend.pid
    exit 1
fi

