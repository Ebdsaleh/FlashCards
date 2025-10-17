# main.py
# This is the is the entry point of the application. 

from tkinter import *
from tkinter import filedialog
import pandas
import time
import random


BACKGROUND_COLOR = "#B1DDC6"
known_words = 0
unknown_words = 0
time_limit = 3000  # Time limit in miliseconds.
card_front_category = "Filipino"
card_back_category = "English"
current_card = {}
total_cards = 0
# Load initial data
try:
    data = pandas.read_csv("data/filipino_english_words.csv")
except FileNotFoundError:
    print("Error: Default data file not found. Starting with empty set.")
    data = pandas.DataFrame(columns=[card_front_category, card_back_category])

to_learn = data.to_dict(orient='records')
print(to_learn)

# --- Score Label References (Declared globally) ---
# Will be defined later in the 'Score Setup' section
known_label = None 
unknown_label = None
# -------------------------------------------------


# --- Function Placeholders (Adding this back for clean button commands) ---
# --- Menu and Data Loading Functions ---
def load_new_data():
    """Opens a file dialog, loads a new CSV file, and restarts the flashcard session."""
    global to_learn, data, card_front_category, card_back_category
    
    # 1. Open File Dialog and select CSV
    file_path = filedialog.askopenfilename(
        defaultextension=".csv",
        filetypes=[("CSV files", "*.csv")]
    )

    if not file_path:
        # User cancelled the dialog
        return

    try:
        # 2. Read the new data
        new_data = pandas.read_csv(file_path)
        if new_data.empty or len(new_data.columns) < 2:
            print("Error: The selected file is empty or does not have at least two columns.")
            return
        # 3. Update Categories based on the first two columns of the new file
        card_front_category = new_data.columns[0]
        card_back_category = new_data.columns[1]
        # 4. Convert and Reset Session
        to_learn = new_data.to_dict(orient='records')
        print(f"Successfully loaded {len(to_learn)} pairs. Categories: {card_front_category} / {card_back_category}")
        
        # Reset the score and restart the card flow
        reset_session()

    except Exception as e:
        print(f"An error occurred while loading the file: {e}")


def reset_session():
    """Resets scores and restarts the card cycle with the current data."""
    global known_words, unknown_words
    known_words = 0
    unknown_words = 0
    update_score_labels()
    next_card()


def create_menu_bar():
    """Creates the main menu bar and adds the File menu."""
    menu_bar = Menu(window)
    window.config(menu=menu_bar)

    # File Menu
    file_menu = Menu(menu_bar, tearoff=0)
    menu_bar.add_cascade(label="File", menu=file_menu)
    
    # Add commands to the File Menu
    file_menu.add_command(label="Load CSV", command=load_new_data)
    file_menu.add_separator()
    file_menu.add_command(label="Exit", command=window.quit)


def update_score_labels():
    """Updates the text of the known and unknown score labels."""
    known_label.config(text=f"Known: {known_words}")
    unknown_label.config(text=f"Unknown: {unknown_words}")


def next_card():
    global current_card, flip_timer, total_cards
    # Check if there is data to learn before proceeding
    if not to_learn:
        canvas.itemconfig(card_title, text="No Data", fill="red")
        canvas.itemconfig(card_word, text="Please load a CSV file.", fill="red")
        window.after_cancel(flip_timer)
        return
    window.after_cancel(flip_timer)
    total_cards += 1
    canvas.itemconfig(card_background, image=card_front_image)
    current_card = random.choice(to_learn)
    canvas.itemconfig(card_title, text=card_front_category, fill="black")
    canvas.itemconfig(card_word, text=current_card[card_front_category], fill="black")
    flip_timer = window.after(time_limit, func=flip_card)
    


def flip_card():
    print("Card has been flipped.")
    if current_card != {}:
        canvas.itemconfig(card_background, image=card_back_image)
        canvas.itemconfig(card_title, text=card_back_category, fill="white")
        canvas.itemconfig(card_word, text=current_card[card_back_category], fill="white")

def next_card_unknown():
    global unknown_words
    print("Unknown button clicked. Show next card.")
    unknown_words += 1
    print("Unknown words: ", unknown_words)
    update_score_labels()
    next_card()
    

def next_card_known():
    global known_words
    print("Known button clicked. Show next card.")
    known_words += 1
    print("known words: ", known_words)
    update_score_labels()
    next_card()
# --------------------------------------------------------


# --- Window instantiation and configuration ---

window = Tk()
window.title("Flash Card Study Tool")
# --- Set Window Size and Resizability ---
# Set the initial size to 860x700 pixels
window.geometry("860x700")
# Allow the window to be resizable (True for width, True for height)
window.resizable(True, True)
window.config(padx=50, pady=50, bg=BACKGROUND_COLOR,)
flip_timer = window.after(time_limit, func=flip_card)
# --- Create the Menu Bar ---
create_menu_bar()
# --- End of Window instantiation and configuration ---

# --- Canvas setup (Row 1) ---
canvas = Canvas(width=800, height=526)
canvas_center_x = 400
canvas_center_y = 263
card_front_image = PhotoImage(file="images/card_front.png")
card_back_image = PhotoImage(file="images/card_back.png")
canvas.front_of_card_image_ref = card_front_image
canvas.back_of_card_image_ref = card_back_image
card_background = canvas.create_image(canvas_center_x, canvas_center_y, image=canvas.front_of_card_image_ref)
title_text_pos = (400, 150)
card_text_pos = (canvas_center_x, canvas_center_y)
card_title = canvas.create_text(title_text_pos, text="Title", font=("Airal", 40, "italic"))
card_word = canvas.create_text(card_text_pos, text="Word", font=("Arial", 60, "bold"))
canvas.config(bg=BACKGROUND_COLOR, highlightthickness=0)
canvas.grid(row=1, column=0, columnspan=2)
# --- End of Canvas setup ---

# --- Score setup (Row 0) ---

unknown_label = Label(text=f"Unknown: {unknown_words}", bg=BACKGROUND_COLOR, font=("Arial", 16))
unknown_label.grid(row=0, column=0, sticky="W", padx=5) # sticky="W" aligns to the left

known_label = Label(text=f"Known: {known_words}", bg=BACKGROUND_COLOR, font=("Arial", 16))
known_label.grid(row=0, column=0, sticky="E", padx=5) # sticky="E" aligns to the right
# --- End of Score setup ---

# --- Button setup (Row 2) ---
cross_image = PhotoImage(file="images/wrong.png")
unknown_button = Button(image=cross_image, highlightthickness=0, command=next_card_unknown)
unknown_button.grid(row=2, column=0)

tick_image = PhotoImage(file="images/right.png")
known_button = Button(image=tick_image, highlightthickness=0, command=next_card_known)
known_button.grid(row=2, column=1)


def main():
    print("Flash Cards Study Tool")
    next_card()
    
    window.mainloop()

if __name__ == '__main__':
    main()
