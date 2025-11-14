"""
Flask API server for User Story Automation
Handles document uploads and generates user stories using autoAgile backend
"""
import os
import json
import tempfile
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
import sys
from dotenv import load_dotenv

# Load environment variables from .env file
# Explicitly specify the .env file path to ensure it's found
env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
load_dotenv(dotenv_path=env_path)

# Debug: Check if API key was loaded (don't print the actual key)
if os.environ.get('auth_key') or os.environ.get('OPENAI_API_KEY'):
    print("✅ API key loaded from environment")
else:
    print("⚠️  WARNING: No API key found in environment variables")
    print(f"   Looking for .env at: {env_path}")
    if os.path.exists(env_path):
        print(f"   .env file exists at: {env_path}")
    else:
        print(f"   .env file NOT found at: {env_path}")

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Import autoAgile modules
from autoAgile.utils.prompts import (
    extract_text_from_docx, refine_doc, extract_functionarity,
    extract_epics, get_epics, generate_test_cases, refine_requirements, rat
)
from langchain_openai import ChatOpenAI
from langchain_ollama import ChatOllama

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend

# Configuration
UPLOAD_FOLDER = tempfile.gettempdir()
ALLOWED_EXTENSIONS = {'docx', 'doc', 'txt', 'md'}
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

# Get API provider from environment (default to ollama for free usage)
USE_OLLAMA = os.environ.get('USE_OLLAMA', 'true').lower() == 'true'
OLLAMA_BASE_URL = os.environ.get('OLLAMA_BASE_URL', 'http://localhost:11434')
OLLAMA_MODEL = os.environ.get('OLLAMA_MODEL', 'llama3.2')  # or 'mistral', 'qwen2.5', etc.

# Get API key from environment (same way autoAgile does) - only needed for OpenAI
# autoAgile uses: api_key = os.environ['auth_key']
# We use get() to avoid KeyError, but should match autoAgile behavior
API_KEY = os.environ.get('auth_key') or os.environ.get('OPENAI_API_KEY')
if not USE_OLLAMA:
    if not API_KEY:
        print("WARNING: No API key found in environment variables. Set 'auth_key' or 'OPENAI_API_KEY'")
    else:
        # Strip any whitespace (in case .env file has trailing spaces)
        API_KEY = API_KEY.strip()
        print(f"✅ OpenAI API key loaded: {API_KEY[:10]}...{API_KEY[-4:]}")
else:
    print(f"✅ Using Ollama (no API key needed)")
    print(f"   Ollama URL: {OLLAMA_BASE_URL}")
    print(f"   Model: {OLLAMA_MODEL}")

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def convert_stories_to_frontend_format(epics_json, test_cases_json, requirements_text):
    """
    Convert backend output format to frontend format
    Backend returns: { "User Stories": [...], "Test Cases": {...} }
    Frontend expects: [{ title, description, definitionOfDone, testCases }]
    """
    try:
        epics_data = json.loads(epics_json) if isinstance(epics_json, str) else epics_json
        test_cases_data = json.loads(test_cases_json) if isinstance(test_cases_json, str) else test_cases_json
        
        user_stories = epics_data.get('User Stories', [])
        test_cases_dict = test_cases_data.get('Test Cases', {})
        
        frontend_stories = []
        
        for idx, story in enumerate(user_stories):
            # Extract user story title/description
            story_text = story.get('User Story', '')
            
            # Extract definition of done from deliverables
            deliverables = story.get('Deliverables', {})
            dod_parts = []
            for key, value in deliverables.items():
                if isinstance(value, dict):
                    dod_parts.append(f"{key}: {value.get('definition_of_done', value.get('description', ''))}")
                else:
                    dod_parts.append(f"{key}: {value}")
            definition_of_done = '\n'.join(dod_parts) if dod_parts else 'To be defined'
            
            # Get test cases for this story (try to match by index or story text)
            test_cases = test_cases_dict.get(str(idx + 1), '')
            if not test_cases:
                # Try to find by story text
                for key, value in test_cases_dict.items():
                    if story_text.lower() in str(value).lower() or str(value).lower() in story_text.lower():
                        test_cases = value
                        break
            
            # If test_cases is a dict, convert to string
            if isinstance(test_cases, dict):
                test_cases = json.dumps(test_cases, indent=2)
            elif not isinstance(test_cases, str):
                test_cases = str(test_cases)
            
            frontend_stories.append({
                'id': idx + 1,
                'title': story_text[:100] + '...' if len(story_text) > 100 else story_text,
                'description': story_text,
                'definitionOfDone': definition_of_done,
                'testCases': test_cases
            })
        
        return frontend_stories
    except Exception as e:
        print(f"Error converting stories: {e}")
        # Return a basic format if conversion fails
        return [{
            'id': 1,
            'title': 'Error processing stories',
            'description': str(e),
            'definitionOfDone': '-',
            'testCases': '-'
        }]

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'ok', 
        'provider': 'ollama' if USE_OLLAMA else 'openai',
        'api_key_configured': bool(API_KEY) if not USE_OLLAMA else True,
        'ollama_url': OLLAMA_BASE_URL if USE_OLLAMA else None,
        'model': OLLAMA_MODEL if USE_OLLAMA else None
    })

