# Backend Integration Guide

This guide explains how to connect your Python backend to the frontend application.

## Overview

The frontend expects a Python backend API running on `http://localhost:5000` (or your configured backend URL). The frontend will send HTTP requests to generate and manage user stories.

## Required API Endpoints

### 1. Generate Stories

**Endpoint:** `POST /api/generate-stories`

**Request:**
```json
{
  "projectDescription": "Your project description text"
}
```

**Response:**
```json
{
  "stories": [
    {
      "id": 1,
      "title": "As a user, I want to...",
      "description": "Full story description",
      "definitionOfDone": "Definition of done criteria",
      "testCases": "Test cases for this story"
    }
  ]
}
```

### 2. Integrate Single Story

**Endpoint:** `POST /api/integrate-story`

**Request:**
```json
{
  "storyId": 1
}
```

**Response:**
```json
{
  "success": true,
  "message": "Story integrated successfully"
}
```

### 3. Integrate All Stories

**Endpoint:** `POST /api/integrate-all`

**Request:**
```json
{
  "storyIds": [1, 2, 3]
}
```

**Response:**
```json
{
  "success": true,
  "message": "All stories integrated successfully"
}
```

## Python Backend Example (Flask)

```python
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend

@app.route('/api/generate-stories', methods=['POST'])
def generate_stories():
    data = request.json
    project_description = data.get('projectDescription', '')
    
    # Call your story generation function
    stories = your_story_generator(project_description)
    
    # Format response
    formatted_stories = []
    for idx, story in enumerate(stories, 1):
        formatted_stories.append({
            "id": idx,
            "title": story.get('title', ''),
            "description": story.get('description', ''),
            "definitionOfDone": story.get('definition_of_done', ''),
            "testCases": story.get('test_cases', '')
        })
    
    return jsonify({"stories": formatted_stories})

@app.route('/api/integrate-story', methods=['POST'])
def integrate_story():
    data = request.json
    story_id = data.get('storyId')
    
    # Your integration logic here
    # ...
    
    return jsonify({"success": True, "message": "Story integrated"})

@app.route('/api/integrate-all', methods=['POST'])
def integrate_all():
    data = request.json
    story_ids = data.get('storyIds', [])
    
    # Your integration logic here
    # ...
    
    return jsonify({"success": True, "message": "All stories integrated"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

## Python Backend Example (FastAPI)

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ProjectDescription(BaseModel):
    projectDescription: str

class StoryId(BaseModel):
    storyId: int

class StoryIds(BaseModel):
    storyIds: list[int]

@app.post("/api/generate-stories")
def generate_stories(project: ProjectDescription):
    # Your story generation logic
    stories = your_story_generator(project.projectDescription)
    return {"stories": stories}

@app.post("/api/integrate-story")
def integrate_story(story: StoryId):
    # Your integration logic
    return {"success": True, "message": "Story integrated"}

@app.post("/api/integrate-all")
def integrate_all(stories: StoryIds):
    # Your integration logic
    return {"success": True, "message": "All stories integrated"}
```

## Frontend Configuration

1. **Edit `assets/js/script.js`**
2. **Uncomment the TODO sections** in these functions:
   - `generateUserStories()` - Line 28-41
   - `loadUserStories()` - Line 65-74
   - `integrateStory()` - Line 190-194
   - `integrateAll()` - Line 210-214

3. **Update the API base URL** if your backend runs on a different port:
   ```javascript
   const API_BASE_URL = 'http://localhost:5000';
   ```

## Testing

1. Start your Python backend:
   ```bash
   python app.py
   # or
   uvicorn main:app --reload
   ```

2. Start the frontend:
   ```bash
   npm start
   ```

3. Open browser: http://localhost

4. Enter a project description and click "Generate User Stories"

## CORS Configuration

Make sure CORS is enabled in your backend to allow requests from the frontend.

**Flask:**
```python
from flask_cors import CORS
CORS(app)
```

**FastAPI:**
```python
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost"])
```
