# FinBot - Financial Literacy Chatbot

A modular RAG-based chatbot for financial literacy using Google Gemini and SentenceTransformers embeddings with Qdrant vector database. Built with clean, maintainable Python code following DRY principles.

## Features

- **Document Processing**: PDF ingestion with OCR capabilities using Docling
- **Semantic Search**: Advanced embeddings using SentenceTransformers (BAAI/bge-large-en-v1.5)
- **LLM Integration**: Google Gemini for intelligent response generation
- **Vector Database**: Qdrant for efficient similarity search
- **Modular Architecture**: Clean separation of concerns with configurable components
- **Command-line Interface**: Simple CLI for document ingestion and chatbot interaction

## Architecture

The project follows a modular architecture with clear separation of responsibilities:

- **Parsing & Chunking**: Separate utilities for document processing and text segmentation
- **Embeddings**: Configurable embedding service with multiple model support
- **Vector Storage**: Qdrant client with automatic collection management
- **LLM Service**: Google Gemini integration with conversation support
- **RAG Pipeline**: Orchestrates retrieval and generation with context management
- **Data Ingestion**: Batch and single-file processing with configurable parameters

## Setup

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Start Qdrant Database**
   ```bash
   docker run -p 6333:6333 qdrant/qdrant
   ```

3. **Configure Environment**
   Create a `.env` file with your configuration:
   ```env
   # Qdrant Configuration
   QDRANT_HOST=localhost
   QDRANT_PORT=6333
   
   # Gemini Configuration
   GEMINI_MODEL=gemini-2.0-flash
   GEMINI_API_KEY=your_api_key_here
   
   # Embedding Configuration
   EMBEDDING_MODEL=BAAI/bge-large-en-v1.5
   
   # Chunking Configuration
   CHUNK_SIZE=1000
   CHUNK_OVERLAP=200
   
   # Retrieval Configuration
   TOP_K_RESULTS=5
   SCORE_THRESHOLD=0.3
   
   # Generation Configuration
   TEMPERATURE=0.1
   MAX_TOKENS=1024
   ```

## Usage

### 1. Ingest Documents
Place your PDF documents in the `Data/` folder, then run:

```bash
# Ingest all documents
python src/ingestion/ingest_data.py --ingest-all

# Ingest a single file
python src/ingestion/ingest_data.py --file path/to/document.pdf

# Clear existing data and reingest
python src/ingestion/ingest_data.py --ingest-all --clear

# Check collection status
python src/ingestion/ingest_data.py --status
```

### 2. Run the Chatbot
```bash
python main.py
```

### 3. Interactive Chat
Once running, you can ask questions about financial topics:
```
You: What is compound interest?
FinBot: [Response based on ingested documents and knowledge]

You: How do mutual funds work?
FinBot: [Contextual response with relevant document excerpts]

You: quit
Goodbye! Thanks for using FinBot!
```

## Configuration Options

All configuration is handled through environment variables with sensible defaults:

| Parameter | Description | Default | 
|-----------|-------------|---------|
| `CHUNK_SIZE` | Size of text chunks for processing | 1000 |
| `CHUNK_OVERLAP` | Overlap between consecutive chunks | 200 |
| `TOP_K_RESULTS` | Number of documents to retrieve | 5 |
| `SCORE_THRESHOLD` | Minimum similarity score (0.0-1.0) | 0.3 |
| `TEMPERATURE` | LLM response creativity (0.0-1.0) | 0.1 |
| `MAX_TOKENS` | Maximum response length | 1024 |
| `EMBEDDING_MODEL` | SentenceTransformer model name | BAAI/bge-large-en-v1.5 |
| `GEMINI_MODEL` | Gemini model variant | gemini-2.0-flash |

## Project Structure

```
FinBot/
├── Data/                           # PDF documents for ingestion
├── src/                           # Source code
│   ├── __init__.py               # Package initialization
│   ├── chatbot.py                # Main chatbot class
│   ├── rag_pipeline.py           # RAG orchestration logic
│   ├── embeddings/               # Embedding services
│   │   └── embeddings.py         # SentenceTransformers integration
│   ├── vectorstore/              # Vector database
│   │   └── qdrant_client.py      # Qdrant client wrapper
│   ├── llm/                      # Language model services
│   │   ├── __init__.py
│   │   └── gemini.py             # Google Gemini integration
│   ├── utils/                    # Utility modules
│   │   ├── parsing.py            # PDF parsing with Docling
│   │   └── chunking.py           # Text chunking strategies
│   └── ingestion/                # Data processing
│       └── ingest_data.py        # Document ingestion pipeline
├── main.py                       # Application entry point
├── requirements.txt              # Python dependencies
├── .env                         # Environment configuration
├── .gitignore                   # Git ignore patterns
└── README.md                    # This file
```

## Key Features

### Modular Design
- **Separation of Concerns**: Each module has a single responsibility
- **DRY Principle**: No code duplication, shared configuration management
- **Factory Pattern**: Consistent component creation with environment-based defaults
- **Clean Interfaces**: Well-defined APIs between components

### Document Processing
- **OCR Support**: Handles scanned PDFs and images using Docling
- **Multiple Chunking Strategies**: Word-based, sentence-based, and paragraph-based chunking
- **Metadata Preservation**: Maintains document source, page numbers, and titles
- **Batch Processing**: Efficient handling of multiple documents

### Intelligent Retrieval
- **Semantic Search**: Uses state-of-the-art embeddings for document similarity
- **Configurable Retrieval**: Adjustable result count and similarity thresholds
- **Context Management**: Proper handling of conversation history
- **Source Attribution**: Tracks which documents contributed to responses

## Dependencies

Core dependencies:
- `torch` - PyTorch for deep learning models
- `transformers` - Hugging Face transformers library
- `sentence-transformers` - Embedding models
- `google-generativeai` - Google Gemini API
- `qdrant-client` - Vector database client
- `docling` - Advanced PDF processing with OCR
- `python-dotenv` - Environment configuration

## Development

The codebase follows Python best practices:
- **Type Hints**: Full type annotation for better IDE support
- **Docstrings**: Comprehensive documentation for all public methods
- **Error Handling**: Graceful error handling with informative messages
- **Configuration**: Environment-based configuration with defaults
- **Logging**: Clean, emoji-free logging and user feedback

## License

This project is for educational and research purposes. Please ensure you comply with the terms of service for Google Gemini API and respect the licenses of all dependencies.