# game.py

import random

class BaseGame:
    """Abstract base class for SOS game."""

    def __init__(self, board_size):
        if board_size <= 2:
            raise ValueError("Board size must be greater than 2.")
        self.board_size = board_size
        self.board = [[None for _ in range(board_size)] for _ in range(board_size)]
        self.current_player = 'Blue'
        self.game_over = False
        self.winner = None
        self.blue_sequences = []
        self.red_sequences = []

    def start_new_game(self):
        """Reset the game state to start a new game."""
        self.board = [[None for _ in range(self.board_size)] for _ in range(self.board_size)]
        self.current_player = 'Blue'
        self.game_over = False
        self.winner = None
        self.blue_sequences = []
        self.red_sequences = []

    def is_move_valid(self, row, col):
        """Check if a move is valid."""
        if 0 <= row < self.board_size and 0 <= col < self.board_size:
            return self.board[row][col] is None
        else:
            return False

    def switch_player(self):
        """Switch the current player."""
        self.current_player = 'Red' if self.current_player == 'Blue' else 'Blue'

    def check_for_sos_s(self, row, col):
        """Check for SOS sequences when an 'S' is placed at (row, col)."""
        sequences = []
        s_row, s_col = row, col

        directions = [
            (-1, 0),   # Up
            (1, 0),    # Down
            (0, -1),   # Left
            (0, 1),    # Right
            (-1, -1),  # Up-Left
            (-1, 1),   # Up-Right
            (1, -1),   # Down-Left
            (1, 1),    # Down-Right
        ]

        for dx, dy in directions:
            o_row = s_row + dx
            o_col = s_col + dy
            s2_row = s_row + 2 * dx
            s2_col = s_col + 2 * dy

            if not (0 <= o_row < self.board_size and 0 <= o_col < self.board_size):
                continue
            if not (0 <= s2_row < self.board_size and 0 <= s2_col < self.board_size):
                continue

            o_cell = self.board[o_row][o_col]
            s2_cell = self.board[s2_row][s2_col]

            if o_cell and s2_cell:
                if o_cell['letter'] == 'O' and s2_cell['letter'] == 'S':
                    start_pos = (s_row, s_col)
                    end_pos = (s2_row, s2_col)
                    if start_pos > end_pos:
                        start_pos, end_pos = end_pos, start_pos
                    sequences.append((start_pos, end_pos))

        return sequences

    def check_for_sos(self, row, col):
        """Check for SOS sequences when an 'O' is placed at (row, col)."""
        sequences = []
        o_row, o_col = row, col

        if self.board[o_row][o_col]['letter'] != 'O':
            return sequences

        directions = [
            (-1, 0),   # Vertical
            (1, 0),
            (0, -1),   # Horizontal
            (0, 1),
            (-1, -1),  # Diagonal \
            (1, 1),
            (-1, 1),   # Diagonal /
            (1, -1),
        ]

        for dx, dy in directions:
            s1_row = o_row - dx
            s1_col = o_col - dy
            s2_row = o_row + dx
            s2_col = o_col + dy

            if not (0 <= s1_row < self.board_size and 0 <= s1_col < self.board_size):
                continue
            if not (0 <= s2_row < self.board_size and 0 <= s2_col < self.board_size):
                continue

            s1_cell = self.board[s1_row][s1_col]
            s2_cell = self.board[s2_row][s2_col]

            if s1_cell and s2_cell:
                if s1_cell['letter'] == 'S' and s2_cell['letter'] == 'S':
                    start_pos = (s1_row, s1_col)
                    end_pos = (s2_row, s2_col)
                    if start_pos > end_pos:
                        start_pos, end_pos = end_pos, start_pos
                    sequences.append((start_pos, end_pos))

        return sequences

    def get_valid_moves(self):
        """Get a list of all valid moves."""
        valid_moves = []
        for row in range(self.board_size):
            for col in range(self.board_size):
                if self.board[row][col] is None:
                    valid_moves.append((row, col))
        return valid_moves

    def find_potential_sos_moves(self):
        """Find moves that will create an SOS."""
        potential_moves = []
        for row, col in self.get_valid_moves():
            for letter in ['S', 'O']:
                # Temporarily place the letter
                self.board[row][col] = {'letter': letter, 'player': self.current_player}
                sequences = []
                if letter == 'S':
                    sequences.extend(self.check_for_sos_s(row, col))
                elif letter == 'O':
                    sequences.extend(self.check_for_sos(row, col))
                # Remove the temporary letter
                self.board[row][col] = None
                if sequences:
                    potential_moves.append((row, col, letter))
        return potential_moves

    def make_move(self, row, col, letter):
        """Abstract method to make a move."""
        raise NotImplementedError("Must be implemented by subclasses.")

    def check_game_over(self):
        """Abstract method to check if the game is over."""
        raise NotImplementedError("Must be implemented by subclasses.")


