"""
Flask API server for User Story Automation
Handles document uploads and generates user stories using autoAgile backend
"""
import os
import json
import tempfile
from datetime import datetime
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
import sys
from dotenv import load_dotenv

# Load environment variables from .env file
# Explicitly specify the .env file path to ensure it's found
env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
load_dotenv(dotenv_path=env_path)

# Debug: Check if .env file exists
if os.path.exists(env_path):
    print(f"[OK] .env file found: {env_path}")
    # Note: API keys can be commented out if using Ollama (no API key needed)
else:
    print(f"[WARNING] .env file NOT found at: {env_path}")
    print(f"   Note: .env is optional - will use defaults (Ollama)")
    print(f"   To customize, create .env with LLM_PROVIDER=ollama")

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Import autoAgile modules
from autoAgile.utils.prompts import (
    extract_text_from_docx, refine_doc, extract_functionarity,
    extract_epics, get_epics, generate_test_cases, refine_requirements, rat
)
from autoAgile.save_output import save_json_output
from autoAgile.utils.validation import validate_output, validate_requirements_completeness, print_validation_report
from langchain_openai import ChatOpenAI
from langchain_ollama import ChatOllama
from langchain_groq import ChatGroq

# Configure Flask to serve static files and templates
app = Flask(__name__, 
            static_folder='assets',
            static_url_path='/assets',
            template_folder='pages')
CORS(app)  # Enable CORS for frontend

# Configuration
UPLOAD_FOLDER = tempfile.gettempdir()
ALLOWED_EXTENSIONS = {'docx', 'doc', 'txt', 'md'}
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

# ============================================================
# LLM Provider Configuration (from .env)
# ============================================================
LLM_PROVIDER = os.environ.get('LLM_PROVIDER', 'ollama').lower()

# Groq Configuration
GROQ_API_KEY = os.environ.get('GROQ_API_KEY', '').strip()

# OpenAI Configuration
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', '') or os.environ.get('auth_key', '')
OPENAI_API_KEY = OPENAI_API_KEY.strip() if OPENAI_API_KEY else ''

# Ollama Configuration (fallback)
OLLAMA_BASE_URL = os.environ.get('OLLAMA_BASE_URL', 'http://localhost:11434')
OLLAMA_MODEL = os.environ.get('OLLAMA_MODEL', 'llama3.2:latest')

# Initialize LLM based on provider
print("\n" + "="*60)
print("LLM Configuration")
print("="*60)

if LLM_PROVIDER == 'ollama':
    print(f"[OK] Using Ollama LLM (local, recommended)")
    print(f"   Base URL: {OLLAMA_BASE_URL}")
    print(f"   Model: {OLLAMA_MODEL}")
    print(f"   Note: No API key needed for Ollama (local)")
    
elif LLM_PROVIDER == 'openai':
    if not OPENAI_API_KEY:
        print("[ERROR] OpenAI API key not found in .env file!")
        print("   Set OPENAI_API_KEY=your_key in .env")
    else:
        print(f"[OK] Using OpenAI LLM")
        print(f"   API Key: {OPENAI_API_KEY[:10]}...{OPENAI_API_KEY[-4:]}")
        
elif LLM_PROVIDER == 'groq':
    if not GROQ_API_KEY:
        print("[ERROR] Groq API key not found in .env file!")
        print("   Set GROQ_API_KEY=your_key in .env")
    else:
        print(f"[OK] Using Groq LLM")
        print(f"   API Key: {GROQ_API_KEY[:10]}...{GROQ_API_KEY[-4:]}")
    
else:
    print(f"[ERROR] Unknown LLM_PROVIDER: {LLM_PROVIDER}")
    print("   Valid options: ollama (recommended), openai, groq")
    
