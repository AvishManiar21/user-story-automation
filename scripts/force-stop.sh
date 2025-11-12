#!/bin/bash

# Force stop all nginx processes and free port 80

echo "🛑 Stopping all nginx processes..."

# Stop nginx gracefully first
sudo nginx -s stop 2>/dev/null
sleep 1

# Stop systemd service if running
sudo systemctl stop nginx 2>/dev/null
sleep 1

# Kill all nginx processes
sudo pkill -9 nginx 2>/dev/null
sleep 1

# Check what's using port 80
echo ""
echo "🔍 Checking what's using port 80..."
if command -v lsof >/dev/null 2>&1; then
    sudo lsof -i :80 2>/dev/null || echo "Port 80 is free"
elif command -v netstat >/dev/null 2>&1; then
    sudo netstat -tlnp 2>/dev/null | grep :80 || echo "Port 80 is free"
else
    echo "Cannot check port 80 (lsof/netstat not available)"
fi

# Verify nginx is stopped
if pgrep -x nginx > /dev/null 2>&1; then
    echo "⚠️  Nginx processes still running, trying harder..."
    sudo killall -9 nginx 2>/dev/null
    sleep 2
fi

if pgrep -x nginx > /dev/null 2>&1; then
    echo "❌ Failed to stop nginx"
    echo "Run manually: sudo pkill -9 nginx"
    exit 1
else
    echo "✅ All nginx processes stopped"
    echo "✅ Port 80 should be free now"
    exit 0
fi

