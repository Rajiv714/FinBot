#!/usr/bin/env python3
"""
FinBot - Financial Literacy Chatbot Terminal Interface
Terminal-only interface for FinBot.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add src directory to path
src_path = str(Path(__file__).parent / "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

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
            from Chatbot import run_chatbot
            run_chatbot()
        elif choice == "2":
            from Data_ingestion import interactive_ingestion
            interactive_ingestion()
        elif choice == "3":
            from Handout_Creator import run_handout_creator
            run_handout_creator()
        elif choice == "4":
            print("\nThank you for using FinBot! Goodbye!")
            break
        else:
            print("Invalid choice. Please enter 1, 2, 3, or 4.")

def main():
    """Main entry point for terminal mode."""
    try:
        main_menu()
    except KeyboardInterrupt:
        print("\n\nGoodbye! Thanks for using FinBot!")
    except Exception as e:
        print(f"\nERROR: {str(e)}")

# Run terminal interface
if __name__ == "__main__":
    main()