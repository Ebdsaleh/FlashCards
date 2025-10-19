# src/card_manager.py
import pandas
import random
import os
import sys
from .config import FRONT_CATEGORY, BACK_CATEGORY, DEFAULT_CSV_PATH

# --- PyInstaller Resource Path Helper (Utility) ---
def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        # Use relative path when running in normal development environment
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)
# ----------------------------------------

class CardManager:
    """Manages all application data, card state, and scoring."""
    
    def __init__(self):
        self.known_words = 0
        self.unknown_words = 0
        self.front_category = FRONT_CATEGORY
        self.back_category = BACK_CATEGORY
        self.to_learn = self._load_data()
        self.current_card = {}

    def _load_data(self):
        """Loads data from the default CSV path."""
        try:
            data = pandas.read_csv(resource_path(DEFAULT_CSV_PATH))
            print(f"Loaded {len(data)} words from default path.")
        except FileNotFoundError:
            print(f"Error: Data file not found at {DEFAULT_CSV_PATH}. Starting empty.")
            return []
        except Exception as e:
            print(f"Error loading CSV: {e}")
            return []
            
        # Update categories based on the first two columns of the loaded file
        if not data.empty and len(data.columns) >= 2:
            self.front_category = data.columns[0]
            self.back_category = data.columns[1]
            
        return data.to_dict(orient='records')
        
    def load_new_data(self, file_path):
        """Loads a new CSV file selected by the user and resets the session."""
        try:
            new_data = pandas.read_csv(file_path)
            if new_data.empty or len(new_data.columns) < 2:
                print("Error: The selected file is empty or does not have at least two columns.")
                return False
                
            self.front_category = new_data.columns[0]
            self.back_category = new_data.columns[1]
            self.to_learn = new_data.to_dict(orient='records')
            self.reset_scores()
            return True

        except Exception as e:
            print(f"An error occurred while loading the file: {e}")
            return False

    def reset_scores(self):
        """Resets known and unknown scores."""
        self.known_words = 0
        self.unknown_words = 0

    def get_next_card(self):
        """Selects a random card from the list of words to learn."""
        if not self.to_learn:
            return None
        self.current_card = random.choice(self.to_learn)
        return self.current_card

    def mark_known(self):
        """Increments known score and removes the current card from the learning list."""
        self.known_words += 1
        if self.current_card in self.to_learn:
            self.to_learn.remove(self.current_card)

    def mark_unknown(self):
        """Increments the unknown score."""
        self.unknown_words += 1
