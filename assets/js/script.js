// Store selected file globally
let selectedFile = null;

// Handle file selection
function handleFileSelect(event) {
    const file = event.target.files[0];
    if (file) {
        const input = document.getElementById('projectDescription');
        input.value = file.name;
        
        // Store file for upload
        selectedFile = file;
        console.log('File selected:', file.name);
    }
}

// Generate User Stories - upload file and generate stories
async function generateUserStories() {
    const input = document.getElementById('projectDescription');
    const projectDescription = input.value;
    const generateButton = document.querySelector('.btn-primary');
    
    // Check if file is selected
    if (!selectedFile && !projectDescription) {
        alert('Please select a document file (.docx, .doc, .txt, or .md)');
        return;
    }
    
    // If no file selected but text entered, show error
    if (!selectedFile) {
        alert('Please use the Browse button to select a document file');
        return;
    }
    
    // Show loading state
    const originalButtonText = generateButton.textContent;
    generateButton.textContent = 'Generating...';
    generateButton.disabled = true;
    
    try {
        // Create FormData to send file
        const formData = new FormData();
        formData.append('file', selectedFile);
        
        console.log('📤 Uploading file to backend:', selectedFile.name);
        
        // Send file to backend API
        const response = await fetch('/api/generate-stories', {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({ error: 'Unknown error' }));
            throw new Error(errorData.error || `Server error: ${response.status}`);
        }
        
        const data = await response.json();
        console.log('✅ Received response from backend:', data);
        
        if (data.success && data.stories && Array.isArray(data.stories)) {
            console.log(`📝 Generated ${data.stories.length} user stories`);
            
            // Store stories in sessionStorage
            sessionStorage.setItem('userStories', JSON.stringify(data.stories));
            sessionStorage.setItem('projectDescription', projectDescription || selectedFile.name);
            
            // Navigate to stories page
            window.location.href = 'stories.html';
        } else {
            throw new Error('Invalid response format from server. Expected stories array.');
        }
        
    } catch (error) {
        console.error('❌ Error generating stories:', error);
        alert('Error generating user stories:\n\n' + error.message + '\n\nPlease check:\n1. Backend is running (npm run start:backend)\n2. File format is supported (.docx, .doc, .txt, .md)\n3. OpenAI API key is set in .env file');
        
        // Restore button state
        generateButton.textContent = originalButtonText;
        generateButton.disabled = false;
    }
}

// Global array to store user stories (will be populated from backend API)
let userStories = [];

// Load user stories from sessionStorage (set after API call)
function loadUserStories() {
    // Get stories from sessionStorage (set by generateUserStories after API call)
    const storedStories = sessionStorage.getItem('userStories');
    
    console.log('🔍 Loading user stories...');
    console.log('SessionStorage has userStories:', !!storedStories);
    
    if (storedStories) {
        try {
            userStories = JSON.parse(storedStories);
            console.log('✅ Loaded', userStories.length, 'user stories from sessionStorage');
            console.log('First story:', userStories[0]);
        } catch (e) {
            console.error('❌ Error parsing stored stories:', e);
            userStories = [];
        }
    } else {
        console.warn('⚠️ No user stories in sessionStorage');
        console.log('💡 To generate stories:');
        console.log('   1. Go to index.html');
        console.log('   2. Click "Browse" and select a document');
        console.log('   3. Click "Generate User Stories"');
    }
    
    // If no stories found, show message
    if (userStories.length === 0) {
        console.warn('No user stories found. Please generate stories first.');
        // Redirect to index page if no stories
        const currentPath = window.location.pathname;
        if (currentPath.includes('stories.html')) {
            console.log('💡 Redirecting to index page to generate stories...');
            // Don't auto-redirect, just show message
        }
    }
    
    renderStoryList();
    
    // Select first story by default if available
    if (userStories.length > 0) {
        selectStory(0);
    }
}

// Placeholder function removed - using real backend data only

