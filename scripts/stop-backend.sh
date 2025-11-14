#!/bin/bash

# Stop Flask backend server

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$( cd "$SCRIPT_DIR/.." && pwd )"

cd "$PROJECT_DIR"

if [ -f "backend.pid" ]; then
    BACKEND_PID=$(cat backend.pid)
    if ps -p $BACKEND_PID > /dev/null 2>&1; then
        kill $BACKEND_PID 2>/dev/null
        sleep 1
        # Force kill if still running
        if ps -p $BACKEND_PID > /dev/null 2>&1; then
            kill -9 $BACKEND_PID 2>/dev/null
        fi
        echo "✅ Backend stopped"
    else
        echo "ℹ️  Backend is not running"
    fi
    rm -f backend.pid
else
    # Try to find and kill any running Flask app
    pkill -f "python.*app.py" 2>/dev/null
    if [ $? -eq 0 ]; then
        echo "✅ Backend stopped"
    else
        echo "ℹ️  Backend is not running"
    fi
fi

