import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from utils.parsing import DocumentParser
from utils.chunking import create_text_chunker
from vectorstore.qdrant_client import create_qdrant_client
from embeddings.embeddings import create_embedding_service

load_dotenv()

def ingest(pdfs, collection_name="financial_documents"):
    """Ingest PDF files into the vector store."""
    print("Starting data ingestion process...")
    
    # Use FinBot's existing components
    document_parser = DocumentParser()
    text_chunker = create_text_chunker()
    embedding_service = create_embedding_service()
    embedding_dim = embedding_service.get_embedding_dimension()
    vector_client = create_qdrant_client(vector_size=embedding_dim)
    
    print(f"Using embedding model with dimension: {embedding_dim}")
    
    # Process all PDFs
    all_documents = []
    total_files_processed = 0
    
    for pdf_path in pdfs:
        if os.path.exists(pdf_path):
            print(f"Processing: {os.path.basename(pdf_path)}")
            
            try:
                parsed_doc = document_parser.parse_document(pdf_path)
                if parsed_doc["success"]:
                    # Convert to format compatible with chunker
                    doc_content = parsed_doc["content"]
                    doc_metadata = parsed_doc["metadata"]
                    
                    # Create document-like object for chunking
                    class Document:
                        def __init__(self, content, metadata):
                            self.page_content = content
                            self.metadata = metadata
                    
                    all_documents.append(Document(doc_content, doc_metadata))
                    total_files_processed += 1
                    print(f"  Successfully processed {os.path.basename(pdf_path)}")
                else:
                    print(f"  Warning: No content extracted from {os.path.basename(pdf_path)}")
            except Exception as e:
                print(f"  Error processing {os.path.basename(pdf_path)}: {e}")
        else:
            print(f"File not found: {pdf_path}")
    
    if all_documents:
        print(f"\nTotal documents to chunk: {len(all_documents)}")
        print("Creating chunks...")
        
        try:
            # Use FinBot's chunker but adapt the input
            chunks = []
            for doc in all_documents:
                # Pass page content to chunker for page number tracking
                pages_content = doc.metadata.get("pages_content", [])
                doc_chunks = text_chunker.chunk_text(doc.page_content, pages_content=pages_content)
                for chunk in doc_chunks:
                    # Create document-like object for each chunk
                    chunk_doc = Document(
                        chunk["text"], 
                        {**doc.metadata, **chunk}
                    )
                    chunks.append(chunk_doc)
            
            print(f"Created {len(chunks)} chunks from {total_files_processed} PDF files")
            
            # Prepare data for vector storage
            texts = [chunk.page_content for chunk in chunks]
            metadatas = [chunk.metadata for chunk in chunks]
            
            print("Creating embeddings and storing in vector database...")
            
            # Generate embeddings and store
            embeddings = embedding_service.encode(texts)
            vector_client.add_documents(texts, embeddings, metadatas)
            
            print(f"Successfully indexed {len(chunks)} chunks from {total_files_processed} PDF files")
            
        except Exception as e:
            print(f"Error during chunking/insertion: {e}")
            import traceback
            traceback.print_exc()
    else:
        print("No documents to index. Please check your PDF files.")


def interactive_ingestion():
    """Interactive data ingestion interface for terminal use."""
    print("\n" + "=" * 50)
    print("           DOCUMENT INGESTION")
    print("=" * 50)
    print("Process PDF documents and add them to the knowledge base.")
    
    # Get data folder from user
    default_folder = "Data"
    print(f"\nDefault data folder: {default_folder}")
    
    folder_choice = input("Press Enter to use default, or type custom path: ").strip()
    data_folder = folder_choice if folder_choice else default_folder
    
    # Check if folder exists
    if not Path(data_folder).exists():
        print(f"Error: Folder '{data_folder}' does not exist!")
        input("\nPress Enter to return to main menu...")
        return
    
    # Count PDF files
    pdf_files = list(Path(data_folder).glob("*.pdf"))
    if not pdf_files:
        print(f"No PDF files found in '{data_folder}'")
        input("\nPress Enter to return to main menu...")
        return
    
    print(f"Found {len(pdf_files)} PDF files:")
    for pdf in pdf_files:
        print(f"  - {pdf.name}")
    
    # Ask about clearing existing data
    print("\nOptions:")
    print("1. Add to existing knowledge base (incremental)")
    print("2. Clear existing data and rebuild (fresh start)")
    
    while True:
        choice = input("Choose option (1 or 2): ").strip()
        if choice in ["1", "2"]:
            break
        print("Please enter 1 or 2")
    
    clear_existing = (choice == "2")
    
    if clear_existing:
        print("Clearing existing knowledge base...")
    else:
        print("Adding to existing knowledge base...")
    
    try:
        # Convert to string paths for ingest function
        pdf_paths = [str(pdf) for pdf in pdf_files]
        ingest(pdf_paths)
        
        print(f"\nSuccess! Your documents are now available for Q&A and handout generation.")
        print(f"Documents processed: {len(pdf_files)}")
            
    except Exception as e:
        print(f"\nError during ingestion: {str(e)}")
        import traceback
        traceback.print_exc()
    
    input("\nPress Enter to return to main menu...")


if __name__ == "__main__":
    """Run data ingestion when called directly."""
    if len(sys.argv) > 1:
        # Command line arguments support
        import argparse
        parser = argparse.ArgumentParser(description="FinBot Data Ingestion")
        parser.add_argument("--data-folder", "-d", default="Data", help="Data folder path")
        parser.add_argument("--clear", "-c", action="store_true", help="Clear existing collection")
        
        args = parser.parse_args()
        
        # Check if folder exists
        if not Path(args.data_folder).exists():
            print(f"Error: Data folder '{args.data_folder}' does not exist!")
            sys.exit(1)
        
        # Get PDF files
        pdf_files = list(Path(args.data_folder).glob("*.pdf"))
        if not pdf_files:
            print(f"No PDF files found in '{args.data_folder}'")
            sys.exit(1)
        
        print(f"Found {len(pdf_files)} PDF files to process")
        
        if args.clear:
            print("Clearing existing knowledge base...")
        
        # Convert to string paths and run ingestion
        pdf_paths = [str(pdf) for pdf in pdf_files]
        try:
            ingest(pdf_paths)
            print("Terminal ingestion completed successfully!")
        except Exception as e:
            print(f"Terminal ingestion failed: {str(e)}")
            sys.exit(1)
    else:
        # Interactive mode
        interactive_ingestion()