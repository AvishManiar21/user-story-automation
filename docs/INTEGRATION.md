# Backend Integration Guide

## Overview

Connect your Python backend to generate user stories from project descriptions.

## API Endpoints Required

### 1. Generate Stories
**POST** `/api/generate-stories`

**Request:**
```json
{
  "projectDescription": "Your project description"
}
```

**Response:**
```json
{
  "stories": [{
    "id": 1,
    "title": "As a user, I want to...",
    "description": "...",
    "definitionOfDone": "...",
    "testCases": "..."
  }]
}
```

### 2. Integrate Story
**POST** `/api/integrate-story`
```json
{ "storyId": 1 }
```

### 3. Integrate All
**POST** `/api/integrate-all`
```json
{ "storyIds": [1, 2, 3] }
```

## Python Backend Example

```python
from flask import Flask, request, jsonify
from flask_cors import CORS
from your_library import generate_user_stories

app = Flask(__name__)
CORS(app)

@app.route('/api/generate-stories', methods=['POST'])
def generate_stories():
    data = request.json
    project_description = data.get('projectDescription')
    
    # Call your Python library
    stories = generate_user_stories(project_description)
    
    # Format stories
    formatted = []
    for idx, story in enumerate(stories, 1):
        formatted.append({
            "id": idx,
            "title": story.get('title', ''),
            "description": story.get('description', ''),
            "definitionOfDone": story.get('definition_of_done', ''),
            "testCases": story.get('test_cases', '')
        })
    
    return jsonify({"stories": formatted})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

## Update Frontend

Edit `assets/js/script.js` and uncomment the TODO sections:

1. **`generateUserStories()`** - Uncomment API call
2. **`loadUserStories()`** - Uncomment API call
3. **`integrateStory()`** - Uncomment API call
4. **`integrateAll()`** - Uncomment API call

**Example:**
```javascript
// Replace TODO section with:
fetch('http://localhost:5000/api/generate-stories', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ projectDescription: projectDescription })
})
.then(response => response.json())
.then(data => {
    updateUserStories(data.stories);
    window.location.href = 'stories.html';
})
```

## Testing

1. Start Python backend: `python app.py`
2. Start frontend: `npm start`
3. Open: http://localhost
4. Enter project description and generate stories

## CORS Setup

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
