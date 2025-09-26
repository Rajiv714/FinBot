# 🤖 FinBot - Financial Literacy Chatbot

FinBot is an advanced Retrieval-Augmented Generation (RAG) chatbot designed to answer questions about financial literacy. It combines the power of local large language models with vector similarity search to provide accurate, contextual responses based on your financial documents.

## ✨ Features

- **Local LLM**: Uses Llama 3.1 8B model for response generation
- **Advanced Embeddings**: Leverages Qwen2-Embedding-8B for semantic search
- **Document Processing**: Supports PDF parsing with Docling (handles text and images)
- **Vector Database**: Qdrant for efficient similarity search
- **Web Interface**: Beautiful Streamlit-based chat interface
- **CLI Support**: Command-line interface for quick queries
- **RAG Pipeline**: Retrieval-augmented generation for accurate responses
- **Flexible Architecture**: Modular design for easy customization

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   PDF Documents │────▶│  Docling Parser │────▶│  Text Chunks    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                        │
                                                        ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│     User Query  │────▶│ Qwen2 Embedding │────▶│ Vector Search   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                                              │
         │              ┌─────────────────┐            │
         └─────────────▶│  Llama 3.1 8B   │◀───────────┘
                        │   (Generation)  │
                        └─────────────────┘
                                 │
                                 ▼
                        ┌─────────────────┐
                        │    Response     │
                        └─────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Docker (for Qdrant)
- CUDA-capable GPU (recommended)
- At least 16GB RAM

### 1. Clone and Setup

```bash
git clone <repository-url>
cd FinBot

# Run automated setup
python setup.py --all
```

### 2. Start Qdrant Vector Database

```bash
# Using Docker
docker run -p 6333:6333 qdrant/qdrant

# Or using Docker Compose
docker-compose up -d qdrant
```

### 3. Add Your Financial Documents

Place your PDF documents in the `Data/` folder:

```bash
Data/
├── financial_guide.pdf
├── investment_basics.pdf
└── budgeting_tips.pdf
```

### 4. Ingest Documents

```bash
# Ingest all documents
python ingest_data.py --ingest-all

# Or ingest a single file
python ingest_data.py --file Data/your_document.pdf
```

### 5. Start the Chatbot

```bash
# Web interface (recommended)
python main.py --mode web

# Command line interface
python main.py --mode cli

# Or use the convenience script
./start.sh --web
```

## 📁 Project Structure

```
FinBot/
├── main.py                 # Main application entry point
├── ingest_data.py          # Data ingestion pipeline
├── setup.py                # Setup and system check script
├── start.sh                # Convenience startup script
├── requirements.txt        # Python dependencies
├── docker-compose.yml      # Docker services configuration
├── .env                    # Environment variables
├── .gitignore              # Git ignore rules
├── Readme.md              # This file
│
├── Data/                   # PDF documents folder
│   ├── GUIDE310113_F.pdf
│   └── MD18KYCF6E92C82E1E1419D87323E3869BC9F13.pdf
│
├── Llama-3.1-8B/         # Llama model files
│   ├── config.json
│   ├── tokenizer.json
│   ├── model-*.safetensors
│   └── ...
│
└── src/                   # Source code
    ├── __init__.py
    ├── document_parser.py      # PDF parsing with Docling
    ├── embedding_service.py    # Qwen2 embedding service
    ├── rag_pipeline.py        # RAG orchestration
    │
    ├── llm/                   # LLM services
    │   ├── __init__.py
    │   └── llama_service.py   # Llama 3.1 8B service
    │
    └── vectordb/              # Vector database
        ├── __init__.py
        └── qdrant_client.py   # Qdrant client
```

## ⚙️ Configuration

Environment variables in `.env`:

```bash
# Qdrant Configuration
QDRANT_HOST=localhost
QDRANT_PORT=6333
QDRANT_COLLECTION_NAME=financial_documents

# Model Paths
LLAMA_MODEL_PATH=./Llama-3.1-8B
EMBEDDING_MODEL_NAME=Alibaba-NLP/gte-Qwen2-7B-instruct

# Application Settings
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
MAX_TOKENS=4096
TEMPERATURE=0.1
TOP_K=5
LOG_LEVEL=INFO
```

## 🛠️ Advanced Usage

### Data Ingestion Options

```bash
# Clear existing data and re-ingest
python ingest_data.py --ingest-all --clear

# Custom chunk settings
python ingest_data.py --ingest-all --chunk-size 1500 --chunk-overlap 300

# List all PDF files
python ingest_data.py --list-files

# Check collection status
python ingest_data.py --status
```

### API Usage

```python
from src.rag_pipeline import create_rag_pipeline

# Initialize pipeline
rag = create_rag_pipeline()

# Single query
response = rag.query("What is compound interest?")
print(response["answer"])

# Chat conversation
messages = [
    {"role": "user", "content": "How should I start investing?"},
]
response = rag.chat(messages)
print(response["answer"])
```

### Web Interface Features

- **Interactive Chat**: Natural conversation with context
- **Source Attribution**: See which documents informed the response
- **Adjustable Settings**: Temperature control, context toggle
- **System Status**: Monitor component health
- **Example Questions**: Quick-start prompts

## 🔧 Troubleshooting

### Common Issues

**1. CUDA Out of Memory**
```bash
# Use CPU-only mode
export CUDA_VISIBLE_DEVICES=""

# Or reduce model precision in the code
# (Already implemented with 4-bit quantization)
```

**2. Qdrant Connection Error**
```bash
# Check if Qdrant is running
curl http://localhost:6333/health

# Restart Qdrant
docker restart <qdrant-container-id>
```

**3. Model Loading Issues**
```bash
# Verify model files
python setup.py --check

# Check available disk space
df -h
```

**4. Embedding Dimension Mismatch**
```bash
# Clear and recreate collection
python ingest_data.py --status
# Then re-ingest with --clear flag
```

### Performance Optimization

**GPU Usage**
- Ensure CUDA drivers are properly installed
- Monitor GPU memory usage with `nvidia-smi`
- Use mixed precision (FP16) for better performance

**Memory Management**
- Reduce `chunk_size` if running out of memory
- Lower `batch_size` in embedding service
- Use model quantization (already enabled)

**Response Speed**
- Keep Qdrant collection optimized
- Use SSD storage for better I/O
- Adjust `top_k` parameter for fewer retrievals

## 📊 System Requirements

### Minimum Requirements
- CPU: 4 cores
- RAM: 8GB
- Storage: 50GB
- GPU: Optional (CPU-only supported)

### Recommended Requirements
- CPU: 8+ cores
- RAM: 16GB+
- Storage: 100GB+ SSD
- GPU: 8GB+ VRAM (RTX 3070 or better)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **Llama 3.1**: Meta's powerful language model
- **Qwen2**: Alibaba's embedding model
- **Qdrant**: High-performance vector database
- **Docling**: Advanced document processing
- **Streamlit**: Beautiful web interfaces

## 📞 Support

For issues and questions:
1. Check the troubleshooting section
2. Review existing GitHub issues
3. Create a new issue with detailed information
4. Include system info and error logs

---

**Happy chatting with FinBot! 🤖💰**