// Render the story list dynamically
function renderStoryList() {
    const storyList = document.getElementById('storyList');
    // Clear existing items safely
    while (storyList.firstChild) {
        storyList.removeChild(storyList.firstChild);
    }
    
    if (userStories.length === 0) {
        const noStoriesItem = document.createElement('li');
        noStoriesItem.className = 'no-stories';
        noStoriesItem.textContent = 'No user stories available';
        storyList.appendChild(noStoriesItem);
        
        // Show helpful message
        const noStoriesMsg = document.getElementById('noStoriesMessage');
        if (noStoriesMsg) {
            noStoriesMsg.style.display = 'block';
        }
        return;
    }
    
    // Hide no stories message if stories exist
    const noStoriesMsg = document.getElementById('noStoriesMessage');
    if (noStoriesMsg) {
        noStoriesMsg.style.display = 'none';
    }
    
    userStories.forEach((story, index) => {
        const listItem = document.createElement('li');
        listItem.className = 'story-item';
        listItem.setAttribute('data-story-index', index);
        listItem.textContent = `User story ${index + 1}`;
        listItem.onclick = () => selectStory(index);
        storyList.appendChild(listItem);
    });
}

// Select a story from the list by index
function selectStory(storyIndex) {
    // Validate index
    if (storyIndex < 0 || storyIndex >= userStories.length) {
        console.error('Invalid story index:', storyIndex);
        return;
    }
    
    // Remove active class from all items
    const items = document.querySelectorAll('.story-item');
    items.forEach(item => item.classList.remove('active'));
    
    // Add active class to selected item
    const selectedItem = document.querySelector(`[data-story-index="${storyIndex}"]`);
    if (selectedItem) {
        selectedItem.classList.add('active');
    }
    
    // Update story details
    updateStoryDetails(storyIndex);
}

// Update story details in the content panel
function updateStoryDetails(storyIndex) {
    const story = userStories[storyIndex];
    
    if (!story) {
        console.error('Story not found at index:', storyIndex);
        return;
    }
    
    document.getElementById('storyTitle').textContent = story.title || '-';
    document.getElementById('storyDescription').textContent = story.description || '-';
    document.getElementById('storyDoD').textContent = story.definitionOfDone || '-';
    document.getElementById('storyTestCases').textContent = story.testCases || '-';
}

// Integrate a single story
async function integrateStory() {
    const activeItem = document.querySelector('.story-item.active');
    if (activeItem) {
        const storyIndex = parseInt(activeItem.getAttribute('data-story-index'));
        const story = userStories[storyIndex];
        
        if (story) {
            try {
                const response = await fetch('/api/integrate-story', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ storyId: story.id || storyIndex })
                });
                
                const data = await response.json();
                if (data.success) {
                    alert(`User Story ${storyIndex + 1} integrated successfully!`);
                } else {
                    throw new Error(data.error || 'Integration failed');
                }
            } catch (error) {
                console.error('Error integrating story:', error);
                alert('Error integrating user story: ' + error.message);
            }
        }
    } else {
        alert('Please select a user story to integrate.');
    }
}

// Integrate all stories
async function integrateAll() {
    if (userStories.length === 0) {
        alert('No user stories available to integrate.');
        return;
    }
    
    try {
        const response = await fetch('/api/integrate-all', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ storyIds: userStories.map(s => s.id) })
        });
        
        const data = await response.json();
        if (data.success) {
            alert(`All ${userStories.length} user stories integrated successfully!`);
        } else {
            throw new Error(data.error || 'Integration failed');
        }
    } catch (error) {
        console.error('Error integrating stories:', error);
        alert('Error integrating user stories: ' + error.message);
    }
}

// Initialize stories page
if (window.location.pathname.includes('stories.html')) {
    // Load and render user stories when page loads
    loadUserStories();
}

// Function to update stories from backend (call this when Python code generates stories)
function updateUserStories(stories) {
    userStories = stories;
    sessionStorage.setItem('userStories', JSON.stringify(stories));
    renderStoryList();
    
    // Select first story by default
    if (userStories.length > 0) {
        selectStory(0);
    }
}

