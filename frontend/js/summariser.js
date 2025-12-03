// Backend API URL - automatically detects the correct host
const BACKEND_URL = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
    ? 'http://localhost:8000' 
    : `http://${window.location.hostname}:8000`;

let selectedFile = null;
let currentAnalysis = null;

// Handle file select
function handleFileSelect(event) {
    const file = event.target.files[0];
    if (file && file.type === 'application/pdf') {
        selectedFile = file;
        displayFileInfo(file);
        document.getElementById('analyzeBtn').disabled = false;
    } else {
        alert('Please select a valid PDF file');
    }
}

// Display file info
function displayFileInfo(file) {
    const fileInfo = document.getElementById('fileInfo');
    const fileName = document.getElementById('fileName');
    const fileSize = document.getElementById('fileSize');
    
    fileName.textContent = file.name;
    fileSize.textContent = formatFileSize(file.size);
    fileInfo.classList.remove('hidden');
}

// Clear file
function clearFile() {
    selectedFile = null;
    document.getElementById('fileInput').value = '';
    document.getElementById('fileInfo').classList.add('hidden');
    document.getElementById('analyzeBtn').disabled = true;
}

// Format file size
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}

// Analyze document
async function analyzeDocument() {
    if (!selectedFile) {
        alert('Please select a file first');
        return;
    }
    
    let query = document.getElementById('documentQuery').value.trim();
    const loadingIndicator = document.getElementById('loadingIndicator');
    const resultsContainer = document.getElementById('analysisResults');
    
    // Get selected language
    const langSelect = document.getElementById('languageSelect');
    const selectedLang = langSelect ? langSelect.value : 'en';
    
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
        query = query ? `[Analyze in ${languageName} language] ${query}` : `Analyze this document and provide output in ${languageName} language`;
    }
    
    // Show loading
    resultsContainer.classList.add('hidden');
    loadingIndicator.classList.remove('hidden');
    
    try {
        // Create form data
        const formData = new FormData();
        formData.append('file', selectedFile);
        if (query) {
            formData.append('user_query', query);
        }
        
        // Call API
        const response = await fetch(`${BACKEND_URL}/api/summarise`, {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            throw new Error('API request failed');
        }
        
        const data = await response.json();
        
        // Debug: Log the response
        console.log('API Response:', data);
        
        // Hide loading
        loadingIndicator.classList.add('hidden');
        resultsContainer.classList.remove('hidden');
        
        if (data.success) {
            currentAnalysis = data; // Store for download
            displayResults(data);
        } else {
            throw new Error(data.error || 'Analysis failed');
        }
        
    } catch (error) {
        loadingIndicator.classList.add('hidden');
        resultsContainer.classList.remove('hidden');
        resultsContainer.innerHTML = `
            <div class="bg-red-50 border border-red-200 rounded-xl p-6 text-center">
                <i class="fas fa-exclamation-circle text-red-500 text-4xl mb-3"></i>
                <p class="text-red-600 font-semibold mb-2">Error</p>
                <p class="text-gray-600">${error.message}</p>
                <p class="text-sm text-gray-500 mt-2">Please make sure the backend server is running</p>
            </div>
        `;
        console.error('Error:', error);
    }
}

// Display results
function displayResults(data) {
    const resultsContainer = document.getElementById('analysisResults');
    
    let html = '';
    
    // Success message
    html += `
        <div class="bg-green-50 border border-green-200 rounded-xl p-4 mb-6">
            <div class="flex items-center">
                <i class="fas fa-check-circle text-green-500 text-2xl mr-3"></i>
                <span class="text-green-700 font-semibold">Analysis completed successfully!</span>
            </div>
        </div>
    `;
    
    // Document Type
    if (data.document_type) {
        html += `
            <div class="mb-6">
                <h4 class="text-lg font-bold text-gray-800 mb-2 flex items-center">
                    <i class="fas fa-file-alt text-purple-600 mr-2"></i>
                    Document Type
                </h4>
                <div class="bg-purple-50 border border-purple-200 rounded-xl p-4">
                    <p class="text-gray-800 font-semibold">${data.document_type}</p>
                </div>
            </div>
        `;
    }
    
    // Main Analysis
    if (data.analysis) {
        // Convert markdown bold (**text**) to HTML bold
        const formattedAnalysis = data.analysis
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\n/g, '<br>');
        
        html += `
            <div class="mb-6">
                <h4 class="text-lg font-bold text-gray-800 mb-2 flex items-center">
                    <i class="fas fa-comment-dots text-purple-600 mr-2"></i>
                    Analysis
                </h4>
                <div class="bg-gray-50 border border-gray-200 rounded-xl p-6">
                    <div class="text-gray-800 leading-relaxed">${formattedAnalysis}</div>
                </div>
            </div>
        `;
    }
    
    // Download Button
    if (data.analysis) {
        html += `
            <div class="text-center">
                <button onclick="downloadAnalysis()" class="inline-flex items-center px-6 py-3 bg-gradient-to-r from-purple-600 to-pink-600 text-white font-semibold rounded-xl hover:shadow-lg transform hover:-translate-y-1 transition-all duration-300">
                    <i class="fas fa-download mr-2"></i>
                    Download Analysis
                </button>
            </div>
        `;
    }
    
    resultsContainer.innerHTML = html;
}

// Escape HTML
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Capitalize first letter
function capitalizeFirst(str) {
    return str.charAt(0).toUpperCase() + str.slice(1).replace(/_/g, ' ');
}

// Download analysis as text file
function downloadAnalysis() {
    if (!currentAnalysis || !currentAnalysis.analysis) {
        alert('No analysis to download');
        return;
    }
    
    // Create formatted content
    let content = '========================================\n';
    content += 'DOCUMENT ANALYSIS\n';
    content += '========================================\n\n';
    
    if (currentAnalysis.document_type) {
        content += `Document Type: ${currentAnalysis.document_type}\n\n`;
    }
    
    if (currentAnalysis.filename) {
        content += `Filename: ${currentAnalysis.filename}\n\n`;
    }
    
    content += '----------------------------------------\n';
    content += 'ANALYSIS\n';
    content += '----------------------------------------\n\n';
    
    // Remove markdown formatting for plain text
    const plainAnalysis = currentAnalysis.analysis.replace(/\*\*(.*?)\*\*/g, '$1');
    content += plainAnalysis;
    
    content += '\n\n----------------------------------------\n';
    content += `Generated on: ${new Date().toLocaleString()}\n`;
    content += `Text Length: ${currentAnalysis.text_length || 'N/A'} characters\n`;
    content += '========================================\n';
    
    // Create and download file
    const blob = new Blob([content], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `analysis_${Date.now()}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

// Drag and drop handlers
const uploadArea = document.getElementById('fileUploadArea');

uploadArea.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadArea.classList.add('dragover');
});

uploadArea.addEventListener('dragleave', () => {
    uploadArea.classList.remove('dragover');
});

uploadArea.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadArea.classList.remove('dragover');
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        const file = files[0];
        if (file.type === 'application/pdf') {
            selectedFile = file;
            displayFileInfo(file);
            document.getElementById('analyzeBtn').disabled = false;
            // Update file input
            const dataTransfer = new DataTransfer();
            dataTransfer.items.add(file);
            document.getElementById('fileInput').files = dataTransfer.files;
        } else {
            alert('Please select a valid PDF file');
        }
    }
});
