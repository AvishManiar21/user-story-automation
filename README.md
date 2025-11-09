# User Story Automation Frontend

Frontend web application for generating and managing user stories. Designed to work with a Python backend.

## Quick Start

**Run from WSL terminal:**

```bash
# Navigate to project
cd /mnt/c/Users/avish/OneDrive/Desktop/User\ Story\ automation\ frontend

# Start server
npm start

# Stop server
npm stop

# Check status
npm run status
```

**Access:** http://localhost

## Project Structure

```
.
├── pages/              # HTML pages
│   ├── index.html
│   └── stories.html
├── assets/             # Static assets
│   ├── css/
│   └── js/
├── config/             # Configuration
│   └── nginx.conf
├── scripts/            # Utility scripts
│   ├── start.sh
│   └── stop.sh
├── docs/               # Documentation
│   ├── SETUP.md
│   ├── INTEGRATION.md
│   └── TROUBLESHOOTING.md
└── package.json        # npm scripts
```

## Features

- **Page 1**: Project description input and story generation
- **Page 2**: Dynamic user stories list with details (Title, Description, DoD, Test Cases)
- Supports any number of user stories
- Ready for Python backend integration

## Backend Integration

See [docs/INTEGRATION.md](docs/INTEGRATION.md) for integration guide.

**Expected API endpoints:**
- `POST /api/generate-stories` - Generate stories from project description
- `POST /api/integrate-story` - Integrate single story
- `POST /api/integrate-all` - Integrate all stories

**Story format:**
```json
{
  "stories": [{
    "id": 1,
    "title": "...",
    "description": "...",
    "definitionOfDone": "...",
    "testCases": "..."
  }]
}
```

## Documentation

- [docs/SETUP.md](docs/SETUP.md) - Setup instructions
- [docs/INTEGRATION.md](docs/INTEGRATION.md) - Backend integration guide
- [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) - Common issues
- [docs/GITHUB.md](docs/GITHUB.md) - GitHub setup guide

## Commands

```bash
npm start      # Start server
npm stop       # Stop server
npm run restart # Restart server
npm test       # Test nginx config
npm run status # Check if running
```