print("="*60 + "\n")

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def remove_duplicate_stories(stories):
    """Remove duplicate or very similar user stories"""
    if not stories:
        return stories
    
    unique_stories = []
    seen_texts = set()
    
    for story in stories:
        story_text = story.get('User Story', '').strip().lower()
        
        # Skip empty stories
        if not story_text:
            print(f"Skipping empty story")
            continue
        
        # Check for exact duplicates
        if story_text in seen_texts:
            print(f"Skipping duplicate story: {story_text[:50]}...")
            continue
        
        # Check for similar stories (word overlap similarity)
        is_duplicate = False
        for seen_text in seen_texts:
            # Calculate word overlap similarity
            words1 = set(story_text.split())
            words2 = set(seen_text.split())
            
            if len(words1) > 0 and len(words2) > 0:
                # Intersection of words
                overlap = len(words1.intersection(words2))
                # Use Jaccard similarity (intersection / union)
                union = len(words1.union(words2))
                jaccard_similarity = overlap / union if union > 0 else 0
                
                # If more than 60% word overlap, consider it duplicate (more aggressive)
                if jaccard_similarity > 0.6:
                    print(f"Skipping similar story (Jaccard similarity: {jaccard_similarity:.2f})")
                    print(f"  New: {story_text[:60]}...")
                    print(f"  Existing: {seen_text[:60]}...")
                    is_duplicate = True
                    break
        
        if not is_duplicate:
            unique_stories.append(story)
            seen_texts.add(story_text)
            print(f"Added story: {story_text[:60]}...")
    
    removed_count = len(stories) - len(unique_stories)
    print(f"\nDeduplication summary: Kept {len(unique_stories)} unique stories, removed {removed_count} duplicates")
    return unique_stories

