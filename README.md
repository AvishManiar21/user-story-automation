# User Story Automation Frontend

Frontend web application for generating and managing user stories. Designed to work with a Python backend.

## Quick Start

**Run from WSL terminal:**

```bash
# Navigate to project
cd /mnt/c/Users/avish/OneDrive/Desktop/User\ Story\ automation\ frontend/user-story-automation

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
│   ├── index.html      # Main page - project input
│   └── stories.html    # Stories list and details
├── assets/             # Static assets
│   ├── css/
│   │   └── styles.css
│   └── js/
│       └── script.js
├── config/             # Configuration
│   └── nginx.conf      # Nginx server configuration
├── scripts/            # Utility scripts
│   ├── start.sh        # Start nginx server
│   └── stop.sh         # Stop nginx server
├── docs/               # Documentation
│   ├── SETUP.md        # Setup instructions
│   └── INTEGRATION.md  # Backend integration guide
└── package.json        # npm scripts
```

## Features

- **Page 1 (index.html)**: Project description input and story generation
- **Page 2 (stories.html)**: Dynamic user stories list with details
  - Title, Description, Definition of Done, Test Cases
  - Supports any number of user stories
  - Individual and bulk integration options

## Commands

```bash
npm start      # Start nginx server
npm stop       # Stop nginx server
npm run restart # Restart nginx server
npm test       # Test nginx configuration
npm run status # Check if server is running
```

## Backend Integration

See [docs/INTEGRATION.md](docs/INTEGRATION.md) for detailed integration guide.

**Required API endpoints:**
- `POST /api/generate-stories` - Generate stories from project description
- `POST /api/integrate-story` - Integrate single story
- `POST /api/integrate-all` - Integrate all stories

**Story format:**
```json
{
  "stories": [{
    "id": 1,
    "title": "Story title",
    "description": "Story description",
    "definitionOfDone": "Definition of done",
    "testCases": "Test cases"
  }]
}
```

## Documentation

- [docs/SETUP.md](docs/SETUP.md) - Setup and installation instructions
- [docs/INTEGRATION.md](docs/INTEGRATION.md) - Backend integration guide
