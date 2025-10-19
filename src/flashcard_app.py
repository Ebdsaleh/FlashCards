# src/flashcard_app
from tkinter import *
from tkinter import filedialog
from tkinter import colorchooser
import random

# Import constants and logic manager
from .config import (
    TIME_LIMIT_MS, DEFAULT_FONT_SIZE, BACKGROUND_COLOR, 
    CARD_FRONT_COLOR, CARD_BACK_COLOR, CARD_BACK_TEXT_COLOR
)
from .card_manager import CardManager, resource_path


class FlashCardApp(Tk):
    """The main Tkinter application class for the Flash Card Tool."""

    def __init__(self, data_manager):
        super().__init__()
        self.data_manager = data_manager
        
        # --- Config Variables (Can be updated via settings) ---
        self.time_limit = TIME_LIMIT_MS
        self.current_font_size = DEFAULT_FONT_SIZE
        self.bg_color = BACKGROUND_COLOR
        self.card_front_color = CARD_FRONT_COLOR
        self.card_back_color = CARD_BACK_COLOR
        
        # --- UI Element References ---
        self.known_label = None
        self.unknown_label = None
        self.card_rectangle = None
        self.card_image_overlay = None
        self.card_title = None
        self.card_word = None
        
        # --- Timers and Resources ---
        self.flip_timer = self.after(self.time_limit, func=lambda: None)
        self.card_front_image = PhotoImage(file=resource_path("images/card_front.png"))
        self.card_back_image = PhotoImage(file=resource_path("images/card_back.png"))
        
        # --- Initial Setup ---
        self.setup_window()
        self.create_menu_bar()
        self.setup_canvas()
        self.setup_score_labels()
        self.setup_buttons()
        
        # Start the first card
        self.next_card()

    def setup_window(self):
        """Configures the main window properties."""
        self.title("Flash Card Study Tool")
        self.geometry("860x700")
        self.resizable(True, True)
        self.config(padx=50, pady=50, bg=self.bg_color)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

    def setup_canvas(self):
        """Creates the main card canvas and its elements."""
        self.canvas = Canvas(width=800, height=526, bg=self.bg_color, highlightthickness=0)
        
        canvas_center_x = 400
        canvas_center_y = 263

        # 1. Colored Rectangle (the actual card background/color)
        self.card_rectangle = self.canvas.create_rectangle(
            0, 0, 800, 526, 
            fill=self.card_front_color, 
            outline=""
        )

        # 2. Card Image Overlay (transparent borders/details)
        self.card_image_overlay = self.canvas.create_image(
            canvas_center_x, canvas_center_y, 
            image=self.card_front_image
        )

        # 3. Text Elements
        self.card_title = self.canvas.create_text(
            400, 150, 
            text="Title", 
            font=("Airal", 40, "italic")
        )
        self.card_word = self.canvas.create_text(
            canvas_center_x, canvas_center_y, 
            text="Word", 
            font=("Arial", self.current_font_size, "bold")
        )

        self.canvas.grid(row=1, column=0, columnspan=2)

    def setup_score_labels(self):
        """Creates and places the Known/Unknown score labels."""
        self.unknown_label = Label(text="Unknown: 0", bg=self.bg_color, font=("Arial", 16))
        self.unknown_label.grid(row=0, column=0, sticky="W", padx=5) 

        self.known_label = Label(text="Known: 0", bg=self.bg_color, font=("Arial", 16))
        self.known_label.grid(row=0, column=1, sticky="E", padx=5)
        
        # Set instance references for easy global access
        self.data_manager.known_label = self.known_label
        self.data_manager.unknown_label = self.unknown_label

    def setup_buttons(self):
        """Creates and places the Known and Unknown buttons."""
        cross_image = PhotoImage(file=resource_path("images/wrong.png"))
        self.unknown_button = Button(image=cross_image, highlightthickness=0, command=self.next_card_unknown)
        self.unknown_button.image = cross_image # Keep reference
        self.unknown_button.grid(row=2, column=0, pady=20)

        tick_image = PhotoImage(file=resource_path("images/right.png"))
        self.known_button = Button(image=tick_image, highlightthickness=0, command=self.next_card_known)
        self.known_button.image = tick_image # Keep reference
        self.known_button.grid(row=2, column=1, pady=20)

    # --- Menu Bar ---
    
    def create_menu_bar(self):
        """Creates the main menu bar."""
        menu_bar = Menu(self)
        self.config(menu=menu_bar)

        file_menu = Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Load CSV", command=self.load_new_data)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.quit)

        edit_menu = Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Change Settings", command=self.open_settings_dialog)

    # --- Settings Dialog ---

    def choose_color(self, color_preview_label):
        """Opens the color chooser and updates the preview label text/color."""
        color_code = colorchooser.askcolor(title="Choose Color")
        if color_code[1]: 
            hex_code = color_code[1]
            # Determine contrasting foreground color for readability
            fg_color = "#000000" if sum(int(hex_code[i:i+2], 16) for i in (1, 3, 5)) / 3 > 128 else "#ffffff"
            
            color_preview_label.config(text=hex_code, bg=hex_code, fg=fg_color)
            color_preview_label.selected_color = hex_code # Store color in custom attribute

    def create_color_chooser_row(self, parent_window, label_text, default_color, row_index):
        """Helper function to create a color chooser row."""
        Label(parent_window, text=label_text, bg=self.bg_color, font=("Arial", 12)).grid(row=row_index, column=0, pady=5, sticky="w")
        
        color_preview = Label(parent_window, text=default_color, width=10, bg=default_color, relief="ridge", font=("Arial", 10, "bold"))
        color_preview.grid(row=row_index, column=1, pady=5, padx=(0, 5), sticky="w")
        color_preview.selected_color = default_color
        
        color_button = Button(parent_window, text="Change", 
                              command=lambda: self.choose_color(color_preview),
                              font=("Arial", 10))
        color_button.grid(row=row_index, column=1, pady=5, sticky="e")
        
        return color_preview

    def apply_settings(self, new_time_ms, new_font_size_pt, bg_hex, front_hex, back_hex, settings_window):
        """Validates inputs, updates global settings, and applies changes to the UI."""
        try:
            # 1. Update Time Limit and Font Size
            self.time_limit = max(500, int(new_time_ms))
            self.current_font_size = max(10, int(new_font_size_pt))

            # 2. Update and Apply Colors
            self.bg_color = bg_hex
            self.card_front_color = front_hex
            self.card_back_color = back_hex

            self.config(bg=self.bg_color)
            self.canvas.config(bg=self.bg_color)
            self.unknown_label.config(bg=self.bg_color)
            self.known_label.config(bg=self.bg_color)
            
            # 3. Apply Font Size
            self.canvas.itemconfig(self.card_word, font=("Arial", self.current_font_size, "bold"))
            
            # 4. Close the settings window
            settings_window.destroy()

            # 5. Restart the card cycle to apply time limit and initial card color
            self.after_cancel(self.flip_timer)
            self.next_card() 

        except ValueError:
            Label(settings_window, text="Invalid input. Please enter whole numbers.", 
                  fg="red", bg=self.bg_color).grid(row=6, column=0, columnspan=2, pady=10)


    def open_settings_dialog(self):
        """Creates a modal window for changing all settings."""
        settings_window = Toplevel(self)
        settings_window.title("App Settings")
        settings_window.config(padx=20, pady=20, bg=self.bg_color)
        settings_window.grab_set() 
        
        # Row 0: Time Limit
        Label(settings_window, text="Card Flip Delay (ms):", bg=self.bg_color, font=("Arial", 12)).grid(row=0, column=0, pady=5, sticky="w")
        time_entry = Entry(settings_window, width=10, font=("Arial", 12))
        time_entry.insert(0, str(self.time_limit))
        time_entry.grid(row=0, column=1, pady=5)

        # Row 1: Font Size
        Label(settings_window, text="Card Word Font Size (pt):", bg=self.bg_color, font=("Arial", 12)).grid(row=1, column=0, pady=5, sticky="w")
        font_entry = Entry(settings_window, width=10, font=("Arial", 12))
        font_entry.insert(0, str(self.current_font_size))
        font_entry.grid(row=1, column=1, pady=5)
        
        # Color Chooser Rows
        bg_preview = self.create_color_chooser_row(settings_window, "Main Background Color:", self.bg_color, 2)
        front_preview = self.create_color_chooser_row(settings_window, "Card Front Color:", self.card_front_color, 3)
        back_preview = self.create_color_chooser_row(settings_window, "Card Back Color:", self.card_back_color, 4)
        
        # Row 5: Apply Button
        apply_button = Button(settings_window, text="Apply Settings", 
                              command=lambda: self.apply_settings(
                                  time_entry.get(), 
                                  font_entry.get(), 
                                  bg_preview.selected_color, 
                                  front_preview.selected_color, 
                                  back_preview.selected_color, 
                                  settings_window
                              ),
                              font=("Arial", 12, "bold"), bg="#FFFFFF", relief="flat")
        apply_button.grid(row=5, column=0, columnspan=2, pady=20)


    # --- Card Actions ---

    def update_score_labels(self):
        """Updates the score labels using data from the manager."""
        self.known_label.config(text=f"Known: {self.data_manager.known_words}")
        self.unknown_label.config(text=f"Unknown: {self.data_manager.unknown_words}")

    def update_card_rectangle_color(self, color_hex):
        """Updates the fill color of the canvas rectangle."""
        self.canvas.itemconfig(self.card_rectangle, fill=color_hex)

    def next_card(self):
        """Fetches the next card and updates the canvas."""
        self.after_cancel(self.flip_timer)
        next_card_data = self.data_manager.get_next_card()

        if next_card_data is None:
            self.canvas.itemconfig(self.card_title, text="FINISH!", fill="green")
            self.canvas.itemconfig(self.card_word, text="All words learned!", fill="green")
            return
            
        # Set card front appearance
        self.update_card_rectangle_color(self.card_front_color)
        self.canvas.itemconfig(self.card_image_overlay, image=self.card_front_image)
        self.canvas.itemconfig(self.card_title, text=self.data_manager.front_category, fill="black")
        self.canvas.itemconfig(self.card_word, text=next_card_data[self.data_manager.front_category], fill="black")
        
        # Start the flip timer
        self.flip_timer = self.after(self.time_limit, func=self.flip_card)

    def flip_card(self):
        """Flips the card to show the back side (translation)."""
        card = self.data_manager.current_card
        if card:
            # Set card back appearance
            self.update_card_rectangle_color(self.card_back_color)
            self.canvas.itemconfig(self.card_image_overlay, image=self.card_back_image)
            
            # Use appropriate text color for the back (e.g., white if card back is dark)
            self.canvas.itemconfig(self.card_title, text=self.data_manager.back_category, fill=CARD_BACK_TEXT_COLOR)
            self.canvas.itemconfig(self.card_word, text=card[self.data_manager.back_category], fill=CARD_BACK_TEXT_COLOR)

    def next_card_unknown(self):
        """Handles 'Unknown' button click."""
        self.data_manager.mark_unknown()
        self.update_score_labels()
        self.next_card()
        
    def next_card_known(self):
        """Handles 'Known' button click."""
        self.data_manager.mark_known()
        self.update_score_labels()
        self.next_card()
        
    def load_new_data(self):
        """Opens file dialog and loads new data via the manager."""
        file_path = filedialog.askopenfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])

        if file_path:
            if self.data_manager.load_new_data(file_path):
                self.update_score_labels()
                self.next_card()


if __name__ == '__main__':
    # 1. Initialize the Data/Logic Manager
    data_manager = CardManager()
    
    # 2. Initialize and run the UI
    app = FlashCardApp(data_manager)
    app.mainloop()