@app.route('/api/generate-stories', methods=['POST'])
def generate_stories():
    """Generate user stories from uploaded document"""
    try:
        # Check if file is present
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'File type not allowed. Please upload .docx, .doc, .txt, or .md files'}), 400

        # Only check API key if using OpenAI (not Ollama)
        if not USE_OLLAMA and not API_KEY:
            return jsonify({'error': 'OpenAI API key not configured. Set auth_key environment variable'}), 500

        # Save uploaded file temporarily
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        try:
            # Initialize model (Ollama or OpenAI)
            temp = 0.3
            
            if USE_OLLAMA:
                # Use Ollama (free, local, no API key needed)
                model_name = request.form.get('model', OLLAMA_MODEL)
                print(f"Using Ollama model: {model_name}")
                chat = ChatOllama(
                    model=model_name,
                    temperature=temp,
                    base_url=OLLAMA_BASE_URL
                )
            else:
                # Use OpenAI (requires API key)
                model = request.form.get('model', 'gpt-4o')
                
                # Get API key the same way autoAgile does
                api_key_clean = os.environ.get('auth_key', '').strip()
                if not api_key_clean:
                    api_key_clean = os.environ.get('OPENAI_API_KEY', '').strip()
                
                if not api_key_clean:
                    return jsonify({'error': 'OpenAI API key not configured. Set auth_key environment variable'}), 500
                
                print(f"Using OpenAI model: {model}")
                print(f"Using API key: {api_key_clean[:10]}...{api_key_clean[-4:]}")
                
                chat = ChatOpenAI(model=model, temperature=temp, openai_api_key=api_key_clean)
            
            # Extract text from document
            if filename.endswith('.docx') or filename.endswith('.doc'):
                extracted_text = extract_text_from_docx(filepath)
            else:
                # For txt/md files, read directly
                with open(filepath, 'r', encoding='utf-8') as f:
                    extracted_text = f.read()
            
            # Process document using autoAgile
            mode = "prod"
            requirements = rat(refine_doc, extract_functionarity, extracted_text, chat, mode)
            deliverables = rat(refine_requirements, extract_epics, requirements, chat, mode)
            epics = get_epics(deliverables, chat)
            test_cases = rat(refine_requirements, generate_test_cases, requirements, chat, mode)
            
            # Convert to frontend format
            stories = convert_stories_to_frontend_format(epics, test_cases, requirements)
            
            return jsonify({
                'success': True,
                'stories': stories,
                'count': len(stories)
            })
            
        finally:
            # Clean up temporary file
            if os.path.exists(filepath):
                os.remove(filepath)
                
    except Exception as e:
        print(f"Error generating stories: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Error generating stories: {str(e)}'}), 500

@app.route('/api/integrate-story', methods=['POST'])
def integrate_story():
    """Integrate a single user story (placeholder for future implementation)"""
    data = request.json
    story_id = data.get('storyId')
    
    return jsonify({
        'success': True,
        'message': f'Story {story_id} integrated successfully',
        'storyId': story_id
    })

@app.route('/api/integrate-all', methods=['POST'])
def integrate_all():
    """Integrate all user stories (placeholder for future implementation)"""
    data = request.json
    story_ids = data.get('storyIds', [])
    
    return jsonify({
        'success': True,
        'message': f'All {len(story_ids)} stories integrated successfully',
        'storyIds': story_ids
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)

