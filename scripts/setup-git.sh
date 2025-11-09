#!/bin/bash

# Setup Git and push to GitHub using SSH
# Run this from WSL: ./scripts/setup-git.sh

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$( cd "$SCRIPT_DIR/.." && pwd )"

cd "$PROJECT_DIR"

echo "📦 Setting up Git repository..."

# Initialize git if not already
if [ ! -d .git ]; then
    git init
    echo "✅ Git initialized"
else
    echo "ℹ️  Git already initialized"
fi

# Check if remote exists
if git remote get-url origin > /dev/null 2>&1; then
    echo "ℹ️  Remote 'origin' already exists"
    read -p "Do you want to update it? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        read -p "Enter GitHub SSH URL (e.g., git@github.com:username/repo.git): " GITHUB_URL
        git remote set-url origin "$GITHUB_URL"
        echo "✅ Remote updated"
    fi
else
    read -p "Enter GitHub SSH URL (e.g., git@github.com:username/repo.git): " GITHUB_URL
    git remote add origin "$GITHUB_URL"
    echo "✅ Remote added"
fi

# Add all files
git add .

# Check if there are changes to commit
if git diff --staged --quiet; then
    echo "ℹ️  No changes to commit"
else
    read -p "Enter commit message (or press Enter for default): " COMMIT_MSG
    if [ -z "$COMMIT_MSG" ]; then
        COMMIT_MSG="Initial commit: User Story Automation Frontend"
    fi
    git commit -m "$COMMIT_MSG"
    echo "✅ Changes committed"
fi

# Push to GitHub
echo ""
echo "🚀 Pushing to GitHub..."
read -p "Push to main branch? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    BRANCH="main"
else
    read -p "Enter branch name (default: main): " BRANCH
    BRANCH=${BRANCH:-main}
fi

# Set default branch if needed
git branch -M "$BRANCH" 2>/dev/null

# Push
if git push -u origin "$BRANCH"; then
    echo ""
    echo "✅ Successfully pushed to GitHub!"
    echo "📍 Repository: $GITHUB_URL"
else
    echo ""
    echo "❌ Push failed. Common issues:"
    echo "   1. SSH key not set up: ssh-keygen -t ed25519 -C 'your_email@example.com'"
    echo "   2. SSH key not added to GitHub: https://github.com/settings/keys"
    echo "   3. Repository doesn't exist on GitHub"
    echo ""
    echo "Create repository on GitHub first:"
    echo "   https://github.com/new"
fi

