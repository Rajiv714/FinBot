# FinBot - Financial Literacy Assistant 💰

> 🚀 **AI-Powered Financial Education Platform** with RAG Chatbot, Handout Generator, and Document Analyzer  
> 🌐 **15 Indian Languages** | ⚡ **GPU-Accelerated** | 📺 **Live News & YouTube Integration**

[![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)](https://streamlit.io)
[![License](https://img.shields.io/badge/License-Educational-yellow.svg)](LICENSE)

---

## 🎯 What is FinBot?

A comprehensive financial education platform with RAG-based chatbot, educational handout generation, and document analysis. Built with Google Gemini, SentenceTransformers, and Qdrant vector database. Features multilingual support (15 Indian languages), GPU-accelerated OCR, and real-time news & YouTube integrations.

## ✨ Features

### 🤖 Three Core Modules

1. **Financial Chatbot**
   - RAG-based conversational AI with context-aware responses
   - Real-time news articles integration (Google News via SERPAPI)
   - Related YouTube videos sidebar (Educational content recommendations)
   - Semantic search with source attribution
   - 15 Indian language support with automatic translation

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

- **15 Indian Languages**: English, Hindi, Bengali, Telugu, Marathi, Tamil, Gujarati, Kannada, Malayalam, Punjabi, Odia, Urdu, Assamese, Konkani, Sanskrit
- **Auto-detection**: Automatic language detection for user queries
- **Deep Translator**: Handles 4000+ character translations with chunking
- **UI Translation**: All interface elements dynamically translated

### ⚡ Performance Features

- **GPU Acceleration**: CUDA-enabled OCR processing (5-10x faster)
- **Vector Database**: Qdrant with 1024-dim embeddings (BAAI/bge-large-en-v1.5)
- **Stateless Chat**: Token-optimized queries without history overhead
- **Smart Chunking**: 1000 chars with 200 overlap for optimal retrieval
- **Text Cleaning**: Automatic removal of headers, footers, page numbers

### 🎯 Advanced Capabilities

- **Context-Aware**: 10,000 char context window (~2000 words)
- **Dual Token Configs**: Chat (1024 tokens) vs Handout (3000 tokens)
- **Safety Settings**: Configurable content filtering with HarmCategory enums
- **Rich Sources**: Compact display with filename, score percentage, text preview
- **Colored UI**: Green-bordered answer boxes, emoji avatars, clean formatting

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

### Frontend (Streamlit)

```
frontend/
└── streamlit_app.py              # Multi-page web interface
    ├── Home Page                 # 3 feature cards
    ├── Chatbot Page              # Chat + News/YouTube sidebar
    ├── Learning Module Page      # Handout generator
    └── Document Summariser Page  # File upload & analysis
```

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
- **NVIDIA GPU** (optional, for faster OCR - 5-10x speedup)
- **CUDA** installed (if using GPU)

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

**Option 1: Web Interface (Recommended)**

```bash
# Terminal 1: Start Backend
chmod +x backend.sh
./backend.sh

# Terminal 2: Start Frontend
chmod +x frontend.sh
./frontend.sh
```

Access at: `http://localhost:8501`

**Option 2: Terminal Interface**

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
- Open browser at `http://localhost:8501`
- Currently uses terminal-based ingestion (web ingestion in development)

## 📖 Usage Guide

### Feature 1: Financial Chatbot 💬

1. Navigate to **Chatbot** page
2. Select language from top-right dropdown (15 languages available)
3. Ask questions in any supported language
4. **Right Sidebar** automatically shows:
   - 📺 Top 5 related YouTube videos
   - 📰 Top 5 latest news articles
5. View sources in compact format (filename, score, preview)
6. Answers are automatically translated to your selected language

**Example Questions:**
- "What is compound interest?"
- "How do mutual funds work?"
- "Explain tax-saving investment options"

### Feature 2: Learning Module Generator 📚

1. Navigate to **Learning Module** page
2. Enter topic (e.g., "Investment Strategies")
3. Configure options:
   - Target word count: 1000/1100/1200 words
   - Include latest news: ✓/✗ (uses Google Search)
   - Search depth: basic/standard/comprehensive
4. Click "Generate Learning Module"
5. Wait 30-60 seconds for 3-agent pipeline
6. Download as markdown file

**Generated Structure:**
- Introduction (200-220 words)
- Core Concepts (250-270 words)
- Practical Applications (250-270 words)
- Key Considerations (200-220 words)
- Additional Resources (150-170 words)

### Feature 3: Document Summariser 📄

1. Navigate to **Document Summariser** page
2. Upload PDF (loan agreement, insurance, investment doc)
3. Optional: Add specific question about document
4. View analysis showing:
   - Document type identification
   - Key information extraction
   - Answer to your specific question
5. Results available in all 15 languages

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
├── frontend/                     # Streamlit UI
│   └── streamlit_app.py          # Multi-page web interface
├── src/                          # Core libraries
│   ├── rag_pipeline.py           # RAG orchestration (stateless)
│   ├── summariser.py             # OpenRouter integration
│   ├── agents/                   # Multi-agent system
│   │   ├── base_agent.py         # Agent base class
│   │   ├── content_extractor.py  # Vector DB retrieval
│   │   ├── google_search_agent.py# SERPAPI search
│   │   └── handout_generator.py  # Content generation
│   ├── embeddings/
│   │   └── embeddings.py         # SentenceTransformer (GPU)
│   ├── llm/
│   │   └── gemini.py             # Gemini with use-case configs
│   ├── vectorstore/
│   │   └── qdrant_client.py      # Vector DB operations
│   ├── integrations/
│   │   ├── serp_news.py          # Google News API
│   │   └── serp_youtube.py       # YouTube API
│   └── utils/
│       ├── parsing.py            # Docling OCR (GPU-enabled)
│       └── chunking.py           # Text segmentation
├── Data/                         # PDF documents (78 files)
├── Handout/                      # Generated learning modules
├── main.py                       # Terminal interface
├── backend.sh                    # Backend startup script
├── frontend.sh                   # Frontend startup script
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
- **Chunking**: Handles 4000+ char translations
- **Bidirectional**: Query translation (to EN) + Response translation (to target)
- **UI Elements**: Pre-translated common phrases
- **Detection**: Automatic language detection for queries

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
streamlit>=1.28.0                 # Web UI
httpx>=0.25.0                     # Async HTTP client
python-multipart>=0.0.6           # File uploads
```

### Language & Search
```
deep-translator>=1.11.4           # 15 language support
langdetect>=1.0.9                 # Language detection
google-search-results>=2.4.2      # SERPAPI (News/YouTube)
```

### Utilities
```
python-dotenv>=1.0.0              # Environment config
pydantic>=2.5.0                   # Data validation
requests>=2.31.0                  # HTTP requests
```

**Total Size**: ~5-6 GB (includes PyTorch + models)

## 🐛 Troubleshooting

### Common Issues

**1. CUDA Out of Memory**
```bash
# Reduce batch size or disable GPU
export CUDA_VISIBLE_DEVICES=""  # Force CPU mode
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

**5. Translation Timeout**
```
Error: Translation failed
Solution: Text too long (>5000 chars), will be chunked automatically
```

**6. Port Already in Use**
```bash
# Kill process on port 8000 (backend)
lsof -ti:8000 | xargs kill -9
# Kill process on port 8501 (frontend)
lsof -ti:8501 | xargs kill -9
```

## 🎯 Performance Benchmarks

### Document Processing (78 PDFs)
- **GPU (RTX 4500)**: 12-15 minutes (~10-12 sec/doc)
- **CPU (12-core)**: 40-80 minutes (~30-60 sec/doc)
- **Speedup**: 5-10x with GPU

### Query Response Time
- **Vector Search**: 50-100ms
- **Gemini API**: 2-4 seconds
- **Total (Chat)**: 2-5 seconds
- **Total (Handout)**: 30-60 seconds (3 agents)

### Token Usage
- **Chat (stateless)**: ~2500 tokens/query
- **Chat (with history)**: ~6000 tokens/query (60% saving!)
- **Handout**: ~8000-10000 tokens/generation
- **Context**: 10,000 chars (~2000 words)

## 🚧 Known Limitations

1. **Web-based Ingestion**: Currently uses terminal interface (web UI in development)
2. **SERPAPI Free Tier**: Limited to 100 searches/month (upgrade for more)
3. **Translation**: Very long responses (>5000 chars) may take extra time
4. **GPU Memory**: Large PDFs may require 8GB+ VRAM for OCR
5. **Gemini Rate Limits**: Free tier limited to 60 requests/minute

## 🔮 Future Enhancements

- [ ] Web-based document ingestion UI
- [ ] Chat history persistence with session management
- [ ] Advanced analytics dashboard
- [ ] Export chat conversations to PDF
- [ ] Multi-document comparison feature
- [ ] Voice input/output support
- [ ] More language support (add regional languages)
- [ ] Fine-tuned embedding models for finance domain
- [ ] Blockchain integration for document verification
- [ ] Mobile app (React Native)

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