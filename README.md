# User Story Automation

Full-stack web application for generating and managing user stories from project documents using GPT.

## Quick Start

**Prerequisites:**
- Python 3.8+ with pip
- Node.js and npm (for scripts)
- Nginx (installed in WSL)
- OpenAI API key

**Setup:**

1. **Configure API Key:**
   ```bash
   cd /mnt/c/Users/avish/OneDrive/Desktop/User\ Story\ automation\ frontend/user-story-automation
   
   # Create .env file
   echo "auth_key=your_openai_api_key_here" > .env
   ```

2. **Start Backend (Flask API):**
   ```bash
   npm run start:backend
   ```
   This will:
   - Create a Python virtual environment
   - Install dependencies
   - Start Flask server on port 5000

3. **Start Frontend (Nginx):**
   ```bash
   npm start
   ```

4. **Access:** http://localhost

**Or start both at once:**
```bash
npm run start:all
```

## Project Structure

```
.
├── pages/              # HTML pages
│   ├── index.html      # Main page - document upload
│   └── stories.html    # Stories list and details
├── assets/             # Static assets
│   ├── css/
│   │   └── styles.css
│   └── js/
│       └── script.js   # Frontend JavaScript
├── autoAgile/          # Python backend module
│   ├── autoAgile.py    # Main processing logic
│   ├── save_output.py  # Output handling
│   └── utils/          # Utilities and prompts
├── config/             # Configuration
│   └── nginx.conf      # Nginx server configuration
├── scripts/            # Utility scripts
│   ├── start.sh        # Start nginx server
│   ├── stop.sh         # Stop nginx server
│   └── start-backend.sh # Start Flask backend
├── docs/               # Documentation
│   ├── SETUP.md        # Setup instructions
│   └── INTEGRATION.md  # Backend integration guide
├── app.py              # Flask API server
├── requirements.txt    # Python dependencies
├── .env.example        # Environment variables template
└── package.json        # npm scripts
```

## Features

- **Document Upload**: Upload .docx, .doc, .txt, or .md files
- **AI-Powered Generation**: Uses GPT to analyze documents and generate user stories
- **Dynamic Story Display**: Automatically displays all generated stories
- **Story Details**: Each story includes:
  - Title and Description
  - Definition of Done
  - Test Cases
- **Integration**: Individual and bulk integration options

## How It Works

1. **Upload Document**: User selects a project document (.docx, .doc, .txt, or .md)
2. **Backend Processing**: 
   - Flask API receives the document
   - autoAgile module extracts text and processes it
   - GPT API generates requirements, epics, and test cases
3. **Display Results**: Frontend displays all generated user stories with details

## Commands

**Frontend (Nginx):**
```bash
npm start      # Start nginx server
npm stop       # Stop nginx server
npm run restart # Restart nginx server
npm test       # Test nginx configuration
npm run status # Check if server is running
```

**Backend (Flask):**
```bash
npm run start:backend  # Start Flask API server
```

**Both:**
```bash
npm run start:all  # Start both frontend and backend
```

## API Endpoints

The Flask backend provides these endpoints:

- `POST /api/generate-stories` - Upload document and generate user stories
  - Request: FormData with `file` field
  - Response: `{ success: true, stories: [...], count: N }`

- `POST /api/integrate-story` - Integrate a single story
  - Request: `{ storyId: number }`
  - Response: `{ success: true, message: "...", storyId: number }`

- `POST /api/integrate-all` - Integrate all stories
  - Request: `{ storyIds: [number] }`
  - Response: `{ success: true, message: "...", storyIds: [number] }`

- `GET /api/health` - Health check endpoint

**Story Format:**
```json
{
  "id": 1,
  "title": "Story title",
  "description": "Full story description",
  "definitionOfDone": "Definition of done criteria",
  "testCases": "Test cases for verification"
}
```

## Configuration

1. **Environment Variables:**
   - Copy `.env.example` to `.env`
   - Add your OpenAI API key: `auth_key=your_api_key_here`

2. **Nginx Configuration:**
   - API requests are proxied from `/api/*` to Flask on port 5000
   - Frontend is served from `pages/` directory
   - Static assets from `assets/` directory

## Troubleshooting

- **Backend not responding**: Make sure Flask is running on port 5000 (`npm run start:backend`)
- **API key error**: Check `.env` file has `auth_key` set correctly
- **Port 80 in use**: Run `npm run force-stop` then `npm start`
- **File upload fails**: Check file size (max 16MB) and format (.docx, .doc, .txt, .md)

## Documentation

- [docs/SETUP.md](docs/SETUP.md) - Detailed setup and installation instructions
- [docs/INTEGRATION.md](docs/INTEGRATION.md) - Backend integration guide
