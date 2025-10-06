# FinBot - Financial Literacy Chatbot

A simple RAG-based chatbot for financial literacy using Llama 3.1 8B model and SentenceTransformers embeddings with Qdrant vector database.

## Features

- Document ingestion from PDF files
- Semantic search using embeddings
- Local Llama 3.1 8B model for response generation
- Qdrant vector database for storing embeddings
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

3. **Ensure Llama Model is Available**
   - Make sure the Llama-3.1-8B model is in `/home/rajiv07/Chatbots/Llama-3.1-8B`
   - Or update the path in `.env` file

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

## File Structure

- `Data/` - PDF documents to be ingested
- `src/` - Source code
  - `Chunking/document_parser.py` - PDF parsing
  - `embeddings/qwen.py` - Embedding generation
  - `vectorstore/qdrant_client.py` - Vector database operations
  - `llm/llama.py` - Local LLM service
  - `ingestion/ingest_data.py` - Data ingestion pipeline
  - `rag_pipeline.py` - Main RAG orchestration
- `main.py` - Main application entry point

## Configuration

Edit `.env` file to configure:
- Qdrant connection settings
- Model paths
- Other parameters