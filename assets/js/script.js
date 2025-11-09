// Handle file selection
function handleFileSelect(event) {
    const file = event.target.files[0];
    if (file) {
        const input = document.getElementById('projectDescription');
        input.value = file.name;
        
        // Store file for later use
        // In a real application, you might want to read the file content here
        console.log('File selected:', file.name);
    }
}

// Generate User Stories - navigate to stories page
function generateUserStories() {
    const input = document.getElementById('projectDescription');
    const projectDescription = input.value;
    
    if (!projectDescription) {
        alert('Please select or enter a project description');
        return;
    }
    
    // Store project description in sessionStorage for later use
    sessionStorage.setItem('projectDescription', projectDescription);
    
    // TODO: When backend is ready, send project description to API:
    // fetch('/api/generate-stories', {
    //     method: 'POST',
    //     headers: { 'Content-Type': 'application/json' },
    //     body: JSON.stringify({ projectDescription: projectDescription })
    // })
    // .then(response => response.json())
    // .then(stories => {
    //     updateUserStories(stories);
    //     window.location.href = 'stories.html';
    // })
    // .catch(error => {
    //     console.error('Error generating stories:', error);
    //     alert('Error generating user stories. Please try again.');
    // });
    
    // For now, just navigate to stories page
    window.location.href = 'stories.html';
}

// Global array to store user stories (will be populated from backend API)
let userStories = [];

// Load user stories from backend API or sessionStorage
async function loadUserStories() {
    // Check if stories are in sessionStorage (for demo purposes)
    const storedStories = sessionStorage.getItem('userStories');
    
    if (storedStories) {
        try {
            userStories = JSON.parse(storedStories);
        } catch (e) {
            console.error('Error parsing stored stories:', e);
            userStories = [];
        }
    }
    
    // TODO: When backend is ready, replace this with actual API call:
    // try {
    //     const response = await fetch('/api/user-stories', {
    //         method: 'GET',
    //         headers: { 'Content-Type': 'application/json' }
    //     });
    //     userStories = await response.json();
    // } catch (error) {
    //     console.error('Error fetching user stories:', error);
    //     userStories = [];
    // }
    
    // If no stories loaded, use placeholder data for demo
    if (userStories.length === 0) {
        userStories = getPlaceholderStories();
    }
    
    renderStoryList();
    
    // Select first story by default if available
    if (userStories.length > 0) {
        selectStory(0);
    }
}

// Get placeholder stories for demo (remove when backend is connected)
function getPlaceholderStories() {
    return [
        {
            id: 1,
            title: 'adipisicing elit, sed do eiusmod tempor.',
            description: 'Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in.',
            definitionOfDone: 'Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in.',
            testCases: 'Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in.'
        },
        {
            id: 2,
            title: 'User Story 2 Title',
            description: 'Description for user story 2. Lorem ipsum dolor sit amet, consectetur adipisicing elit.',
            definitionOfDone: 'Definition of done for user story 2.',
            testCases: 'Test cases for user story 2.'
        },
        {
            id: 3,
            title: 'User Story 3 Title',
            description: 'Description for user story 3. Lorem ipsum dolor sit amet, consectetur adipisicing elit.',
            definitionOfDone: 'Definition of done for user story 3.',
            testCases: 'Test cases for user story 3.'
        },
        {
            id: 4,
            title: 'User Story 4 Title',
            description: 'Description for user story 4. Lorem ipsum dolor sit amet, consectetur adipisicing elit.',
            definitionOfDone: 'Definition of done for user story 4.',
            testCases: 'Test cases for user story 4.'
        }
    ];
}

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
        return;
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
function integrateStory() {
    const activeItem = document.querySelector('.story-item.active');
    if (activeItem) {
        const storyIndex = parseInt(activeItem.getAttribute('data-story-index'));
        const story = userStories[storyIndex];
        
        if (story) {
            alert(`Integrating User Story ${storyIndex + 1}...\n\nIn a real application, this would send a request to the backend API.`);
            // TODO: When backend is ready, replace with actual API call:
            // fetch('/api/integrate-story', {
            //     method: 'POST',
            //     headers: { 'Content-Type': 'application/json' },
            //     body: JSON.stringify({ storyId: story.id || storyIndex })
            // })
        }
    } else {
        alert('Please select a user story to integrate.');
    }
}

// Integrate all stories
function integrateAll() {
    if (userStories.length === 0) {
        alert('No user stories available to integrate.');
        return;
    }
    
    alert(`Integrating all ${userStories.length} user stories...\n\nIn a real application, this would send a request to the backend API.`);
    // TODO: When backend is ready, replace with actual API call:
    // fetch('/api/integrate-all', {
    //     method: 'POST',
    //     headers: { 'Content-Type': 'application/json' },
    //     body: JSON.stringify({ storyIds: userStories.map(s => s.id) })
    // })
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

