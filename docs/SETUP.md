# Setup Guide

## Quick Start (WSL)

1. **Open WSL terminal**

2. **Navigate to project:**
   ```bash
   cd /mnt/c/Users/avish/OneDrive/Desktop/User\ Story\ automation\ frontend
   ```

3. **Start server:**
   ```bash
   npm start
   ```

4. **Access:** http://localhost

## Installation

### Install Nginx (if needed)

```bash
sudo apt-get update
sudo apt-get install -y nginx
```

## Manual Commands

```bash
# Test configuration
npm test

# Start manually
sudo nginx -c "$(pwd)/config/nginx.conf"

# Stop manually
sudo nginx -s stop

# Check status
npm run status
```

## Troubleshooting

### Port 80 in use
```bash
# Find what's using port 80
sudo lsof -i :80

# Stop nginx first
npm stop

# Start again
npm start
```

### Permission errors
- Use `sudo` for nginx commands
- Or use `npm start` which handles sudo automatically

### Check logs
```bash
sudo tail -f /var/log/nginx/error.log
```

See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for more help.