class SimpleGame(BaseGame):
    """Class representing a simple SOS game."""

    def make_move(self, row, col, letter):
        letter = letter.upper()
        if letter not in ('S', 'O'):
            return False  # Invalid letter

        if not self.is_move_valid(row, col):
            return False

        self.board[row][col] = {'letter': letter, 'player': self.current_player}

        sequences = []

        if letter == 'S':
            sequences.extend(self.check_for_sos_s(row, col))
        elif letter == 'O':
            sequences.extend(self.check_for_sos(row, col))

        if sequences:
            self.game_over = True
            self.winner = self.current_player
            if self.current_player == 'Blue':
                self.blue_sequences.extend(sequences)
            else:
                self.red_sequences.extend(sequences)
        else:
            self.switch_player()

        return True

    def check_game_over(self):
        if self.game_over:
            return True
        else:
            # Check if the board is full
            for row in self.board:
                for cell in row:
                    if cell is None:
                        return False  # Board is not full yet
            # Board is full and no winner, so it's a draw
            self.game_over = True
            self.winner = 'Draw'
            return True

    def get_computer_move(self):
        """Determine the computer's move."""
        # Try to find a move that will create an SOS and win the game
        potential_moves = self.find_potential_sos_moves()
        if potential_moves:
            # Choose one of the moves that create an SOS
            move = random.choice(potential_moves)
            return move  # (row, col, letter)
        else:
            # Choose a random valid move
            valid_moves = self.get_valid_moves()
            if not valid_moves:
                return None  # No moves left
            row, col = random.choice(valid_moves)
            letter = random.choice(['S', 'O'])
            return (row, col, letter)


class GeneralGame(BaseGame):
    """Class representing a general SOS game."""

    def make_move(self, row, col, letter):
        letter = letter.upper()
        if letter not in ('S', 'O'):
            return False  # Invalid letter

        if not self.is_move_valid(row, col):
            return False

        self.board[row][col] = {'letter': letter.upper(), 'player': self.current_player}

        sequences = []

        if letter == 'S':
            sequences.extend(self.check_for_sos_s(row, col))
        elif letter == 'O':
            sequences.extend(self.check_for_sos(row, col))

        if sequences:
            if self.current_player == 'Blue':
                self.blue_sequences.extend(sequences)
            else:
                self.red_sequences.extend(sequences)
            # Player gets another turn, so do not switch
        else:
            self.switch_player()

        return True

    def check_game_over(self):
        if self.game_over:
            return True

        # Check if the board is full
        for row in self.board:
            for cell in row:
                if cell is None:
                    return False  # Game is not over yet

        self.game_over = True
        # Determine winner
        blue_count = len(self.blue_sequences)
        red_count = len(self.red_sequences)
        if blue_count > red_count:
            self.winner = 'Blue'
        elif red_count > blue_count:
            self.winner = 'Red'
        else:
            self.winner = 'Draw'
        return True

    def get_computer_move(self):
        """Determine the computer's move."""
        # Try to find a move that will create an SOS
        potential_moves = self.find_potential_sos_moves()
        if potential_moves:
            # Choose one of the moves that create an SOS
            move = random.choice(potential_moves)
            return move  # (row, col, letter)
        else:
            # Choose a random valid move
            valid_moves = self.get_valid_moves()
            if not valid_moves:
                return None  # No moves left
            row, col = random.choice(valid_moves)
            letter = random.choice(['S', 'O'])
            return (row, col, letter)