def convert_stories_to_frontend_format(epics_json, test_cases_json, requirements_text):
    """
    Convert backend output format to frontend format
    Backend returns: { "User Stories": [...], "Test Cases": {...} }
    Frontend expects: [{ title, description, definitionOfDone, testCases }]
    """
    try:
        # Safe JSON parsing with fallbacks
        if isinstance(epics_json, str):
            try:
                epics_data = json.loads(epics_json)
            except json.JSONDecodeError:
                print(f"Error parsing epics_json, trying to clean...")
                # Try cleaning
                cleaned = epics_json.replace("```json", "").replace("```", "").strip()
                start = cleaned.find('{')
                end = cleaned.rfind('}')
                if start != -1 and end != -1:
                    cleaned = cleaned[start:end+1]
                try:
                    epics_data = json.loads(cleaned)
                except:
                    epics_data = {"User Stories": []}
        else:
            epics_data = epics_json
        
        if isinstance(test_cases_json, str):
            try:
                test_cases_data = json.loads(test_cases_json)
            except json.JSONDecodeError:
                print(f"Error parsing test_cases_json, trying to clean...")
                cleaned = test_cases_json.replace("```json", "").replace("```", "").strip()
                start = cleaned.find('{')
                end = cleaned.rfind('}')
                if start != -1 and end != -1:
                    cleaned = cleaned[start:end+1]
                try:
                    test_cases_data = json.loads(cleaned)
                except:
                    test_cases_data = {"Test Cases": {}}
        else:
            test_cases_data = test_cases_json
        
        # Try both "User Stories" and "Epics" keys (LLM might return either)
        user_stories = epics_data.get('User Stories', [])
        if not user_stories:
            # Try "Epics" key as fallback
            epics_list = epics_data.get('Epics', [])
            if epics_list:
                print(f"DEBUG: Found 'Epics' key instead of 'User Stories', converting...")
                user_stories = epics_list
        
        # Handle different test cases formats
        # Format 1: {"Test Cases": {...}} - dictionary with keys
        # Format 2: {"testCases": [...]} - array of test case objects
        test_cases_dict = test_cases_data.get('Test Cases', {})
        test_cases_list = test_cases_data.get('testCases', [])
        
        # Debug: Print what we got
        print(f"DEBUG: epics_data keys: {list(epics_data.keys())}")
        print(f"DEBUG: user_stories count BEFORE deduplication: {len(user_stories)}")
        print(f"DEBUG: user_stories sample: {user_stories[:2] if user_stories else 'EMPTY'}")
        print(f"DEBUG: test_cases_data keys: {list(test_cases_data.keys())}")
        print(f"DEBUG: test_cases_dict type: {type(test_cases_dict)}, length: {len(test_cases_dict) if isinstance(test_cases_dict, dict) else 'N/A'}")
        print(f"DEBUG: test_cases_list type: {type(test_cases_list)}, length: {len(test_cases_list) if isinstance(test_cases_list, list) else 'N/A'}")
        
        # Remove duplicate stories based on similarity
        user_stories = remove_duplicate_stories(user_stories)
        
        print(f"DEBUG: user_stories count AFTER deduplication: {len(user_stories)}")
        
        frontend_stories = []
        
        for idx, story in enumerate(user_stories):
            # Extract user story title/description
            story_text = story.get('User Story', '').strip()
            
            # Generate a COMPLETE, meaningful title (3-5 words)
            if story_text:
                # Check if story follows "The system must [action] so that [benefit]" pattern
                if ' so that ' in story_text.lower():
                    # Extract action part (before "so that")
                    action_part = story_text.split(' so that ')[0].strip()
                    # Remove common prefixes
                    action_part = action_part.replace('The system must ', '').replace('The system shall ', '').replace('Users can ', '').replace('The ', '').strip()
                    
                    # Extract meaningful action words (skip stop words but keep important verbs)
                    words = action_part.split()
                    meaningful_words = []
                    stop_words = {'and', 'the', 'for', 'with', 'from', 'to', 'a', 'an', 'in', 'on', 'at', 'by'}
                    
                    for w in words:
                        w_clean = w.rstrip(',;.').lower()
                        # Keep verbs and important words, skip stop words
                        if w_clean not in stop_words or w_clean in {'shall', 'must', 'can', 'will'}:
                            meaningful_words.append(w.rstrip(',;.'))
                        # Take 4-5 words for a complete title
                        if len(meaningful_words) >= 5:
                            break
                    
                    # If we have meaningful words, use them; otherwise use first 4 words
                    if meaningful_words:
                        title = ' '.join(meaningful_words[:5])
                    else:
                        title = ' '.join(words[:4])
                    
                    # Capitalize first letter of each word for title case
                    title = ' '.join(word.capitalize() for word in title.split())
                else:
                    # Fallback: extract first 4-5 meaningful words
                    words = story_text.split()
                    meaningful_words = []
                    stop_words = {'the', 'system', 'must', 'shall', 'can', 'will', 'and', 'for', 'with'}
                    for w in words:
                        w_clean = w.rstrip(',;.').lower()
                        if w_clean not in stop_words:
                            meaningful_words.append(w.rstrip(',;.'))
                        if len(meaningful_words) >= 5:
                            break
                    title = ' '.join(meaningful_words) if meaningful_words else ' '.join(words[:4])
                    title = ' '.join(word.capitalize() for word in title.split())
            else:
                title = f'User Story {idx + 1}'
            
            # Extract deliverables and format properly
            deliverables = story.get('Deliverables', {})
            deliverable_items = []
            
            if deliverables and isinstance(deliverables, dict):
                # Remove "User Story" key if it exists (it's redundant)
                deliverables_filtered = {k: v for k, v in deliverables.items() if k != 'User Story'}
                
                for key, value in deliverables_filtered.items():
                    # Format key name (convert snake_case to Title Case)
                    formatted_key = key.replace('_', ' ').title()
                    
                    if isinstance(value, dict):
                        # Try multiple fields for definition of done
                        dod = (value.get('definition_of_done') or 
                               value.get('definitionOfDone') or 
                               value.get('description') or 
                               value.get('criteria') or
                               str(value))
                        # Skip if it's just "TBD" or empty
                        if dod and dod.strip() and dod.strip().upper() != 'TBD':
                            deliverable_items.append(f"• {formatted_key}: {dod}")
                    else:
                        # Skip if value is "TBD" or empty
                        value_str = str(value).strip()
                        if value_str and value_str.upper() != 'TBD':
                            deliverable_items.append(f"• {formatted_key}: {value_str}")
            
            # If no deliverables found, try to infer from story text
            if not deliverable_items:
                # Extract key functionality from story text as a fallback
                if story_text:
                    # Try to identify the main feature/component
                    action_part = story_text.split(' so that ')[0] if ' so that ' in story_text.lower() else story_text
                    # Remove common prefixes
                    action_part = action_part.replace('The system must ', '').replace('The system shall ', '').replace('The ', '').strip()
                    # Create a basic deliverable from the action
                    if action_part:
                        deliverable_items.append(f"• Feature Implementation: {action_part}")
            
            definition_of_done = '\n'.join(deliverable_items) if deliverable_items else 'Deliverables will be defined during sprint planning'
            
            # Get test cases for this story
            # Try multiple matching strategies
            test_cases = None
            
            # Strategy 1: Match by requirement ID (try multiple field name variations)
            if isinstance(test_cases_list, list) and len(test_cases_list) > 0:
                matching_tests = []
                for test_case in test_cases_list:
                    if isinstance(test_case, dict):
                        # Try different field name variations (camelCase and snake_case)
                        req_id = (test_case.get('requirementId') or 
                                 test_case.get('requirementID') or 
                                 test_case.get('requirement_id') or 
                                 test_case.get('req_id'))
                        
                        # Match by index (1-based) - STRICT matching
                        if req_id and req_id == idx + 1:
                            matching_tests.append(test_case)
                        # Also try matching by story text keywords
                        elif story_text:
                            test_case_text = str(test_case).lower()
                            story_keywords = [w for w in story_text.lower().split() if len(w) > 4]
                            if any(kw in test_case_text for kw in story_keywords[:3]):
                                matching_tests.append(test_case)
                
                if matching_tests:
                    # Format test cases nicely
                    formatted_tests = []
                    for test in matching_tests:
                        test_name = test.get('name') or test.get('testCaseName') or test.get('test_case_name') or 'Test Case'
                        test_desc = test.get('description') or test.get('testDescription') or ''
                        formatted_tests.append(f"{test_name}: {test_desc}")
                    test_cases = '\n'.join(formatted_tests) if formatted_tests else json.dumps(matching_tests, indent=2)
                    print(f"DEBUG: Found {len(matching_tests)} test cases for story {idx + 1}")
            
            # Strategy 2: Try dictionary lookup by index
            if not test_cases and test_cases_dict:
                test_cases = test_cases_dict.get(str(idx + 1), '')
                if not test_cases:
                    # Try to find by story text
                    for key, value in test_cases_dict.items():
                        if story_text.lower() in str(value).lower() or str(value).lower() in story_text.lower():
                            test_cases = value
                            break
            
            # Strategy 3: If still no match, create a basic test case from story
            if not test_cases or test_cases == '-':
                # Generate a basic test case from the story text
                if story_text:
                    action_part = story_text.split(' so that ')[0] if ' so that ' in story_text.lower() else story_text
                    test_cases = f"Test: Verify that {action_part.lower()}\nExpected: Functionality works as specified in the user story"
                else:
                    test_cases = 'Test cases will be defined during test planning'
            
            # Convert to string if needed
            if isinstance(test_cases, dict):
                test_cases = json.dumps(test_cases, indent=2)
            elif not isinstance(test_cases, str):
                test_cases = str(test_cases)
            
            frontend_stories.append({
                'id': idx + 1,
                'title': title,
                'description': story_text,  # Full user story text
                'definitionOfDone': definition_of_done,  # Formatted deliverables
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
        'provider': LLM_PROVIDER,
        'api_key_configured': bool(OPENAI_API_KEY if LLM_PROVIDER == 'openai' else GROQ_API_KEY if LLM_PROVIDER == 'groq' else True),
        'ollama_url': OLLAMA_BASE_URL if LLM_PROVIDER == 'ollama' else None,
        'model': OLLAMA_MODEL if LLM_PROVIDER == 'ollama' else 'llama-3.3-70b-versatile' if LLM_PROVIDER == 'groq' else 'gpt-4o'
    })

