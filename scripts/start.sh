#!/bin/bash

# User Story Automation Frontend - Start Script
# Run this from WSL: ./scripts/start.sh or npm start

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$( cd "$SCRIPT_DIR/.." && pwd )"
NGINX_CONFIG="$PROJECT_DIR/config/nginx.conf"

# Stop nginx if already running (force restart to use new config)
if pgrep -x nginx > /dev/null 2>&1; then
    # Try graceful stop first
    sudo nginx -s stop > /dev/null 2>&1
    sleep 1
    # Stop system service if running
    sudo systemctl stop nginx > /dev/null 2>&1
    sleep 1
    # Force kill if still running
    if pgrep -x nginx > /dev/null 2>&1; then
        sudo pkill -9 nginx 2>/dev/null
        sleep 1
    fi
fi

# Test configuration (silent unless error)
if ! sudo nginx -t -c "$NGINX_CONFIG" > /dev/null 2>&1; then
    echo "❌ Configuration test failed!"
    sudo nginx -t -c "$NGINX_CONFIG"
    exit 1
fi

# Start nginx (suppress output)
NGINX_OUTPUT=$(sudo nginx -c "$NGINX_CONFIG" 2>&1)

# Wait a moment for nginx to start
sleep 2

# Verify nginx actually started
NGINX_RUNNING=$(pgrep -x nginx > /dev/null 2>&1 && echo "yes" || echo "no")
if [ "$NGINX_RUNNING" = "yes" ]; then
    echo "✅ Server running at http://localhost"
    exit 0
else
    echo "❌ Failed to start server"
    if [ -n "$NGINX_OUTPUT" ]; then
        echo "$NGINX_OUTPUT"
    fi
    echo "Check error log: sudo tail /var/log/nginx/error.log"
    exit 1
fi
