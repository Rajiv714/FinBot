// Backend API URL - automatically detects the correct host
const BACKEND_URL = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
    ? 'http://localhost:8000' 
    : `http://${window.location.hostname}:8000`;

// Chat history
let chatHistory = [];
let currentQuery = '';
let selectedLanguage = 'en'; // Default language

// Language change handler
function changeLanguage() {
    const languageSelect = document.getElementById('languageSelect');
    if (languageSelect) {
        selectedLanguage = languageSelect.value;
        console.log('Language changed to:', selectedLanguage);
    }
}

// Send message function
async function sendMessage(message) {
    const input = document.getElementById('chatInput');
    const messagesContainer = document.getElementById('chatMessages');
    
    // Get message from input or parameter
    const userMessage = message || input.value.trim();
    if (!userMessage) return;
    
    // Clear input
    if (input) input.value = '';
    
    // Add user message to chat
    addUserMessage(userMessage);
    
    // Show typing indicator
    const typingId = showTypingIndicator();
    
    try {
        // Get selected language
        const langSelect = document.getElementById('languageSelect');
        const selectedLang = langSelect ? langSelect.value : 'en';
        
        // Build query with language instruction if not English
        let queryToSend = userMessage;
        if (selectedLang !== 'en') {
            const languageNames = {
                'hi': 'Hindi',
                'bn': 'Bengali',
                'te': 'Telugu',
                'mr': 'Marathi',
                'ta': 'Tamil',
                'gu': 'Gujarati',
                'kn': 'Kannada',
                'ml': 'Malayalam',
                'pa': 'Punjabi'
            };
            const languageName = languageNames[selectedLang] || selectedLang;
            // More natural language instruction that's less likely to trigger safety filters
            queryToSend = `${userMessage}\n\n(Please provide your response in ${languageName})`;
        }
        
        // Call API
        const response = await fetch(`${BACKEND_URL}/api/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                query: queryToSend,
                include_context: true
            })
        });
        
        if (!response.ok) {
            throw new Error('API request failed');
        }
        
        const data = await response.json();
        
        // Remove typing indicator
        removeTypingIndicator(typingId);
        
        // Add bot response
        addBotMessage(data.answer || 'No response received');
        
        // Store current query for integrations
        currentQuery = userMessage;
        
        // Load integrations
        loadVideos(userMessage);
        loadNews(userMessage);
        
        // Sources removed - not displayed
        // if (data.sources && data.sources.length > 0) {
        //     addSourcesMessage(data.sources);
        // }
        
    } catch (error) {
        removeTypingIndicator(typingId);
        addBotMessage('❌ Sorry, I encountered an error. Please make sure the backend server is running.');
        console.error('Error:', error);
    }
}

// Add user message to chat
function addUserMessage(message) {
    const messagesContainer = document.getElementById('chatMessages');
    const messageDiv = document.createElement('div');
    messageDiv.className = 'flex justify-end message';
    messageDiv.innerHTML = `
        <div class="max-w-[70%] gradient-bg text-white px-6 py-4 rounded-3xl rounded-tr-md shadow-lg">
            <p class="leading-relaxed">${escapeHtml(message)}</p>
        </div>
    `;
    messagesContainer.appendChild(messageDiv);
    scrollToBottom();
    chatHistory.push({ role: 'user', content: message });
}

// Add bot message to chat
function addBotMessage(message) {
    const messagesContainer = document.getElementById('chatMessages');
    const messageDiv = document.createElement('div');
    messageDiv.className = 'flex justify-start message';
    messageDiv.innerHTML = `
        <div class="max-w-[70%] bg-white px-6 py-4 rounded-3xl rounded-tl-md shadow-lg border border-gray-100">
            <div class="flex items-start space-x-3">
                <div class="w-8 h-8 gradient-bg rounded-lg flex items-center justify-center flex-shrink-0 mt-1">
                    <i class="fas fa-robot text-white text-sm"></i>
                </div>
                <p class="text-gray-800 leading-relaxed">${formatMessage(message)}</p>
            </div>
        </div>
    `;
    messagesContainer.appendChild(messageDiv);
    scrollToBottom();
    chatHistory.push({ role: 'assistant', content: message });
}

// Show typing indicator
function showTypingIndicator() {
    const messagesContainer = document.getElementById('chatMessages');
    const typingDiv = document.createElement('div');
    const typingId = 'typing-' + Date.now();
    typingDiv.id = typingId;
    typingDiv.className = 'flex justify-start message';
    typingDiv.innerHTML = `
        <div class="bg-white px-6 py-4 rounded-3xl rounded-tl-md shadow-lg border border-gray-100">
            <div class="flex items-center space-x-2">
                <div class="w-2 h-2 bg-purple-500 rounded-full animate-bounce"></div>
                <div class="w-2 h-2 bg-purple-500 rounded-full animate-bounce" style="animation-delay: 0.2s"></div>
                <div class="w-2 h-2 bg-purple-500 rounded-full animate-bounce" style="animation-delay: 0.4s"></div>
            </div>
        </div>
    `;
    messagesContainer.appendChild(typingDiv);
    scrollToBottom();
    return typingId;
}

// Remove typing indicator
function removeTypingIndicator(typingId) {
    const typingDiv = document.getElementById(typingId);
    if (typingDiv) {
        typingDiv.remove();
    }
}

// Add sources message
function addSourcesMessage(sources) {
    const messagesContainer = document.getElementById('chatMessages');
    const sourcesDiv = document.createElement('div');
    sourcesDiv.className = 'flex justify-start message';
    
    let sourcesHtml = sources.slice(0, 3).map((source, index) => {
        const filename = source.metadata?.filename || 'Unknown';
        const score = (source.score * 100).toFixed(0);
        const text = source.text.substring(0, 150) + '...';
        return `
            <div class="mb-3 pb-3 ${index < 2 ? 'border-b border-gray-200' : ''}">
                <div class="flex items-center justify-between mb-2">
                    <span class="font-semibold text-gray-800">Source ${index + 1}</span>
                    <span class="text-sm text-purple-600 font-medium">${score}% match</span>
                </div>
                <p class="text-sm text-gray-600 mb-1"><i class="fas fa-file mr-2"></i>${filename}</p>
                <p class="text-xs text-gray-500">${text}</p>
            </div>
        `;
    }).join('');
    
    sourcesDiv.innerHTML = `
        <div class="max-w-[70%] bg-purple-50 px-6 py-4 rounded-2xl border border-purple-200">
            <h4 class="font-bold text-gray-800 mb-3 flex items-center">
                <i class="fas fa-book text-purple-600 mr-2"></i>
                Sources
            </h4>
            ${sourcesHtml}
        </div>
    `;
    messagesContainer.appendChild(sourcesDiv);
    scrollToBottom();
}

// Load videos
async function loadVideos(query) {
    const videosList = document.getElementById('videosList');
    videosList.innerHTML = '<p class="text-gray-400 text-sm">Loading...</p>';
    
    try {
        const response = await fetch(`${BACKEND_URL}/api/integrations/youtube?query=${encodeURIComponent(query)}&max_results=5`);
        const data = await response.json();
        
        if (data.success && data.results && data.results.length > 0) {
            videosList.innerHTML = data.results.map(video => `
                <a href="${video.link}" target="_blank" class="block p-3 bg-gray-50 rounded-xl hover:bg-purple-50 transition-colors border border-gray-200 hover:border-purple-300">
                    <p class="font-semibold text-gray-800 text-sm mb-1 line-clamp-2">${video.title}</p>
                    <p class="text-xs text-gray-500">
                        <i class="fas fa-user mr-1"></i>${video.channel || 'Unknown'}
                        <span class="mx-2">•</span>
                        <i class="fas fa-clock mr-1"></i>${video.duration || 'N/A'}
                    </p>
                </a>
            `).join('');
        } else {
            videosList.innerHTML = '<p class="text-gray-500 text-sm text-center py-4">No videos found</p>';
        }
    } catch (error) {
        videosList.innerHTML = '<p class="text-red-500 text-sm">Error loading videos</p>';
        console.error('Error loading videos:', error);
    }
}

// Load news
async function loadNews(query) {
    const newsList = document.getElementById('newsList');
    newsList.innerHTML = '<p class="text-gray-400 text-sm">Loading...</p>';
    
    try {
        const response = await fetch(`${BACKEND_URL}/api/integrations/news?query=${encodeURIComponent(query)}&max_results=5`);
        const data = await response.json();
        
        if (data.success && data.results && data.results.length > 0) {
            newsList.innerHTML = data.results.map(article => `
                <a href="${article.link}" target="_blank" class="block p-3 bg-gray-50 rounded-xl hover:bg-purple-50 transition-colors border border-gray-200 hover:border-purple-300">
                    <p class="font-semibold text-gray-800 text-sm mb-1 line-clamp-2">${article.title}</p>
                    <p class="text-xs text-gray-500">
                        <i class="fas fa-newspaper mr-1"></i>${article.source || 'Unknown'}
                        <span class="mx-2">•</span>
                        <i class="fas fa-calendar mr-1"></i>${article.date || 'N/A'}
                    </p>
                </a>
            `).join('');
        } else {
            newsList.innerHTML = '<p class="text-gray-500 text-sm text-center py-4">No news found</p>';
        }
    } catch (error) {
        newsList.innerHTML = '<p class="text-red-500 text-sm">Error loading news</p>';
        console.error('Error loading news:', error);
    }
}

// Clear chat
function clearChat() {
    if (confirm('Are you sure you want to clear the chat history?')) {
        const messagesContainer = document.getElementById('chatMessages');
        messagesContainer.innerHTML = `
            <div class="flex justify-center">
                <div class="bg-white rounded-2xl shadow-md p-6 max-w-md text-center">
                    <div class="text-4xl mb-3">👋</div>
                    <h3 class="text-xl font-bold text-gray-800 mb-2">Welcome to FinBot!</h3>
                    <p class="text-gray-600 mb-4">I'm here to help with all your financial questions.</p>
                    <div class="flex flex-wrap gap-2 justify-center">
                        <button onclick="sendMessage('What are mutual funds?')" class="px-4 py-2 bg-purple-100 text-purple-700 rounded-full text-sm font-medium hover:bg-purple-200 transition-colors">
                            What are mutual funds?
                        </button>
                        <button onclick="sendMessage('How to start investing?')" class="px-4 py-2 bg-purple-100 text-purple-700 rounded-full text-sm font-medium hover:bg-purple-200 transition-colors">
                            How to start investing?
                        </button>
                        <button onclick="sendMessage('Tax saving tips')" class="px-4 py-2 bg-purple-100 text-purple-700 rounded-full text-sm font-medium hover:bg-purple-200 transition-colors">
                            Tax saving tips
                        </button>
                    </div>
                </div>
            </div>
        `;
        chatHistory = [];
        document.getElementById('videosList').innerHTML = '<p class="text-gray-500 text-center py-8">Ask a question to see related videos</p>';
        document.getElementById('newsList').innerHTML = '<p class="text-gray-500 text-center py-8">Ask a question to see latest news</p>';
    }
}

// Scroll to bottom
function scrollToBottom() {
    const messagesContainer = document.getElementById('chatMessages');
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

// Format message (basic markdown-like formatting)
function formatMessage(text) {
    // Convert line breaks
    text = text.replace(/\n/g, '<br>');
    // Bold text
    text = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    // Italic text
    text = text.replace(/\*(.*?)\*/g, '<em>$1</em>');
    return text;
}

// Escape HTML
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Initialize
document.addEventListener('DOMContentLoaded', function() {
    const input = document.getElementById('chatInput');
    if (input) {
        input.focus();
    }
});