@app.route('/api/generate-stories', methods=['POST'])
def generate_stories():
    """Generate user stories from uploaded document"""
    print("\n" + "="*60)
    print("API CALL RECEIVED: /api/generate-stories")
    print("="*60)
    print(f"LLM_PROVIDER from env: {LLM_PROVIDER}")
    if LLM_PROVIDER == 'ollama':
        print(f"OLLAMA_BASE_URL: {OLLAMA_BASE_URL}")
        print(f"OLLAMA_MODEL: {OLLAMA_MODEL}")
    elif LLM_PROVIDER == 'groq':
        print(f"GROQ_API_KEY exists: {bool(GROQ_API_KEY)}")
        print(f"GROQ_API_KEY length: {len(GROQ_API_KEY) if GROQ_API_KEY else 0}")
    elif LLM_PROVIDER == 'openai':
        print(f"OPENAI_API_KEY exists: {bool(OPENAI_API_KEY)}")
    
    try:
        # Check if file is present
        if 'file' not in request.files:
            print("[ERROR] No file in request")
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        print(f"[OK] File received: {file.filename}")
        
        if file.filename == '':
            print("[ERROR] Empty filename")
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            print(f"[ERROR] File type not allowed: {file.filename}")
            return jsonify({'error': 'File type not allowed. Please upload .docx, .doc, .txt, or .md files'}), 400

        # Validate API key based on provider
        print(f"[DEBUG] Checking provider: {LLM_PROVIDER}")
        if LLM_PROVIDER == 'ollama':
            print("[OK] Ollama - no API key needed (local)")
        elif LLM_PROVIDER == 'openai' and not OPENAI_API_KEY:
            print("[ERROR] OpenAI API key missing")
            return jsonify({'error': 'OpenAI API key not configured. Set OPENAI_API_KEY in .env'}), 500
        elif LLM_PROVIDER == 'groq' and not GROQ_API_KEY:
            print("[ERROR] Groq API key missing")
            return jsonify({'error': 'Groq API key not configured. Set GROQ_API_KEY in .env'}), 500
        
        print(f"[OK] API key validation passed for {LLM_PROVIDER}")

        # Save uploaded file temporarily
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        try:
            # Initialize LLM model based on configured provider
            temp = 0.3
            chat = None
            
            if LLM_PROVIDER == 'ollama':
                # Use Ollama (free, local, recommended)
                model_name = request.form.get('model', OLLAMA_MODEL)
                print(f"\n[Ollama] ===== INITIALIZING OLLAMA LLM =====")
                print(f"[Ollama] Model: {model_name}")
                print(f"[Ollama] Base URL: {OLLAMA_BASE_URL}")
                print(f"[Ollama] Temperature: {temp}")
                chat = ChatOllama(
                    model=model_name,
                    temperature=temp,
                    base_url=OLLAMA_BASE_URL
                )
                print(f"[Ollama] ✓ ChatOllama instance created successfully!")
                print(f"[Ollama] ====================================\n")
                
            elif LLM_PROVIDER == 'openai':
                # Use OpenAI (cloud, requires API key)
                if not OPENAI_API_KEY:
                    return jsonify({'error': 'OpenAI API key not configured. Set OPENAI_API_KEY in .env'}), 500
                model = request.form.get('model', 'gpt-4o')
                print(f"[OpenAI] Initializing OpenAI LLM: {model}")
                print(f"   API Key: {OPENAI_API_KEY[:10]}...{OPENAI_API_KEY[-4:]}")
                chat = ChatOpenAI(
                    model=model,
                    temperature=temp,
                    openai_api_key=OPENAI_API_KEY
                )
                
            elif LLM_PROVIDER == 'groq':
                # Use Groq (fast, free, cloud)
                print(f"\n[Groq] ===== INITIALIZING GROQ LLM =====")
                print(f"[Groq] API Key present: {bool(GROQ_API_KEY)}")
                print(f"[Groq] API Key preview: {GROQ_API_KEY[:15]}...{GROQ_API_KEY[-5:] if GROQ_API_KEY else 'NONE'}")
                
                if not GROQ_API_KEY:
                    print("[Groq] ERROR: API key missing!")
                    return jsonify({'error': 'Groq API key not configured. Set GROQ_API_KEY in .env'}), 500
                
                print(f"[Groq] Creating ChatGroq instance...")
                print(f"[Groq] Model: llama-3.3-70b-versatile")
                print(f"[Groq] Temperature: {temp}")
                
                chat = ChatGroq(
                    model="llama-3.3-70b-versatile",  # Latest supported Groq model (llama-3.1-70b-versatile and mixtral-8x7b-32768 are deprecated)
                    temperature=temp,
                    api_key=GROQ_API_KEY
                )
                print(f"[Groq] ✓ ChatGroq instance created successfully!")
                print(f"[Groq] ====================================\n")
            else:
                return jsonify({'error': f'Unknown LLM_PROVIDER: {LLM_PROVIDER}'}), 500
            
            if chat is None:
                return jsonify({'error': 'Failed to initialize LLM'}), 500
            
            # Extract text from document
            if filename.endswith('.docx') or filename.endswith('.doc'):
                extracted_text = extract_text_from_docx(filepath)
            else:
                # For txt/md files, read directly
                with open(filepath, 'r', encoding='utf-8') as f:
                    extracted_text = f.read()
            
            # Process document using autoAgile
            mode = "prod"
            print(f"Processing document: {filename}")
            print(f"Extracted text length: {len(extracted_text)} characters")
            
            try:
                print("\n" + "="*60)
                print("STEP 1: Extracting requirements...")
                print("="*60)
                print(f"[DEBUG] About to call LLM (chat type: {type(chat).__name__})")
                print(f"[DEBUG] This will make the FIRST LLM API call!")
                
                try:
                    print(f"[DEBUG] Calling rat() with chat type: {type(chat).__name__}")
                    print(f"[DEBUG] Extracted text length: {len(extracted_text)} characters")
                    requirements = rat(refine_doc, extract_functionarity, extracted_text, chat, mode)
                except Exception as llm_error:
                    import traceback
                    error_trace = traceback.format_exc()
                    print(f"[ERROR] LLM call failed: {llm_error}")
                    print(f"[ERROR] Error type: {type(llm_error).__name__}")
                    print(f"[ERROR] Full traceback:\n{error_trace}")
                    # Check if it's an API key issue
                    error_str = str(llm_error).lower()
                    if 'api' in error_str and 'key' in error_str:
                        raise Exception(f"API key issue: {str(llm_error)}. Check your .env file and ensure {LLM_PROVIDER.upper()}_API_KEY is set correctly.")
                    elif 'connection' in error_str or 'timeout' in error_str:
                        raise Exception(f"Connection issue: {str(llm_error)}. Check your internet connection and LLM service availability.")
                    else:
                        raise Exception(f"LLM API call failed: {str(llm_error)}") from llm_error
                
                if requirements is None:
                    raise Exception("Requirements extraction returned None - LLM call may have failed. Check Flask console for detailed error messages.")
                
                if not isinstance(requirements, str):
                    requirements = str(requirements)
                
                print(f"[OK] Requirements extracted: {len(requirements)} characters")
                print(f"[OK] Requirements preview: {requirements[:200]}...")
                print(f"[OK] FIRST API CALL COMPLETED!\n")
                
                print("Step 2: Extracting epics...")
                deliverables = rat(refine_requirements, extract_epics, requirements, chat, mode)
                if deliverables is None:
                    raise Exception("Epics extraction returned None - LLM call may have failed")
                if not isinstance(deliverables, str):
                    deliverables = str(deliverables)
                print(f"Deliverables extracted: {len(deliverables)} characters")
                
                print("Step 3: Getting epics...")
                print(f"DEBUG: deliverables type: {type(deliverables)}, length: {len(str(deliverables))}")
                print(f"DEBUG: deliverables sample: {str(deliverables)[:500]}")
                epics = get_epics(deliverables, chat)
                if epics is None:
                    raise Exception("get_epics returned None")
                if not isinstance(epics, str):
                    epics = str(epics)
                print(f"DEBUG: epics type: {type(epics)}, length: {len(str(epics))}")
                print(f"DEBUG: epics sample: {str(epics)[:500]}")
                print(f"Epics extracted")
                
                print("Step 4: Generating test cases...")
                test_cases = rat(refine_requirements, generate_test_cases, requirements, chat, mode)
                if test_cases is None:
                    raise Exception("Test cases generation returned None - LLM call may have failed")
                if not isinstance(test_cases, str):
                    test_cases = str(test_cases)
                print(f"Test cases generated: {len(test_cases)} characters")
            except Exception as processing_error:
                import traceback
                error_trace = traceback.format_exc()
                print(f"Error during processing: {processing_error}")
                print(f"Traceback:\n{error_trace}")
                raise  # Re-raise to be caught by outer exception handler
            
            # VALIDATION: Check for invented metrics and other issues
            print(f"\n{'='*60}")
            print("VALIDATION: Checking output quality...")
            print(f"{'='*60}")
            
            # Validate epics output
            epics_validation = validate_output(epics, extracted_text)
            print_validation_report(epics_validation, "Epics/User Stories Validation")
            
            # Validate test cases output
            test_cases_validation = validate_output(test_cases, extracted_text)
            print_validation_report(test_cases_validation, "Test Cases Validation")
            
            # Validate completeness
            completeness_validation = validate_requirements_completeness(requirements, epics)
            print_validation_report(completeness_validation, "Completeness Validation")
            
            # Combine all issues
            all_issues = (
                epics_validation['issues'] + 
                test_cases_validation['issues'] + 
                completeness_validation['issues']
            )
            
            if all_issues:
                print(f"⚠️ WARNING: {len(all_issues)} validation issues found!")
                print("The output may contain invented metrics or other quality issues.")
                print("Review the issues above before using in production.\n")
            else:
                print("✅ VALIDATION PASSED: No issues detected!\n")
            
            # Convert to frontend format
            print(f"\n{'='*60}")
            print("DEBUG: About to convert to frontend format")
            print(f"{'='*60}")
            print(f"epics type: {type(epics)}")
            print(f"epics length: {len(str(epics))}")
            print(f"epics preview (first 1000 chars):\n{str(epics)[:1000]}")
            print(f"\ntest_cases type: {type(test_cases)}")
            print(f"test_cases length: {len(str(test_cases))}")
            print(f"{'='*60}\n")
            
            stories = convert_stories_to_frontend_format(epics, test_cases, requirements)
            print(f"\n{'='*60}")
            print(f"DEBUG: Converted stories count: {len(stories)}")
            print(f"{'='*60}\n")
            
            if len(stories) == 0:
                print("⚠️ WARNING: No stories generated!")
                print("This could mean:")
                print("  1. Epics JSON doesn't have 'User Stories' key")
                print("  2. Epics array is empty")
                print("  3. All stories were filtered as duplicates")
                print("  4. JSON parsing failed")
                print("\nCheck the epics preview above to see what was returned.")
            
            # Save output to JSON file
            output_file_path = None
            try:
                output_file_path = save_json_output(requirements, epics, test_cases, filepath)
                print(f"Output saved to: {output_file_path}")
            except Exception as save_error:
                print(f"Warning: Could not save JSON output: {save_error}")
                import traceback
                traceback.print_exc()
                # Continue even if saving fails
            
            return jsonify({
                'success': True,
                'stories': stories,
                'count': len(stories),
                'output_file': output_file_path
            })
            
        finally:
            # Clean up temporary file
            if os.path.exists(filepath):
                os.remove(filepath)
                
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"Error generating stories: {e}")
        print(f"Full traceback:\n{error_trace}")
        # Return detailed error for debugging
        return jsonify({
            'error': f'Error generating stories: {str(e)}',
            'details': error_trace.split('\n')[-5:] if len(error_trace) > 0 else []
        }), 500

