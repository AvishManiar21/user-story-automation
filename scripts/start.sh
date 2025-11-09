#!/bin/bash

# User Story Automation Frontend - Start Script
# Run this from WSL: ./scripts/start.sh or npm start

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$( cd "$SCRIPT_DIR/.." && pwd )"
NGINX_CONFIG="$PROJECT_DIR/config/nginx.conf"

# Stop nginx if already running
if pgrep -x nginx > /dev/null 2>&1; then
    sudo nginx -s stop > /dev/null 2>&1
    sleep 1
fi

# Test configuration (silent unless error)
if ! sudo nginx -t -c "$NGINX_CONFIG" > /dev/null 2>&1; then
    echo "❌ Configuration test failed!"
    sudo nginx -t -c "$NGINX_CONFIG"
    exit 1
fi

# Start nginx
if sudo nginx -c "$NGINX_CONFIG" 2>/dev/null; then
    echo "✅ Server running at http://localhost"
else
    echo "❌ Failed to start server. Check: sudo tail /var/log/nginx/error.log"
    exit 1
fi

