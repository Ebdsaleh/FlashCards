# main.py
# This is the is the entry point of the application. 

from src.card_manager import CardManager
from src.flashcard_app import FlashCardApp

def main():
    """Initializes the data manager and starts the Tkinter application."""
    print("--- Starting Flash Card Study Tool ---")
    
    # 1. Initialize Core Logic (Data & State Management)
    data_manager = CardManager()
    
    # 2. Initialize and Run UI (Tkinter App)
    app = FlashCardApp(data_manager)
    app.mainloop()

if __name__ == '__main__':
    main()