@app.route('/api/integrate-story', methods=['POST'])
def integrate_story():
    """Integrate a single user story - save to json_output"""
    try:
        data = request.json
        story_id = data.get('storyId')
        story_data = data.get('story')  # Full story object from frontend
        
        if not story_data:
            return jsonify({'error': 'Story data not provided'}), 400
        
        # Save integrated story to json_output
        current_dir = os.path.dirname(os.path.abspath(__file__))
        output_dir = os.path.join(current_dir, "autoAgile", "json_output")
        
        if not os.path.exists(output_dir):
            os.makedirs(output_dir, mode=0o777, exist_ok=True)
        
        # Create filename for integrated story
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = os.path.join(output_dir, f"integrated_story_{story_id}_{timestamp}.json")
        
        # Save story as JSON
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({
                'story_id': story_id,
                'integrated_at': timestamp,
                'story': story_data
            }, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Integrated story {story_id} saved to: {output_file}")
        
        return jsonify({
            'success': True,
            'message': f'Story {story_id} integrated successfully',
            'storyId': story_id,
            'output_file': output_file
        })
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"Error integrating story: {e}\n{error_trace}")
        return jsonify({
            'error': f'Error integrating story: {str(e)}',
            'details': error_trace.split('\n')[-5:]
        }), 500

