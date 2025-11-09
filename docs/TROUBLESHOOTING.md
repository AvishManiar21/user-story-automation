# Troubleshooting

## Common Issues

### 403 Forbidden
**Solution:** Restart nginx
```bash
npm stop
npm start
```

### Port 80 Already in Use
```bash
# Find what's using port 80
sudo lsof -i :80

# Stop nginx
npm stop

# Start again
npm start
```

### Files Not Loading (404)
- Check asset paths in HTML files (`/assets/css/styles.css`)
- Verify nginx config has correct root paths
- Restart nginx: `npm run restart`

### Configuration Test Fails
```bash
# Test manually to see errors
npm test

# Check for syntax errors in config/nginx.conf
```

### Server Won't Start
```bash
# Check error logs
sudo tail -f /var/log/nginx/error.log

# Verify nginx is installed
which nginx

# Check permissions
ls -la pages/ assets/
```

### CORS Errors (After Backend Integration)
- Enable CORS in Python backend
- Check backend URL in `assets/js/script.js`
- Verify backend is running

## Getting Help

**Check logs:**
```bash
sudo tail -50 /var/log/nginx/error.log
sudo tail -50 /var/log/nginx/access.log
```

**Test configuration:**
```bash
npm test
```

**Check status:**
```bash
npm run status
```
