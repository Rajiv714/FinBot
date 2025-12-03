# FinBot - Financial Literacy Assistant 💰

> 🚀 **AI-Powered Financial Education Platform** with RAG Chatbot, Handout Generator, and Document Analyzer  
> 🌐 **15 Indian Languages** | ⚡ **GPU-Accelerated** | 📺 **Live News & YouTube Integration**

[![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-3.0+-38bdf8.svg)](https://tailwindcss.com)
[![License](https://img.shields.io/badge/License-Educational-yellow.svg)](LICENSE)

---

## 🎯 What is FinBot?

A comprehensive financial education platform with RAG-based chatbot, educational handout generation, and document analysis. Built with Google Gemini, SentenceTransformers, and Qdrant vector database. Features a modern web interface with Tailwind CSS, multilingual support (10 Indian languages), and real-time news & YouTube integrations.

## ✨ Features

### 🤖 Three Core Modules

1. **Financial Chatbot**
   - RAG-based conversational AI with context-aware responses
   - Real-time news articles integration (Google News via SERPAPI)
   - Related YouTube videos sidebar (Educational content recommendations)
   - Semantic search with source attribution
   - 10 Indian language support with automatic translation
   - Modern chat interface with typing indicators and message bubbles

2. **Educational Handout Generator**
   - AI-powered 1000-1200 word educational content creation
   - 3-agent pipeline: Content Extraction → Google Search → Generation
   - Structured format with 5 sections (Introduction, Concepts, Applications, etc.)
   - Optional latest news integration via Google Search
   - Download as markdown files

3. **Document Summarizer**
   - Financial document analysis (loan agreements, insurance, investments)
   - OCR support for scanned documents (PyMuPDF)
   - Document type identification (6 categories)
   - Natural language queries about documents
   - Powered by OpenRouter API (Grok model)

### 🌐 Multilingual Support

- **10 Indian Languages**: English, Hindi, Bengali, Telugu, Marathi, Tamil, Gujarati, Kannada, Malayalam, Punjabi
- **Seamless Translation**: AI-powered response translation via Gemini's multilingual capabilities
- **No Backend Changes**: Language support implemented via intelligent prompt engineering
- **Dropdown Selection**: Easy language switching on all feature pages

### ⚡ Performance Features

- **Modern UI**: Responsive design with Tailwind CSS, glass-morphism effects, and smooth animations
- **Vector Database**: Qdrant with 1024-dim embeddings (BAAI/bge-large-en-v1.5)
- **Stateless Chat**: Token-optimized queries without history overhead
- **Smart Chunking**: 1000 chars with 200 overlap for optimal retrieval
- **Fast Loading**: CDN-based assets for instant page loads

### 🎯 Advanced Capabilities

- **Context-Aware**: 10,000 char context window (~2000 words)
- **Dual Token Configs**: Chat (1024 tokens) vs Handout (3000 tokens)
- **Safety Settings**: Configurable content filtering with HarmCategory enums
- **Rich UI**: Purple-blue gradient design, card-based layouts, hover effects
- **Auto-Detection**: Automatically uses correct backend URL for local or network access

## 🏗️ Architecture

### Backend (FastAPI)

```
backend/
├── api.py                        # REST API endpoints (7 endpoints)
├── models/
│   └── schemas.py                # Pydantic models for validation
└── services/
    ├── chatbot_service.py        # Chat logic with RAG pipeline
    ├── handout_service.py        # 3-agent handout generation
    ├── ingestion_service.py      # Document processing
    └── summariser_service.py     # Document analysis
```

**API Endpoints:**
- `POST /api/chat` - Single query with RAG
- `POST /api/handouts` - Generate educational handouts
- `POST /api/summarise` - Analyze financial documents
- `POST /api/ingest` - Ingest PDF documents
- `GET /api/integrations/news` - Fetch news articles
- `GET /api/integrations/youtube` - Fetch YouTube videos
- `GET /api/status` - System health check

### Frontend (HTML/CSS/JavaScript)

```
frontend/
├── index.html                    # Modern landing page
├── images/
│   └── logo.png                  # Custom branding logo
├── pages/
│   ├── chatbot.html              # Chat interface with sidebar
│   ├── learning.html             # Handout generator page
│   └── summariser.html           # Document analyzer page
└── js/
    ├── chatbot.js                # Chat logic and API calls
    ├── learning.js               # Handout generation logic
    └── summariser.js             # Document analysis logic
```

**Design Features:**
- Tailwind CSS 3.0 (CDN) for modern styling
- Glass-morphism navigation with logo
- Responsive design (mobile, tablet, desktop)
- Purple-blue gradient theme (#667eea → #764ba2)
- Smooth animations and hover effects
- Font Awesome 6.5.1 icons
- Google Fonts (Inter family)

### Core Services

```
src/
├── rag_pipeline.py               # RAG orchestration (stateless)
├── llm/
│   └── gemini.py                 # Gemini API with use-case configs
├── embeddings/
│   └── embeddings.py             # SentenceTransformer (GPU-enabled)
├── vectorstore/
│   └── qdrant_client.py          # Vector DB operations
├── agents/
│   ├── content_extractor.py     # Vector DB retrieval
│   ├── google_search_agent.py   # SERPAPI integration
│   └── handout_generator.py     # Content generation
├── integrations/
│   ├── serp_news.py             # Google News API
│   └── serp_youtube.py          # YouTube API
├── utils/
│   ├── parsing.py               # Docling OCR (GPU-accelerated)
│   └── chunking.py              # Text segmentation
└── summariser.py                # OpenRouter document analysis
```

## 🚀 Quick Start

### Prerequisites

- **Python 3.12+** with virtual environment
- **Docker** (for Qdrant vector database)
- **Modern Web Browser** (Chrome, Firefox, Safari, Edge)
- **No build tools required** (pure HTML/CSS/JavaScript)

### 1. Installation

```bash
# Clone repository
git clone <repository-url>
cd FinBot

# Create virtual environment (at parent level)
cd ..
python3 -m venv myenv
source myenv/bin/activate
cd FinBot

# Install dependencies
pip install -r requirements.txt
```

### 2. Start Qdrant Database

```bash
docker run -p 6333:6333 -v $(pwd)/qdrant_storage:/qdrant/storage qdrant/qdrant
```

### 3. Configure Environment

Create `.env` file in project root:

```env
# Qdrant Configuration
QDRANT_HOST=localhost
QDRANT_PORT=6333

# Embedding Configuration
EMBEDDING_MODEL=BAAI/bge-large-en-v1.5

# Gemini Configuration (Get key: https://makersuite.google.com/app/apikey)
GEMINI_MODEL=gemini-2.5-flash
GEMINI_API_KEY=your_gemini_api_key_here

# SERPAPI Configuration (Get key: https://serpapi.com/manage-api-key)
# Free tier: 100 searches/month
SERPAPI_API_KEY=your_serpapi_key_here

# Token Configuration
MAX_TOKENS_CHAT=1024
MAX_TOKENS_HANDOUT=3000

# OpenRouter Config (Get key: https://openrouter.ai/keys)
OPENROUTER_API_KEY=your_openrouter_key_here
OPENROUTER_MODEL=x-ai/grok-4.1-fast:free
OPENROUTER_URL=https://openrouter.ai/api/v1/chat/completions

# Chunking Configuration
CHUNK_SIZE=1000
CHUNK_OVERLAP=200

# Retrieval Configuration
TOP_K_RESULTS=5
SCORE_THRESHOLD=0.3

# Generation Configuration
TEMPERATURE=0.2
MAX_TEXT_LENGTH=15000
```

### 4. Run the Application

**Start Backend and Frontend:**

```bash
# Terminal 1: Start Backend (FastAPI on port 8000)
chmod +x backend.sh
./backend.sh

# Terminal 2: Start Frontend (HTTP server on port 5000)
chmod +x frontend.sh
./frontend.sh
```

**Access the Application:**
- Local: `http://localhost:5000`
- Network: `http://[your-ip]:5000` (e.g., `http://192.168.1.100:5000`)
- Frontend auto-detects backend URL (localhost or network)

**Alternative Terminal Interface:**

```bash
python3 main.py
```

### 5. Ingest Documents (First Time)

Place PDF files in `Data/` folder, then:

**Via Terminal:**
```bash
python3 main.py
# Choose option: 2. Ingest Financial Documents
```

**Via Web Interface:**
- Open browser at `http://localhost:5000`
- Navigate to home page
- Use terminal interface for ingestion (web ingestion in development)
- Or run: `python3 main.py` and choose option 2

## 📖 Usage Guide

### Feature 1: Financial Chatbot 💬

1. Navigate to **Chatbot** page from home
2. Select language from dropdown (10 languages: English, Hindi, Bengali, Telugu, Marathi, Tamil, Gujarati, Kannada, Malayalam, Punjabi)
3. Type your question in the chat input
4. Click send or press Enter
5. **Right Sidebar** automatically shows:
   - 📺 Top 5 related YouTube videos
   - 📰 Top 5 latest news articles
6. AI responds in your selected language (via natural prompt translation)
7. View responses with proper formatting and markdown support

**Example Questions:**
- "What is compound interest?"
- "How do mutual funds work?"
- "Explain tax-saving investment options"

### Feature 2: Learning Module Generator 📚

1. Navigate to **Learning Module** page from home
2. Select output language from dropdown (10 languages)
3. Enter topic (e.g., "Investment Strategies") or click a suggestion chip
4. Configure options:
   - Target word count: 1000/1100/1200 words
   - Include latest news: ✓/✗ (uses Google Search)
   - Search depth: basic/standard/comprehensive
5. Click "Generate Handout"
6. Watch animated progress bar (30-60 seconds)
7. View generated content with markdown formatting
8. Download as `.md` file

**Generated Structure:**
- Introduction (200-220 words)
- Core Concepts (250-270 words)
- Practical Applications (250-270 words)
- Key Considerations (200-220 words)
- Additional Resources (150-170 words)

### Feature 3: Document Summariser 📄

1. Navigate to **Document Summariser** page from home
2. Select analysis language from dropdown (10 languages)
3. Drag and drop PDF file or click to browse
4. View file info (name, size, type)
5. Optional: Add specific question about the document
6. Click "Analyze Document"
7. Wait for processing (10-30 seconds depending on file size)
8. View comprehensive analysis:
   - Document type identification
   - Summary in selected language
   - Answer to your question (if provided)
   - Important points highlighted
   - Warnings about potential issues
   - Action points recommended
9. Download analysis as `.txt` file

**Supported Document Types:**
- Personal Loan Agreements
- Mortgage Documents
- Credit Card Terms
- Insurance Policies
- Investment Prospectuses
- Loan Agreements

## ⚙️ Configuration Options

## ⚙️ Configuration Options

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `GEMINI_API_KEY` | Google Gemini API key | - | ✅ |
| `SERPAPI_API_KEY` | SERPAPI key (News/YouTube) | - | ✅ |
| `OPENROUTER_API_KEY` | OpenRouter key (Summariser) | - | ✅ |
| `QDRANT_HOST` | Vector DB host | localhost | ✅ |
| `QDRANT_PORT` | Vector DB port | 6333 | ✅ |
| `EMBEDDING_MODEL` | SentenceTransformer model | BAAI/bge-large-en-v1.5 | ✅ |
| `GEMINI_MODEL` | Gemini model variant | gemini-2.5-flash | ✅ |
| `MAX_TOKENS_CHAT` | Chat response token limit | 1024 | ❌ |
| `MAX_TOKENS_HANDOUT` | Handout token limit | 3000 | ❌ |
| `CHUNK_SIZE` | Text chunk size (chars) | 1000 | ❌ |
| `CHUNK_OVERLAP` | Chunk overlap (chars) | 200 | ❌ |
| `TOP_K_RESULTS` | Documents to retrieve | 5 | ❌ |
| `SCORE_THRESHOLD` | Min similarity score (0-1) | 0.3 | ❌ |
| `TEMPERATURE` | LLM creativity (0-1) | 0.2 | ❌ |

### API Rate Limits

- **Gemini Free Tier**: 60 requests/minute
- **SERPAPI Free Tier**: 100 searches/month
- **OpenRouter**: Varies by model (Grok is free)

### GPU Configuration

Automatic GPU detection and usage:
- **Embeddings**: Uses CUDA if available (faster encoding)
- **OCR**: GPU-accelerated with EasyOCR (5-10x speedup)
- **Fallback**: CPU mode if CUDA not available

Check GPU status:
```bash
nvidia-smi  # Check GPU availability
python -c "import torch; print(torch.cuda.is_available())"  # Check PyTorch CUDA
```

## 📁 Project Structure

```
FinBot/
├── backend/                      # FastAPI backend
│   ├── api.py                    # REST API (7 endpoints)
│   ├── models/
│   │   └── schemas.py            # Pydantic validation models
│   └── services/                 # Business logic layer
│       ├── chatbot_service.py    # RAG chatbot service
│       ├── handout_service.py    # 3-agent handout pipeline
│       ├── ingestion_service.py  # Document processing
│       └── summariser_service.py # Document analysis
├── frontend/                     # Modern web interface
│   ├── index.html                # Landing page with hero section
│   ├── images/
│   │   └── logo.png              # Custom branding (126KB)
│   ├── pages/
│   │   ├── chatbot.html          # Chat interface (bubble UI)
│   │   ├── learning.html         # Handout generator
│   │   └── summariser.html       # Document analyzer
│   └── js/
│       ├── chatbot.js            # Chat logic (304 lines)
│       ├── learning.js           # Handout logic (137 lines)
│       └── summariser.js         # Analysis logic (289 lines)
├── src/                          # Core libraries
│   ├── rag_pipeline.py           # RAG orchestration (stateless)
│   ├── summariser.py             # OpenRouter integration
│   ├── agents/                   # Multi-agent system
│   │   ├── base_agent.py         # Agent base class
│   │   ├── content_extractor.py  # Vector DB retrieval
│   │   ├── google_search_agent.py# SERPAPI search
│   │   └── handout_generator.py  # Content generation
│   ├── embeddings/
│   │   └── embeddings.py         # SentenceTransformer
│   ├── llm/
│   │   └── gemini.py             # Gemini with safety settings
│   ├── vectorstore/
│   │   └── qdrant_client.py      # Vector DB operations
│   ├── integrations/
│   │   ├── serp_news.py          # Google News API
│   │   └── serp_youtube.py       # YouTube API
│   └── utils/
│       ├── parsing.py            # Docling OCR
│       └── chunking.py           # Text segmentation
├── Data/                         # PDF documents (78 files)
├── Handout/                      # Generated learning modules
├── main.py                       # Terminal interface
├── backend.sh                    # Backend startup script
├── frontend.sh                   # Frontend startup script (Python HTTP server)
├── requirements.txt              # Python dependencies
├── .env                          # Configuration (not in git)
└── README.md                     # This file
```

## 🔑 Key Technical Highlights

### 1. Stateless Chat Architecture
- **No history stored**: Reduces token usage by 60-70%
- **Single query processing**: Each query is independent
- **Context from vector DB**: Retrieves relevant chunks per query
- **10,000 char context window**: ~2000 words for quality answers

### 2. Multi-Agent Handout System
```
Phase 1: ContentExtractor → Vector DB search (5-10s)
Phase 2: GoogleSearch → Latest news (optional, 10-20s)
Phase 3: HandoutGenerator → 1200-word content (10-30s)
Total: 30-60 seconds
```

### 3. GPU-Accelerated Pipeline
- **Embedding**: CUDA-enabled SentenceTransformer
- **OCR**: EasyOCR with GPU support (cuda:0)
- **Performance**: 78 PDFs processed in ~12-15 minutes vs 40-80 minutes CPU
- **Hardware**: NVIDIA RTX 4500 Ada (24GB VRAM)

### 4. Multilingual Deep Translation
- **Prompt Engineering**: Natural language instructions appended to queries
- **Gemini Multilingual**: Leverages native multilingual capabilities
- **10 Languages**: English + 9 major Indian languages
- **No Backend Changes**: Pure frontend implementation

### 5. Safety & Content Filtering
```python
HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE
HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE
HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE
HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE
```

### 6. Text Cleaning Pipeline
- Removes: Page numbers, headers/footers, URLs, emails
- Normalizes: Excessive whitespace, decorative lines
- Filters: Lines with <3 alphanumeric chars (junk removal)
- **Result**: 30-40% token reduction in vector DB

## 📦 Dependencies

### Core Libraries
```
torch>=2.0.0                      # PyTorch (CUDA support)
transformers>=4.30.0              # Hugging Face transformers
sentence-transformers>=2.2.0      # Embeddings (GPU-enabled)
google-generativeai>=0.3.0        # Gemini API
qdrant-client>=1.7.0              # Vector database
docling>=1.0.0                    # OCR with GPU support
PyMuPDF>=1.23.0                   # PDF processing for summariser
```

### Web Framework
```
fastapi>=0.104.0                  # REST API
uvicorn[standard]>=0.24.0         # ASGI server
httpx>=0.25.0                     # Async HTTP client
python-multipart>=0.0.6           # File uploads
```

### Frontend (No Dependencies)
```
Pure HTML5, CSS3, JavaScript      # No build tools required
Tailwind CSS 3.0 (CDN)            # Modern styling framework
Font Awesome 6.5.1 (CDN)          # Icon library
Google Fonts - Inter (CDN)        # Typography
Marked.js (CDN)                   # Markdown rendering
```

### Language & Search
```
google-search-results>=2.4.2      # SERPAPI (News/YouTube)
```

### Utilities
```
python-dotenv>=1.0.0              # Environment config
pydantic>=2.5.0                   # Data validation
requests>=2.31.0                  # HTTP requests
```

**Total Size**: ~4-5 GB (includes PyTorch + models)

## 🐛 Troubleshooting

### Common Issues

**1. Port Already in Use**
```bash
# Kill process on port 8000 (backend)
lsof -ti:8000 | xargs kill -9
# Kill process on port 5000 (frontend)
lsof -ti:5000 | xargs kill -9
```

**2. Qdrant Connection Failed**
```bash
# Check if Qdrant is running
docker ps | grep qdrant
# Restart Qdrant
docker restart <container_id>
```

**3. SERPAPI Invalid Key**
```
Error: Invalid API key
Solution: Get new key from https://serpapi.com/manage-api-key
Update SERPAPI_API_KEY in .env
```

**4. Gemini Rate Limit**
```
Error: 429 Resource Exhausted
Solution: Wait 60 seconds (free tier: 60 req/min)
```

**5. Gemini Safety Filters**
```
Error: "I apologize, but I couldn't generate a response..."
Solution: 
- Rephrase question more simply
- Remove special characters
- Ask in English first, then switch language
- Break complex questions into smaller parts
```

**6. Frontend Not Loading**
```bash
# Check if backend is running
curl http://localhost:8000/api/health
# Should return: {"status":"healthy"}

# Check frontend server
ps aux | grep "python3 -m http.server"
# Restart if needed
./frontend.sh
```

## 🎯 Performance Benchmarks

### Query Response Time
- **Vector Search**: 50-100ms
- **Gemini API**: 2-4 seconds
- **Total (Chat)**: 2-5 seconds
- **Total (Handout)**: 30-60 seconds (3 agents)
- **Page Load**: <1 second (CDN assets)

### Token Usage
- **Chat (stateless)**: ~2500 tokens/query
- **Chat (with history)**: ~6000 tokens/query (60% saving!)
- **Handout**: ~8000-10000 tokens/generation
- **Context**: 10,000 chars (~2000 words)

## 🚧 Known Limitations

1. **Web-based Ingestion**: Currently uses terminal interface (web UI in development)
2. **SERPAPI Free Tier**: Limited to 100 searches/month (upgrade for more)
3. **Language Translation**: Relies on Gemini's multilingual capabilities (quality varies by language)
4. **Network Access**: Best on local WiFi; internet access via tunneling not implemented
5. **Gemini Rate Limits**: Free tier limited to 60 requests/minute
6. **Safety Filters**: Some queries may be blocked by Gemini's content filtering

## 🔮 Future Enhancements

- [ ] Web-based document ingestion UI
- [ ] Chat history persistence with session management
- [ ] Advanced analytics dashboard
- [ ] Export chat conversations to PDF
- [ ] Multi-document comparison feature
- [ ] Voice input/output support
- [ ] More language support (regional languages)
- [ ] Fine-tuned embedding models for finance domain
- [ ] Progressive Web App (PWA) for offline access
- [ ] Mobile-optimized responsive design improvements
- [ ] Dark mode theme support
- [ ] Cloud deployment guides (AWS, GCP, Azure)

## 🤝 Contributing

This is an educational project. Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

**Code Standards:**
- Follow PEP 8 style guide
- Add type hints for all functions
- Include docstrings (Google style)
- Write unit tests for new features
- Update README with new features

## 📄 License

This project is for **educational and research purposes**. 

**API Terms:**
- Comply with [Google Gemini Terms of Service](https://ai.google.dev/terms)
- Comply with [SERPAPI Terms](https://serpapi.com/terms)
- Comply with [OpenRouter Terms](https://openrouter.ai/terms)

**Dependencies:**
- All libraries used are under permissive licenses (Apache 2.0, MIT, BSD)