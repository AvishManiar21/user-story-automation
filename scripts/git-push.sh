#!/bin/bash

# Quick git push script
# Run this from WSL: ./scripts/git-push.sh

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$( cd "$SCRIPT_DIR/.." && pwd )"

cd "$PROJECT_DIR"

# Check if git is initialized
if [ ! -d .git ]; then
    echo "❌ Git not initialized. Run: ./scripts/setup-git.sh first"
    exit 1
fi

# Add all files
git add .

# Commit
read -p "Enter commit message: " COMMIT_MSG
if [ -z "$COMMIT_MSG" ]; then
    COMMIT_MSG="Update: $(date +%Y-%m-%d)"
fi

git commit -m "$COMMIT_MSG"

# Push
BRANCH=$(git branch --show-current 2>/dev/null || echo "main")
git push origin "$BRANCH"

echo "✅ Pushed to GitHub"

