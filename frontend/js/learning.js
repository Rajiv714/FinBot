// Backend API URL - automatically detects the correct host
const BACKEND_URL = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
    ? 'http://localhost:8000' 
    : `http://${window.location.hostname}:8000`;

let currentHandoutContent = '';

// Select topic
function selectTopic(topic) {
    document.getElementById('topicInput').value = topic;
}

// Generate handout
async function generateHandout() {
    const topicInput = document.getElementById('topicInput');
    const wordCount = document.getElementById('wordCount').value;
    const includeGoogle = document.getElementById('includeGoogle').checked;
    const loadingIndicator = document.getElementById('loadingIndicator');
    const resultSection = document.getElementById('handoutResult');
    const progressBar = document.getElementById('progressBar');
    
    // Get selected language
    const langSelect = document.getElementById('languageSelect');
    const selectedLang = langSelect ? langSelect.value : 'en';
    
    let topic = topicInput.value.trim();
    
    if (!topic) {
        alert('Please enter a financial topic');
        return;
    }
    
    // Add language instruction if not English
    if (selectedLang !== 'en') {
        const languageNames = {
            'hi': 'Hindi (हिंदी)',
            'bn': 'Bengali (বাংলা)',
            'te': 'Telugu (తెలుగు)',
            'mr': 'Marathi (मराठी)',
            'ta': 'Tamil (தமிழ்)',
            'gu': 'Gujarati (ગુજરાતી)',
            'kn': 'Kannada (ಕನ್ನಡ)',
            'ml': 'Malayalam (മലയാളം)',
            'pa': 'Punjabi (ਪੰਜਾਬੀ)'
        };
        const languageName = languageNames[selectedLang] || selectedLang;
        topic = `[Generate handout in ${languageName} language] ${topic}`;
    }
    
    // Show loading
    loadingIndicator.classList.remove('hidden');
    resultSection.classList.add('hidden');
    
    // Animate progress bar
    let progress = 0;
    const progressInterval = setInterval(() => {
        progress += 2;
        if (progress <= 90) {
            progressBar.style.width = progress + '%';
        }
    }, 300);
    
    try {
        const response = await fetch(`${BACKEND_URL}/api/handouts`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                topic: topic,
                target_length: parseInt(wordCount),
                include_google_search: includeGoogle,
                search_depth: 'standard'
            })
        });
        
        clearInterval(progressInterval);
        progressBar.style.width = '100%';
        
        if (!response.ok) {
            throw new Error('API request failed');
        }
        
        const data = await response.json();
        
        if (data.success && data.handout_content) {
            currentHandoutContent = data.handout_content;
            displayHandout(data.handout_content, topic);
        } else {
            throw new Error(data.error || 'Failed to generate handout');
        }
        
    } catch (error) {
        clearInterval(progressInterval);
        loadingIndicator.classList.add('hidden');
        alert('Error: ' + error.message + '\n\nPlease make sure the backend server is running.');
        console.error('Error:', error);
    }
}

// Display handout
function displayHandout(content, topic) {
    const loadingIndicator = document.getElementById('loadingIndicator');
    const resultSection = document.getElementById('handoutResult');
    const handoutContent = document.getElementById('handoutContent');
    const downloadBtn = document.getElementById('downloadBtn');
    
    // Hide loading
    loadingIndicator.classList.add('hidden');
    
    // Convert markdown to HTML
    if (typeof marked !== 'undefined') {
        handoutContent.innerHTML = marked.parse(content);
    } else {
        // Fallback if marked.js is not available
        handoutContent.innerHTML = '<pre class="whitespace-pre-wrap">' + escapeHtml(content) + '</pre>';
    }
    
    // Show result
    resultSection.classList.remove('hidden');
    
    // Setup download button
    downloadBtn.onclick = function() {
        downloadHandout(content, topic);
    };
    
    // Scroll to result
    resultSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

// Download handout
function downloadHandout(content, topic) {
    const blob = new Blob([content], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${topic.replace(/\s+/g, '_')}_handout.md`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

// Escape HTML
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Initialize
document.addEventListener('DOMContentLoaded', function() {
    const topicInput = document.getElementById('topicInput');
    if (topicInput) {
        topicInput.focus();
    }
});
