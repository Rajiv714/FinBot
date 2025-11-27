#!/usr/bin/env python3
"""
FinBot - Financial Literacy Chatbot Terminal Interface
Terminal-only interface with direct access to core services (maintains terminal privileges)
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add paths to sys.path
src_path = str(Path(__file__).parent / "src")
backend_path = str(Path(__file__).parent / "backend")
if src_path not in sys.path:
    sys.path.insert(0, src_path)
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

def main_menu():
    """Display main menu and handle user choices."""
    while True:
        print("\n" + "=" * 40)
        print("           MAIN MENU")
        print("=" * 40)
        print("1. Interactive Chat")
        print("2. Ingest Financial Documents")
        print("3. Generate Educational Handout")
        print("4. Exit")
        print("=" * 40)
        
        choice = input("Enter your choice (1-4): ").strip()
        
        if choice == "1":
            run_chatbot_terminal()
        elif choice == "2":
            run_ingestion_terminal()
        elif choice == "3":
            run_handout_creator_terminal()
        elif choice == "4":
            print("\nThank you for using FinBot! Goodbye!")
            break
        else:
            print("Invalid choice. Please enter 1, 2, 3, or 4.")


def run_chatbot_terminal():
    """Run chatbot with direct service access (terminal privileges)"""
    from services.chatbot_service import get_chatbot_service
    
    print("\n" + "=" * 60)
    print("           FINANCIAL CHATBOT (Terminal Mode)")
    print("=" * 60)
    print("Ask questions about financial topics. Type 'back' to return.\n")
    
    chatbot = get_chatbot_service()
    
    while True:
        query = input("\nYou: ").strip()
        
        if query.lower() in ['back', 'exit', 'quit']:
            break
        
        if not query:
            continue
        
        try:
            result = chatbot.chat_query(query=query, include_context=True)
            
            if result.get("success"):
                print(f"\nBot: {result['answer']}")
                
                # Show source count if available
                sources = result.get('sources', [])
                if sources:
                    print(f"\n[Retrieved from {len(sources)} source(s)]")
            else:
                print(f"\nBot: Error - {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            print(f"\nBot: I encountered an error: {str(e)}")


def run_ingestion_terminal():
    """Run document ingestion with direct service access (terminal privileges)"""
    from services.ingestion_service import get_ingestion_service
    
    print("\n" + "=" * 60)
    print("           DOCUMENT INGESTION (Terminal Mode)")
    print("=" * 60)
    
    # Get data folder
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
    
    print(f"\nFound {len(pdf_files)} PDF files:")
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
    
    try:
        print(f"\n{'Clearing and rebuilding' if clear_existing else 'Adding to'} knowledge base...")
        
        ingestion = get_ingestion_service()
        result = ingestion.ingest_documents(
            data_folder=data_folder,
            clear_existing=clear_existing
        )
        
        if result['success']:
            print(f"\n✓ Success! Processed {result['files_processed']} files")
            print(f"  Created {result['total_chunks']} chunks")
            print(f"  Time: {result['execution_time']:.2f}s")
        else:
            print(f"\n✗ Ingestion failed")
            if result.get('errors'):
                print("Errors:")
                for error in result['errors']:
                    print(f"  - {error}")
        
    except Exception as e:
        print(f"\n✗ Error during ingestion: {str(e)}")
    
    input("\nPress Enter to return to main menu...")


def run_handout_creator_terminal():
    """Run handout creator with direct service access (terminal privileges)"""
    from services.handout_service import get_handout_service
    
    print("\n" + "=" * 60)
    print("           HANDOUT CREATOR (Terminal Mode)")
    print("=" * 60)
    print("Generate 1000-1200 word educational handouts on financial topics")
    
    print("\nSuggested topics:")
    print("- Mutual Funds")
    print("- Personal Finance Basics")
    print("- Investment Strategies")
    print("- Retirement Planning")
    print("- Tax Planning")
    
    topic = input("\nEnter handout topic (or 'back' to return): ").strip()
    
    if topic.lower() in ['back', 'exit', 'quit']:
        return
    
    if not topic:
        print("Please enter a valid topic")
        input("\nPress Enter to return to main menu...")
        return
    
    # Ask about Google search
    use_google = input("\nInclude latest news via Google search? (y/n, default=y): ").strip().lower()
    include_google = use_google != 'n'
    
    # Target length
    print("\nTarget word count:")
    print("1. 1000 words")
    print("2. 1100 words")
    print("3. 1200 words (default)")
    
    length_choice = input("Choose (1-3, default=3): ").strip()
    target_length = {
        '1': 1000,
        '2': 1100,
        '3': 1200
    }.get(length_choice, 1200)
    
    try:
        print(f"\nGenerating {target_length}-word handout on '{topic}'...")
        print("This may take 30-60 seconds...")
        
        handout_service = get_handout_service()
        result = handout_service.create_handout(
            topic=topic,
            target_length=target_length,
            include_google_search=include_google,
            search_depth="standard"
        )
        
        if result['success']:
            print(f"\n✓ Handout created successfully!")
            print(f"  Word count: {result['word_count']}")
            print(f"  Time: {result['total_execution_time']:.2f}s")
            print(f"  Saved to: {result['filepath']}")
            
            # Show agent breakdown
            print(f"\n  Agent Execution:")
            for agent in result.get('agent_outputs', []):
                status = "✓" if agent['success'] else "✗"
                print(f"    {status} {agent['agent_name']}: {agent['execution_time']:.2f}s ({agent['word_count']} words)")
        else:
            print(f"\n✗ Handout creation failed: {result.get('error', 'Unknown error')}")
        
    except Exception as e:
        print(f"\n✗ Error creating handout: {str(e)}")
    
    input("\nPress Enter to return to main menu...")


def main():
    """Main entry point for terminal mode."""
    try:
        print("\n" + "=" * 60)
        print("  FINBOT - Financial Literacy Assistant (Terminal Mode)")
        print("=" * 60)
        print("  Direct access to all core services with full privileges")
        print("=" * 60)
        
        main_menu()
    except KeyboardInterrupt:
        print("\n\nGoodbye! Thanks for using FinBot!")
    except Exception as e:
        print(f"\nERROR: {str(e)}")
        import traceback
        traceback.print_exc()


# Run terminal interface
if __name__ == "__main__":
    main()