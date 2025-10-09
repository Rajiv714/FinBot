# FinBot - Financial Literacy Chatbot

A simple RAG-based chatbot for financial literacy using Google Gemini and SentenceTransformers embeddings with Qdrant vector database.

## Features

- Document ingestion from PDF files
- Semantic search using embeddings
- Google Gemini for response generation
- Qdrant vector database for storing embeddings
- Configurable chunking and retrieval parameters
- Simple command-line interface

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
   - Update `.env` file with your Gemini API key
   - Adjust chunking and retrieval parameters as needed

## Configuration

Edit `.env` file to configure:

```env
# Qdrant Configuration
QDRANT_HOST=localhost
QDRANT_PORT=6333

# Gemini Configuration
GEMINI_MODEL=gemini-2.0-flash-exp
GEMINI_API_KEY=your_api_key_here

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
```bash
cd /home/rajiv07/Chatbots/FinBot
python src/ingestion/ingest_data.py --ingest-all
```

### 2. Run the Chatbot
```bash
python main.py
```

### 3. Ask Questions
```bash
python main.py --query "What is compound interest?"
```

## Configurable Parameters

- **CHUNK_SIZE**: Size of text chunks (default: 1000 words)
- **CHUNK_OVERLAP**: Overlap between chunks (default: 200 words)  
- **TOP_K_RESULTS**: Number of documents to retrieve (default: 5)
- **SCORE_THRESHOLD**: Minimum similarity score (default: 0.3)
- **TEMPERATURE**: Response creativity (default: 0.1)
- **MAX_TOKENS**: Maximum response length (default: 1024)

## File Structure

- `Data/` - PDF documents to be ingested
- `src/` - Source code
  - `Chunking/document_parser.py` - PDF parsing with configurable chunking
  - `embeddings/qwen.py` - Embedding generation
  - `vectorstore/qdrant_client.py` - Vector database operations with configurable retrieval
  - `llm/gemini.py` - Google Gemini LLM service
  - `ingestion/ingest_data.py` - Data ingestion pipeline
  - `rag_pipeline.py` - Main RAG orchestration
- `main.py` - Main application entry point