@app.route('/api/integrate-all', methods=['POST'])
def integrate_all():
    """Integrate all user stories - save to json_output"""
    try:
        data = request.json
        story_ids = data.get('storyIds', [])
        stories_data = data.get('stories', [])  # Full stories array from frontend
        
        if not stories_data:
            return jsonify({'error': 'Stories data not provided'}), 400
        
        # Save all integrated stories to json_output
        current_dir = os.path.dirname(os.path.abspath(__file__))
        output_dir = os.path.join(current_dir, "autoAgile", "json_output")
        
        if not os.path.exists(output_dir):
            os.makedirs(output_dir, mode=0o777, exist_ok=True)
        
        # Create filename for integrated stories
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = os.path.join(output_dir, f"integrated_all_stories_{timestamp}.json")
        
        # Save all stories as JSON
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({
                'integrated_at': timestamp,
                'total_stories': len(stories_data),
                'story_ids': story_ids,
                'stories': stories_data
            }, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Integrated {len(stories_data)} stories saved to: {output_file}")
        
        return jsonify({
            'success': True,
            'message': f'All {len(story_ids)} stories integrated successfully',
            'storyIds': story_ids,
            'output_file': output_file
        })
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"Error integrating all stories: {e}\n{error_trace}")
        return jsonify({
            'error': f'Error integrating stories: {str(e)}',
            'details': error_trace.split('\n')[-5:]
        }), 500

# Serve frontend pages
@app.route('/')
def index():
    """Serve the main index page"""
    return send_from_directory('pages', 'index.html')

@app.route('/stories.html')
def stories():
    """Serve the stories page"""
    return send_from_directory('pages', 'stories.html')

@app.route('/favicon.ico')
def favicon():
    """Handle favicon requests (suppress 404 errors)"""
    return '', 204  # No Content - suppresses browser favicon requests

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"\n{'='*60}")
    print(f"[STARTING] User Story Automation Server")
    print(f"{'='*60}")
    print(f"Frontend: http://localhost:{port}")
    print(f"API:      http://localhost:{port}/api")
    print(f"Health:   http://localhost:{port}/api/health")
    print(f"{'='*60}\n")
    app.run(host='0.0.0.0', port=port, debug=True)

