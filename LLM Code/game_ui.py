# game_ui.py

import tkinter as tk
from tkinter import messagebox
from game import SimpleGame, GeneralGame
import threading
import time
import json
from tkinter import filedialog

# LLM Imports
import openai
import os

# API Key
openai.api_key = "PLACE KEY HERE"

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

        self.player_types = {'Blue': 'Human', 'Red': 'Human'}  # Default player types
        self.is_recording = False  # To track if recording is enabled
        self.recorded_moves = []   # To store recorded moves
        self.is_replaying = False  # To track if replaying is in progress

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

        # Blue Player selection
        tk.Label(options_frame, text="Blue Player:", font=label_font, fg='blue').grid(row=1, column=0, padx=5, sticky='w')
        self.blue_player_var = tk.StringVar(value='Human')
        tk.Radiobutton(
            options_frame, text='Human', variable=self.blue_player_var, value='Human',
            font=label_font
        ).grid(row=1, column=1, padx=5)
        tk.Radiobutton(
            options_frame, text='Computer', variable=self.blue_player_var, value='Computer',
            font=label_font
        ).grid(row=1, column=2, padx=5)

        # Red Player selection
        tk.Label(options_frame, text="Red Player:", font=label_font, fg='red').grid(row=2, column=0, padx=5, sticky='w')
        self.red_player_var = tk.StringVar(value='Human')
        tk.Radiobutton(
            options_frame, text='Human', variable=self.red_player_var, value='Human',
            font=label_font
        ).grid(row=2, column=1, padx=5)
        tk.Radiobutton(
            options_frame, text='Computer', variable=self.red_player_var, value='Computer',
            font=label_font
        ).grid(row=2, column=2, padx=5)

        # Record Game checkbox
        self.record_var = tk.BooleanVar()
        self.record_checkbox = tk.Checkbutton(
            options_frame, text="Record Game", variable=self.record_var, font=label_font
        )
        self.record_checkbox.grid(row=3, column=0, padx=5, sticky='w')

        # Replay Game button
        replay_button = tk.Button(
            options_frame, text="Replay Game", command=self.replay_game, font=button_font
        )
        replay_button.grid(row=3, column=1, padx=10)

        # LLM Opponent checkbox
        self.llm_var = tk.BooleanVar()
        self.llm_checkbox = tk.Checkbutton(
            options_frame, text="Use LLM Opponent", variable=self.llm_var, font=label_font
        )
        self.llm_checkbox.grid(row=3, column=2, padx=5, sticky='w')

        # Frame for the game area
        self.game_frame = tk.Frame(self.root)
        self.game_frame.pack()

        # Placeholder for the turn label
        self.turn_label = None

    def start_game(self):
        """Start a new game with the selected options."""
        if self.is_replaying:
            messagebox.showwarning("Replay in Progress", "Cannot start a new game during replay.")
            return

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

        # Set player types
        self.player_types['Blue'] = self.blue_player_var.get()
        self.player_types['Red'] = self.red_player_var.get()

        # Set recording state
        self.is_recording = self.record_var.get()
        self.recorded_moves = []

        self.create_game_area()
        self.update_turn_label()
        self.process_computer_turn()  # Check if the first move is by computer

    def create_game_area(self):
        """Create the game board and letter selection buttons."""
        # Clear previous game area if any
        for widget in self.game_frame.winfo_children():
            widget.destroy()

        self.letter_frame = tk.Frame(self.game_frame)
        self.letter_frame.pack(side=tk.LEFT, padx=10)

        self.letter_buttons['S'] = tk.Button(
            self.letter_frame,
            text='S',
            font=('Arial', 14),
            width=4,
            command=lambda: self.select_letter('S')
        )
        self.letter_buttons['S'].pack(pady=5)

        self.letter_buttons['O'] = tk.Button(
            self.letter_frame,
            text='O',
            font=('Arial', 14),
            width=4,
            command=lambda: self.select_letter('O')
        )
        self.letter_buttons['O'].pack(pady=5)

        self.board_canvas = tk.Canvas(self.game_frame)
        self.board_canvas.pack(side=tk.LEFT)

        self.create_board()

        if self.turn_label is None:
            self.turn_label = tk.Label(self.root, text="", font=('Arial', 14))
            self.turn_label.pack(pady=5)
        else:
            # Reset the turn label
            self.turn_label.config(text="")

    def select_letter(self, letter):
        """Handle letter selection."""
        if self.is_replaying:
            return  # Do not allow letter selection during replay
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
                if not self.is_replaying:
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

        if self.player_types[self.game.current_player] == 'Computer':
            # Ignore clicks when it's computer's turn
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
            # Record the move if recording is enabled
            if self.is_recording:
                self.record_move(row, col, letter, self.game.current_player)
            self.update_board()
            self.selected_letter = None  # Reset selected letter after move
            # Reset the letter button states
            for btn in self.letter_buttons.values():
                btn.config(relief=tk.RAISED)
            if self.game.check_game_over():
                self.update_turn_label(game_over=True)
                self.after_game_over()
            else:
                self.update_turn_label()
                self.process_computer_turn()
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

    def process_computer_turn(self):
        """Process the computer's turn if applicable."""
        if self.game.game_over:
            return

        current_player_type = self.player_types[self.game.current_player]
        if current_player_type == 'Computer':
            # Disable letter buttons during computer's turn
            for btn in self.letter_buttons.values():
                btn.config(state=tk.DISABLED)

            # Use threading to prevent freezing the GUI
            threading.Thread(target=self.computer_move).start()
        else:
            # Enable letter buttons for human player
            for btn in self.letter_buttons.values():
                btn.config(state=tk.NORMAL)

    def computer_move(self):
        """Make a computer move."""
        time.sleep(0.5)  # Small delay to mimic thinking

        # Check if LLM Opponent is enabled
        if self.llm_var.get():
            move = self.get_llm_move()
        else:
            move = self.game.get_computer_move()

        if move is None:
            # No valid moves left
            return
        row, col, letter = move
        move_made = self.game.make_move(row, col, letter)
        if move_made:
            # Record the move if recording is enabled
            if self.is_recording:
                self.record_move(row, col, letter, self.game.current_player)
            # Update the UI from the main thread
            self.root.after(0, self.after_computer_move)
        else:
            # Should not happen, but handle it
            messagebox.showwarning("Invalid Move", "Computer attempted an invalid move.")

    def get_llm_move(self):
        """Get the next move from the LLM-based computer opponent."""
        board_state = ""
        for r in range(self.game.board_size):
            row_repr = []
            for c in range(self.game.board_size):
                cell = self.game.board[r][c]
                if cell is None:
                    row_repr.append(".")
                else:
                    row_repr.append(cell['letter'])
            board_state += " ".join(row_repr) + "\n"

        prompt = f"You are playing an SOS game on a {self.game.board_size}x{self.game.board_size} board.\n" \
                 f"The current player is {self.game.current_player}. Game mode is {self.game_mode_var.get()}.\n" \
                 f"Here is the board state ('.' for empty):\n{board_state}\n" \
                 "Suggest a single move in the format: row col letter\n" \
                 "Choose a move that creates an SOS if possible, otherwise choose a valid random move.\n" \
                 "Only return the move, nothing else.\n"

        try:
            response = openai.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant who can play SOS moves."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )
            llm_answer = response.choices[0].message.content.strip()
            parts = llm_answer.split()
            if len(parts) == 3:
                row = int(parts[0])
                col = int(parts[1])
                letter = parts[2].upper()
                if 0 <= row < self.game.board_size and 0 <= col < self.game.board_size and letter in ['S', 'O']:
                    return (row, col, letter)
        except Exception as e:
            messagebox.showerror("LLM Error", str(e))

        return None

    def after_computer_move(self):
        """Update UI after the computer has made a move."""
        self.update_board()
        if self.game.check_game_over():
            self.update_turn_label(game_over=True)
            self.after_game_over()
        else:
            self.update_turn_label()
            self.process_computer_turn()

    def record_move(self, row, col, letter, player):
        """Record the move details."""
        self.recorded_moves.append({
            'row': row,
            'col': col,
            'letter': letter,
            'player': player
        })

    def after_game_over(self):
        """Handle actions after the game is over."""
        if self.is_recording:
            self.save_recording()
        if not self.is_replaying:
            if self.game.winner == 'Draw':
                messagebox.showinfo("Game Over", "The game is over. It's a draw!")
            else:
                messagebox.showinfo("Game Over", f"The game is over. {self.game.winner} Player wins!")
        else:
            # Replay is over
            self.is_replaying = False
            # Enable user interaction after replay
            for btn in self.letter_buttons.values():
                btn.config(state=tk.NORMAL)

    def save_recording(self):
        """Save the recorded moves to a file."""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON Files", "*.json"), ("Text Files", "*.txt")],
            title="Save Game Recording"
        )
        if file_path:
            recording_data = {
                'board_size': self.game.board_size,
                'game_mode': self.game_mode_var.get(),
                'player_types': self.player_types,
                'moves': self.recorded_moves
            }
            with open(file_path, 'w') as f:
                json.dump(recording_data, f)
            messagebox.showinfo("Recording Saved", f"Game recording saved to {file_path}.")

    def replay_game(self):
        """Replay a game from a recorded file."""
        if self.game and not self.game.game_over:
            messagebox.showwarning("Game in Progress", "Please finish the current game before replaying.")
            return

        file_path = filedialog.askopenfilename(
            defaultextension=".json",
            filetypes=[("JSON Files", "*.json"), ("Text Files", "*.txt")],
            title="Open Game Recording"
        )
        if file_path:
            with open(file_path, 'r') as f:
                recording_data = json.load(f)
            if 'board_size' not in recording_data or 'moves' not in recording_data:
                messagebox.showerror("Invalid Recording", "The selected file is not a valid game recording.")
                return
            self.recorded_moves = recording_data['moves']
            self.setup_replay_game(recording_data)
            for btn in self.letter_buttons.values():
                btn.config(state=tk.DISABLED)
            self.is_replaying = True
            self.current_move_index = 0
            self.replay_next_move()

    def setup_replay_game(self, recording_data):
        """Set up the game for replay based on the recording data."""
        board_size = recording_data['board_size']
        game_mode = recording_data['game_mode']
        player_types = recording_data.get('player_types', {'Blue': 'Human', 'Red': 'Human'})

        self.board_size_entry.delete(0, tk.END)
        self.board_size_entry.insert(0, str(board_size))

        self.game_mode_var.set(game_mode)

        self.blue_player_var.set(player_types['Blue'])
        self.red_player_var.set(player_types['Red'])

        if game_mode == 'simple':
            self.game = SimpleGame(board_size)
        else:
            self.game = GeneralGame(board_size)
        self.game.start_new_game()

        self.player_types = player_types

        self.create_game_area()
        self.update_turn_label()

    def replay_next_move(self):
        """Replay the next move from the recorded moves."""
        if self.current_move_index >= len(self.recorded_moves):
            # Replay is over
            self.game.check_game_over()  # Ensure game over status is updated
            self.update_board()
            self.update_turn_label(game_over=True)
            self.after_game_over()
            return

        move = self.recorded_moves[self.current_move_index]
        row = move['row']
        col = move['col']
        letter = move['letter']
        player = move['player']

        self.game.current_player = player

        move_made = self.game.make_move(row, col, letter)
        if move_made:
            self.update_board()
            self.game.check_game_over()  # Check if the game is over after this move
            if self.game.game_over:
                self.update_turn_label(game_over=True)
                self.after_game_over()
                return
            else:
                self.update_turn_label()
                self.current_move_index += 1
                self.root.after(1000, self.replay_next_move)  # 1-second delay between moves
        else:
            messagebox.showerror("Replay Error", "Failed to replay move.")
            self.is_replaying = False

if __name__ == '__main__':
    GameUI()