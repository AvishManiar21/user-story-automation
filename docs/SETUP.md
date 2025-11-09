# Setup Guide

## Prerequisites

- Windows with WSL (Windows Subsystem for Linux) installed
- Nginx installed in WSL

## Installation

### 1. Install Nginx (if not already installed)

```bash
sudo apt-get update
sudo apt-get install -y nginx
```

### 2. Navigate to Project

```bash
cd /mnt/c/Users/avish/OneDrive/Desktop/User\ Story\ automation\ frontend/user-story-automation
```

## Quick Start

```bash
# Start the server
npm start

# Access the application
# Open browser: http://localhost
```

## Server Management

```bash
# Start server
npm start

# Stop server
npm stop

# Restart server
npm run restart

# Check server status
npm run status

# Test nginx configuration
npm test
```

## Manual Nginx Commands

If you need to run nginx commands manually:

```bash
# Test configuration
sudo nginx -t -c config/nginx.conf

# Start nginx with custom config
sudo nginx -c "$(pwd)/config/nginx.conf"

# Stop nginx
sudo nginx -s stop
```

## Troubleshooting

Common issues:
- Port 80 already in use: Stop nginx with `npm stop` and restart with `npm start`
- Permission errors: Use `sudo` for nginx commands or use `npm start` which handles sudo automatically
- Configuration errors: Test configuration with `npm test` and check error logs with `sudo tail /var/log/nginx/error.log`
