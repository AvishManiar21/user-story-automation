# Fixes Applied for Nginx and User Story Generation Issues

## Issues Identified

### 1. **Backend Dependencies Not Installing Properly**
**Problem:** The virtual environment was corrupted or dependencies weren't being installed correctly, causing `ModuleNotFoundError: No module named 'flask'`.

**Fix Applied:**
- Updated `scripts/start-backend.sh` to:
  - Upgrade pip, setuptools, and wheel before installing dependencies
  - Add error checking after each step
  - Show clear error messages if installation fails
  - Automatically create `.env` file if missing

### 2. **Nginx Port Conflicts**
**Problem:** Nginx couldn't start because port 80 was already in use, or old nginx processes weren't being killed properly.

**Fix Applied:**
- Updated `scripts/start.sh` to:
  - Better process detection and killing
  - Check and free port 80 before starting
  - Longer wait times between stop attempts
  - Clearer error messages

### 3. **Ollama Not Found**
**Problem:** Ollama might not be installed or not accessible from WSL.

**Solutions:**
1. **If Ollama is installed on Windows:** You need to access it from WSL
   - Ollama on Windows typically runs on `http://localhost:11434`
   - From WSL, use: `http://127.0.0.1:11434` or `http://$(hostname).local:11434`
   - Update `.env`: `OLLAMA_BASE_URL=http://127.0.0.1:11434`

2. **If Ollama is not installed:**
   - Install on Windows: Download from https://ollama.ai
   - Or install in WSL: Follow instructions at https://ollama.ai/docs/installation

3. **Alternative:** Use OpenAI API instead
   - Set `USE_OLLAMA=false` in `.env`
   - Add your OpenAI API key: `auth_key=your_key_here`

## How to Start Everything

### Step 1: Check Setup
```bash
npm run setup:check
```

This will verify:
- Python is installed
- Nginx is installed
- Ollama is accessible (or suggest alternatives)
- `.env` file exists
- Virtual environment is ready
- Dependencies are installed

### Step 2: Start Backend
```bash
npm run start:backend
```

This will:
- Create/update virtual environment
- Install all Python dependencies
- Start Flask server on port 5000
- Show logs location

### Step 3: Start Frontend
```bash
npm start
```

This will:
- Stop any existing Nginx processes
- Free port 80
- Start Nginx with your configuration
- Serve frontend on http://localhost

### Step 4: Verify Everything Works
1. Open http://localhost in your browser
2. Check backend health: http://localhost:5000/api/health
3. Try uploading a document and generating stories

## Troubleshooting

### Backend Won't Start
1. Check logs: `tail -f backend.log`
2. Verify dependencies: `source venv/bin/activate && pip list`
3. Reinstall: `rm -rf venv && npm run start:backend`

### Nginx Won't Start
1. Check if port 80 is free: `sudo lsof -i :80`
2. Force stop: `npm run force-stop`
3. Check config: `sudo nginx -t -c config/nginx.conf`
4. Check logs: `sudo tail /var/log/nginx/error.log`

### Stories Not Generating
1. **Check Ollama is running:**
   - Windows: Check if Ollama service is running
   - WSL: `curl http://localhost:11434/api/tags` (if curl is installed)
   
2. **Check backend logs:**
   ```bash
   tail -f backend.log
   ```
   Look for errors related to:
   - Ollama connection failures
   - Model not found
   - API errors

3. **Test backend directly:**
   ```bash
   curl http://localhost:5000/api/health
   ```

4. **Check browser console:**
   - Open Developer Tools (F12)
   - Check Console tab for JavaScript errors
   - Check Network tab for failed API requests

### Common Error Messages

**"ModuleNotFoundError: No module named 'flask'"**
- Solution: Dependencies not installed. Run `npm run start:backend` again.

**"bind() to 0.0.0.0:80 failed (98: Address already in use)"**
- Solution: Run `npm run force-stop` then `npm start`

**"Connection refused" when accessing Ollama**
- Solution: Start Ollama on Windows or install in WSL

**"500 Internal Server Error" when generating stories**
- Solution: Check `backend.log` for specific error. Usually:
  - Ollama not running
  - Model not pulled (`ollama pull llama3.2`)
  - Invalid file format

## Next Steps

1. **Install/Start Ollama:**
   - If on Windows: Download and install from https://ollama.ai
   - Start Ollama service
   - Pull model: `ollama pull llama3.2` (run from Windows or WSL)

2. **Update .env if needed:**
   ```env
   USE_OLLAMA=true
   OLLAMA_BASE_URL=http://127.0.0.1:11434  # If Ollama on Windows
   OLLAMA_MODEL=llama3.2
   ```

3. **Restart backend:**
   ```bash
   npm run stop:backend
   npm run start:backend
   ```

4. **Test the flow:**
   - Start backend: `npm run start:backend`
   - Start frontend: `npm start`
   - Open browser: http://localhost
   - Upload a document (.docx, .doc, .txt, .md)
   - Click "Generate User Stories"
   - Wait for generation (may take a few minutes)
   - View stories on the stories page

