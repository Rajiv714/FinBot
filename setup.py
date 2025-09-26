#!/usr/bin/env python3
"""
Setup script for FinBot - Financial Literacy Chatbot

This script helps with initial setup and environment configuration.
"""

import os
import sys
import subprocess
from pathlib import Path
import argparse


def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        return False
    print(f"✅ Python {sys.version.split()[0]} detected")
    return True


def check_cuda_availability():
    """Check if CUDA is available for GPU acceleration."""
    try:
        import torch
        if torch.cuda.is_available():
            device_count = torch.cuda.device_count()
            device_name = torch.cuda.get_device_name(0)
            print(f"✅ CUDA available - {device_count} GPU(s) detected")
            print(f"   Primary GPU: {device_name}")
            return True
        else:
            print("⚠️  CUDA not available - will use CPU")
            return False
    except ImportError:
        print("⚠️  PyTorch not installed - cannot check CUDA")
        return False


def install_requirements():
    """Install required packages."""
    print("\n📦 Installing required packages...")
    
    requirements_file = Path("requirements.txt")
    if not requirements_file.exists():
        print("❌ requirements.txt not found")
        return False
    
    try:
        subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ], check=True)
        print("✅ Requirements installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install requirements: {e}")
        return False


def setup_qdrant_docker():
    """Provide instructions for setting up Qdrant with Docker."""
    print("\n🐳 Qdrant Setup Instructions:")
    print("To run Qdrant vector database using Docker:")
    print()
    print("1. Make sure Docker is installed and running")
    print("2. Run the following command:")
    print("   docker run -p 6333:6333 qdrant/qdrant")
    print()
    print("3. Qdrant will be available at http://localhost:6333")
    print("4. You can also use the web UI at http://localhost:6333/dashboard")
    print()
    print("Alternative: Use Docker Compose")
    print("   docker-compose up -d qdrant")
    print()


def check_model_files():
    """Check if Llama model files are present."""
    model_path = Path("Llama-3.1-8B")
    
    if not model_path.exists():
        print(f"⚠️  Llama model directory not found: {model_path}")
        print("   Please download the Llama-3.1-8B model files")
        return False
    
    required_files = [
        "config.json",
        "tokenizer.json",
        "tokenizer_config.json"
    ]
    
    missing_files = []
    for file_name in required_files:
        if not (model_path / file_name).exists():
            missing_files.append(file_name)
    
    if missing_files:
        print(f"⚠️  Missing model files: {', '.join(missing_files)}")
        return False
    
    print("✅ Llama model files found")
    return True


def check_data_files():
    """Check if data files are present."""
    data_path = Path("Data")
    
    if not data_path.exists():
        print(f"⚠️  Data directory not found: {data_path}")
        print("   Please create the Data/ folder and add your PDF documents")
        return False
    
    pdf_files = list(data_path.rglob("*.pdf"))
    if not pdf_files:
        print("⚠️  No PDF files found in Data/ directory")
        print("   Please add your financial documents (PDFs) to the Data/ folder")
        return False
    
    print(f"✅ Found {len(pdf_files)} PDF files in Data/ directory")
    return True


def create_env_file_if_needed():
    """Create .env file if it doesn't exist or is empty."""
    env_file = Path(".env")
    
    if env_file.exists() and env_file.stat().st_size > 0:
        print("✅ .env file already exists")
        return True
    
    print("📝 Creating .env file with default settings...")
    
    env_content = """# Qdrant Configuration
QDRANT_HOST=localhost
QDRANT_PORT=6333
QDRANT_COLLECTION_NAME=financial_documents

# Local Model Paths
LLAMA_MODEL_PATH=./Llama-3.1-8B
EMBEDDING_MODEL_NAME=Alibaba-NLP/gte-Qwen2-7B-instruct

# Application Settings
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
MAX_TOKENS=4096
TEMPERATURE=0.1
TOP_K=5

# Logging
LOG_LEVEL=INFO
"""
    
    with open(env_file, "w") as f:
        f.write(env_content)
    
    print("✅ .env file created")
    return True


def run_system_check():
    """Run comprehensive system check."""
    print("🔍 FinBot System Check")
    print("=" * 50)
    
    checks = [
        ("Python Version", check_python_version),
        ("Environment File", create_env_file_if_needed),
        ("Model Files", check_model_files),
        ("Data Files", check_data_files),
        ("CUDA Availability", check_cuda_availability),
    ]
    
    results = []
    for check_name, check_func in checks:
        print(f"\n🔍 Checking {check_name}...")
        result = check_func()
        results.append(result)
    
    print("\n" + "=" * 50)
    print("📋 System Check Summary:")
    
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print("✅ All checks passed! System is ready.")
        return True
    else:
        print(f"⚠️  {total - passed} issue(s) found. Please address them before proceeding.")
        return False


def main():
    """Main setup function."""
    parser = argparse.ArgumentParser(description="FinBot Setup Script")
    parser.add_argument(
        "--install",
        action="store_true",
        help="Install required packages"
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Run system check"
    )
    parser.add_argument(
        "--docker-help",
        action="store_true",
        help="Show Docker setup instructions for Qdrant"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Run all setup steps"
    )
    
    args = parser.parse_args()
    
    if args.all:qwen3
        print("🚀 Running complete FinBot setup...")
        
        if not check_python_version():
            return 1
        
        create_env_file_if_needed()
        
        if not install_requirements():
            return 1
        
        setup_qdrant_docker()
        
        if run_system_check():
            print("\n🎉 FinBot setup completed successfully!")
            print("\n📚 Next steps:")
            print("1. Start Qdrant: docker run -p 6333:6333 qdrant/qdrant")
            print("2. Ingest documents: python ingest_data.py --ingest-all")
            print("3. Start chatbot: python main.py --mode web")
        else:
            return 1
    
    elif args.install:
        install_requirements()
    
    elif args.check:
        run_system_check()
    
    elif args.docker_help:
        setup_qdrant_docker()
    
    else:
        parser.print_help()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())