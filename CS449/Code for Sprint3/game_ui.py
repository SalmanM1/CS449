# game_ui.py

import tkinter as tk
from tkinter import messagebox
from game import SimpleGame, GeneralGame

class GameUI:
    """Class to handle the GUI of the SOS game."""

    def __init__(self):
        """Initialize the GUI."""
        self.root = tk.Tk()
        self.root.title("SOS Game")

        self.game = None
        self.selected_letter = None  # To store the selected letter
        self.letter_buttons = {}  # To store letter buttons for enabling/disabling
        self.cell_ids = {}  # Mapping from (row, col) to rectangle and text IDs

        self.create_widgets()
        self.root.mainloop()

    def create_widgets(self):
        """Create and place GUI widgets."""
        # Frame for game options
        options_frame = tk.Frame(self.root)
        options_frame.pack(pady=10)

        # Font settings for labels and buttons
        label_font = ('Arial', 12)
        button_font = ('Arial', 12)

        # Board size input
        tk.Label(options_frame, text="Board Size:", font=label_font).grid(row=0, column=0, padx=5)
        self.board_size_entry = tk.Entry(options_frame, width=5, font=label_font)
        self.board_size_entry.grid(row=0, column=1, padx=5)

        # Game mode selection
        tk.Label(options_frame, text="Game Mode:", font=label_font).grid(row=0, column=2, padx=5)
        self.game_mode_var = tk.StringVar(value='simple')
        tk.Radiobutton(
            options_frame, text='Simple', variable=self.game_mode_var, value='simple',
            font=label_font
        ).grid(row=0, column=3, padx=5)
        tk.Radiobutton(
            options_frame, text='General', variable=self.game_mode_var, value='general',
            font=label_font
        ).grid(row=0, column=4, padx=5)

        # Start game button
        start_button = tk.Button(
            options_frame, text="Start New Game", command=self.start_game, font=button_font
        )
        start_button.grid(row=0, column=5, padx=10)

        # Frame for the game area
        self.game_frame = tk.Frame(self.root)
        self.game_frame.pack()

        # Placeholder for the turn label (will be created after the game starts)
        self.turn_label = None

    def start_game(self):
        """Start a new game with the selected options."""
        try:
            board_size = int(self.board_size_entry.get())
            if board_size <= 2:
                raise ValueError
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid board size (n > 2).")
            return

        game_mode = self.game_mode_var.get()
        if game_mode == 'simple':
            self.game = SimpleGame(board_size)
        else:
            self.game = GeneralGame(board_size)
        self.game.start_new_game()
        self.selected_letter = None  # Reset the selected letter
        self.create_game_area()
        self.update_turn_label()

    def create_game_area(self):
        """Create the game board and letter selection buttons."""
        # Clear previous game area if any
        for widget in self.game_frame.winfo_children():
            widget.destroy()

        # Create a frame for the letter selection buttons
        letter_frame = tk.Frame(self.game_frame)
        letter_frame.pack(side=tk.LEFT, padx=10)

        # Letter selection buttons
        self.letter_buttons['S'] = tk.Button(
            letter_frame,
            text='S',
            font=('Arial', 14),
            width=4,
            command=lambda: self.select_letter('S')
        )
        self.letter_buttons['S'].pack(pady=5)

        self.letter_buttons['O'] = tk.Button(
            letter_frame,
            text='O',
            font=('Arial', 14),
            width=4,
            command=lambda: self.select_letter('O')
        )
        self.letter_buttons['O'].pack(pady=5)

        # Create the board canvas
        self.board_canvas = tk.Canvas(self.game_frame)
        self.board_canvas.pack(side=tk.LEFT)

        self.create_board()

        # Create the turn label after the game starts
        if self.turn_label is None:
            self.turn_label = tk.Label(self.root, text="", font=('Arial', 14))
            self.turn_label.pack(pady=5)
        else:
            # Reset the turn label
            self.turn_label.config(text="")

    def select_letter(self, letter):
        """Handle letter selection."""
        self.selected_letter = letter
        # Update button states to show which letter is selected
        for ltr, btn in self.letter_buttons.items():
            if ltr == letter:
                btn.config(relief=tk.SUNKEN)
            else:
                btn.config(relief=tk.RAISED)

    def create_board(self):
        """Create the game board cells."""
        self.cell_ids = {}
        self.button_positions = {}

        board_size = self.game.board_size
        cell_size = 60  # Size of each cell
        for row in range(board_size):
            for col in range(board_size):
                x1 = col * cell_size
                y1 = row * cell_size
                x2 = x1 + cell_size
                y2 = y1 + cell_size
                # Draw rectangle
                rect_id = self.board_canvas.create_rectangle(
                    x1, y1, x2, y2, fill='white', outline='black'
                )
                # Draw text (initially empty)
                text_id = self.board_canvas.create_text(
                    x1 + cell_size / 2, y1 + cell_size / 2, text='', font=('Arial', 24)
                )
                # Store IDs
                self.cell_ids[(row, col)] = (rect_id, text_id)
                self.button_positions[(row, col)] = (x1 + cell_size / 2, y1 + cell_size / 2)
                # Bind click event to rectangle
                self.board_canvas.tag_bind(rect_id, '<Button-1>', lambda event, r=row, c=col: self.on_cell_click(r, c))
                self.board_canvas.tag_bind(text_id, '<Button-1>', lambda event, r=row, c=col: self.on_cell_click(r, c))
        # Adjust canvas size based on board size
        canvas_width = board_size * cell_size
        canvas_height = board_size * cell_size
        self.board_canvas.config(width=canvas_width, height=canvas_height)

    def on_cell_click(self, row, col):
        """Handle cell click events."""
        if self.game.game_over:
            messagebox.showinfo("Game Over", "The game is over. Please start a new game.")
            return

        if not self.game.is_move_valid(row, col):
            messagebox.showwarning("Invalid Move", "This cell is already occupied.")
            return

        if self.selected_letter is None:
            messagebox.showwarning("No Letter Selected", "Please select 'S' or 'O' before making a move.")
            return

        letter = self.selected_letter
        move_made = self.game.make_move(row, col, letter)
        if move_made:
            self.update_board()
            self.selected_letter = None  # Reset selected letter after move
            # Reset the letter button states
            for btn in self.letter_buttons.values():
                btn.config(relief=tk.RAISED)
            if self.game.check_game_over():
                self.update_turn_label(game_over=True)
                if self.game.winner == 'Draw':
                    messagebox.showinfo("Game Over", "The game is over. It's a draw!")
                else:
                    messagebox.showinfo("Game Over", f"The game is over. {self.game.winner} Player wins!")
            else:
                self.update_turn_label()
        else:
            messagebox.showwarning("Invalid Move", "Cannot make this move.")

    def update_board(self):
        """Update the board cells to reflect the current game state."""
        for row in range(self.game.board_size):
            for col in range(self.game.board_size):
                cell = self.game.board[row][col]
                rect_id, text_id = self.cell_ids[(row, col)]
                if cell is not None:
                    letter = cell['letter']
                    player = cell['player']
                    color = player.lower()
                    # Update text
                    self.board_canvas.itemconfig(text_id, text=letter, fill=color)
                    # Disable further clicks on this cell by unbinding events
                    self.board_canvas.tag_unbind(rect_id, '<Button-1>')
                    self.board_canvas.tag_unbind(text_id, '<Button-1>')
                else:
                    self.board_canvas.itemconfig(text_id, text='')

        self.draw_sos_sequences()

    def update_turn_label(self, game_over=False):
        """Update the turn label to indicate whose turn it is."""
        if game_over:
            if self.game.winner == 'Draw':
                self.turn_label.config(text="Game Over: Draw", fg='black')
            else:
                self.turn_label.config(text=f"Game Over: {self.game.winner} Player Wins!", fg=self.game.winner.lower())
        else:
            player = self.game.current_player
            self.turn_label.config(text=f"Turn: {player} Player", fg=player.lower())

    def draw_sos_sequences(self):
        """Draw lines over the SOS sequences."""
        # Clear previous lines
        self.board_canvas.delete('sos_line')

        sequences = []
        # Collect sequences with their associated colors
        for seq in self.game.blue_sequences:
            sequences.append((seq, 'blue'))
        for seq in self.game.red_sequences:
            sequences.append((seq, 'red'))

        for seq, color in sequences:
            start, end = seq
            start_pos = self.button_positions[start]
            end_pos = self.button_positions[end]

            # Draw the line on the canvas
            self.board_canvas.create_line(
                start_pos[0], start_pos[1], end_pos[0], end_pos[1],
                fill=color,
                width=3,
                tags='sos_line'
            )

if __name__ == '__main__':
    GameUI()