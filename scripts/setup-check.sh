#!/bin/bash

# Setup and verification script
# Checks all prerequisites and helps set up the environment

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$( cd "$SCRIPT_DIR/.." && pwd )"

cd "$PROJECT_DIR"

echo "🔍 Checking setup..."
echo ""

# Check Python
echo "1️⃣  Checking Python..."
if command -v python3 >/dev/null 2>&1; then
    PYTHON_VERSION=$(python3 --version)
    echo "   ✅ $PYTHON_VERSION"
else
    echo "   ❌ Python3 not found. Install with: sudo apt-get install python3 python3-venv"
    exit 1
fi

# Check Nginx
echo ""
echo "2️⃣  Checking Nginx..."
if command -v nginx >/dev/null 2>&1; then
    NGINX_VERSION=$(nginx -v 2>&1)
    echo "   ✅ $NGINX_VERSION"
else
    echo "   ❌ Nginx not found. Install with: sudo apt-get install -y nginx"
    exit 1
fi

# Check Ollama
echo ""
echo "3️⃣  Checking Ollama..."
if command -v ollama >/dev/null 2>&1; then
    echo "   ✅ Ollama is installed"
    # Check if Ollama is running
    if curl -s http://localhost:11434/api/tags >/dev/null 2>&1; then
        echo "   ✅ Ollama is running"
        # Check if model is available
        if ollama list 2>/dev/null | grep -q llama3.2; then
            echo "   ✅ llama3.2 model is available"
        else
            echo "   ⚠️  llama3.2 model not found. Run: ollama pull llama3.2"
        fi
    else
        echo "   ⚠️  Ollama is not running. Start with: ollama serve"
    fi
else
    echo "   ⚠️  Ollama not found. Install from: https://ollama.ai"
    echo "   Or use OpenAI API by setting USE_OLLAMA=false in .env"
fi

# Check .env file
echo ""
echo "4️⃣  Checking .env file..."
if [ -f ".env" ]; then
    echo "   ✅ .env file exists"
    if grep -q "USE_OLLAMA=true" .env 2>/dev/null; then
        echo "   ✅ Using Ollama (configured)"
    elif grep -q "auth_key\|OPENAI_API_KEY" .env 2>/dev/null; then
        echo "   ✅ Using OpenAI API (configured)"
    else
        echo "   ⚠️  .env exists but no provider configured"
    fi
else
    echo "   ⚠️  .env file not found. Creating default..."
    cat > .env << EOF
# Ollama Configuration (Free, Local - No API Key Needed)
USE_OLLAMA=true
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2
EOF
    echo "   ✅ Created default .env file with Ollama configuration"
fi

# Check virtual environment
echo ""
echo "5️⃣  Checking Python virtual environment..."
if [ -d "venv" ]; then
    echo "   ✅ Virtual environment exists"
    if [ -f "venv/bin/python" ]; then
        echo "   ✅ Virtual environment is valid"
    else
        echo "   ⚠️  Virtual environment is corrupted. Will recreate..."
        rm -rf venv
    fi
else
    echo "   ⚠️  Virtual environment not found. Will create on first start..."
fi

# Check dependencies
echo ""
echo "6️⃣  Checking Python dependencies..."
if [ -d "venv" ] && [ -f "venv/bin/python" ]; then
    source venv/bin/activate
    if python -c "import flask" 2>/dev/null; then
        echo "   ✅ Flask is installed"
    else
        echo "   ⚠️  Dependencies not installed. Will install on first start..."
    fi
    deactivate
else
    echo "   ⚠️  Cannot check (venv not ready). Will install on first start..."
fi

# Check project structure
echo ""
echo "7️⃣  Checking project structure..."
MISSING_FILES=0
for file in "app.py" "requirements.txt" "config/nginx.conf" "pages/index.html" "pages/stories.html"; do
    if [ -f "$file" ] || [ -d "$file" ]; then
        echo "   ✅ $file"
    else
        echo "   ❌ $file (missing)"
        MISSING_FILES=$((MISSING_FILES + 1))
    fi
done

if [ $MISSING_FILES -gt 0 ]; then
    echo ""
    echo "❌ Some required files are missing!"
    exit 1
fi

echo ""
echo "✅ Setup check complete!"
echo ""
echo "📋 Next steps:"
echo "   1. Start backend:  npm run start:backend"
echo "   2. Start frontend: npm start"
echo "   3. Open browser:   http://localhost"
echo ""

