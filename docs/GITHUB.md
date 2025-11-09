# GitHub Setup Guide

## Prerequisites

1. **Git installed in WSL:**
   ```bash
   sudo apt-get update
   sudo apt-get install -y git
   ```

2. **SSH key set up:**
   ```bash
   # Check if SSH key exists
   ls -la ~/.ssh/id_ed25519.pub
   
   # If not, create one
   ssh-keygen -t ed25519 -C "your_email@example.com"
   ```

3. **SSH key added to GitHub:**
   - Copy your public key: `cat ~/.ssh/id_ed25519.pub`
   - Go to: https://github.com/settings/keys
   - Click "New SSH key" and paste your key

## Setup Repository

### Step 1: Create Repository on GitHub

1. Go to: https://github.com/new
2. Repository name: `user-story-frontend` (or your choice)
3. Description: "Frontend for User Story Automation"
4. Choose Public or Private
5. **Don't** initialize with README, .gitignore, or license
6. Click "Create repository"

### Step 2: Run Setup Script

**From WSL terminal:**
```bash
cd /mnt/c/Users/avish/OneDrive/Desktop/User\ Story\ automation\ frontend

# Run setup script
npm run git:setup
# or
./scripts/setup-git.sh
```

**The script will:**
- Initialize git (if needed)
- Ask for GitHub SSH URL (e.g., `git@github.com:username/repo.git`)
- Add all files
- Commit changes
- Push to GitHub

## Quick Push (After Setup)

```bash
# Quick push with commit message
npm run git:push
# or
./scripts/git-push.sh
```

## Manual Git Commands

```bash
# Initialize
git init

# Add remote
git remote add origin git@github.com:username/repo.git

# Add files
git add .

# Commit
git commit -m "Initial commit"

# Push
git push -u origin main
```

## Verify SSH Connection

```bash
# Test SSH connection to GitHub
ssh -T git@github.com
```

You should see: "Hi username! You've successfully authenticated..."

