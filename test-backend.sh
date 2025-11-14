#!/bin/bash

# Test the backend directly with insulinPump.docx
# This simulates what the Flask API does

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$( cd "$SCRIPT_DIR/.." && pwd )"

cd "$PROJECT_DIR"

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "❌ Error: .env file not found!"
    echo "Create .env file with: auth_key=your_api_key_here"
    exit 1
fi

# Load .env file
export $(cat .env | grep -v '^#' | xargs)

# Check if API key is set
if [ -z "$auth_key" ]; then
    echo "❌ Error: auth_key not found in .env file"
    exit 1
fi

# Test document path
TEST_DOC="$PROJECT_DIR/autoAgile/tests/docs/insulinPump.docx"

if [ ! -f "$TEST_DOC" ]; then
    echo "❌ Error: Test document not found at $TEST_DOC"
    exit 1
fi

echo "🧪 Testing autoAgile backend with insulinPump.docx"
echo "📄 Document: $TEST_DOC"
echo ""

# Run autoAgile.py directly
cd autoAgile
python3 autoAgile.py "$TEST_DOC" gpt-4-turbo

echo ""
echo "✅ Test completed! Check output above for results."

