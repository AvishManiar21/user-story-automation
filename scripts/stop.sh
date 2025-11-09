#!/bin/bash

# User Story Automation Frontend - Stop Script

if pgrep -x nginx > /dev/null 2>&1; then
    if sudo nginx -s stop 2>/dev/null; then
        echo "✅ Server stopped"
    else
        sudo pkill -9 nginx 2>/dev/null
        echo "✅ Server stopped"
    fi
else
    echo "ℹ️  Server is not running"
fi

