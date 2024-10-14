# game.py

class Game:
    """Class to manage the game logic for the SOS game."""

    def __init__(self, board_size, game_mode):
        """
        Initialize the game with the given board size and game mode.

        Args:
            board_size (int): The size of the board (n x n).
            game_mode (str): The game mode ('simple' or 'general').
        """
        if board_size <= 2:
            raise ValueError("Board size must be greater than 2.")
        self.board_size = board_size
        self.game_mode = game_mode  # 'simple' or 'general'
        self.board = [[None for _ in range(board_size)] for _ in range(board_size)]
        self.current_player = 'Blue'  # Blue starts first
        self.game_over = False
        self.winner = None

    def start_new_game(self):
        """Reset the game state to start a new game."""
        self.board = [[None for _ in range(self.board_size)] for _ in range(self.board_size)]
        self.current_player = 'Blue'
        self.game_over = False
        self.winner = None

    def is_move_valid(self, row, col):
        """
        Check if a move is valid.

        Args:
            row (int): Row index of the move.
            col (int): Column index of the move.

        Returns:
            bool: True if the move is valid, False otherwise.
        """
        if 0 <= row < self.board_size and 0 <= col < self.board_size:
            return self.board[row][col] is None
        else:
            return False

    def make_move(self, row, col, letter):
        """
        Place a letter ('S' or 'O') on the board at the specified position.

        Args:
            row (int): Row index.
            col (int): Column index.
            letter (str): 'S' or 'O'.

        Returns:
            bool: True if the move was made, False otherwise.
        """
        if not self.is_move_valid(row, col):
            return False

        self.board[row][col] = {'letter': letter.upper(), 'player': self.current_player}
        # For Sprint 2, we are not checking for SOS formation
        self.switch_player()
        return True

    def switch_player(self):
        """Switch the current player."""
        self.current_player = 'Red' if self.current_player == 'Blue' else 'Blue'

    def check_game_over(self):
        """
        Check if the game is over.

        Returns:
            bool: True if the game is over, False otherwise.
        """
        for row in self.board:
            for cell in row:
                if cell is None:
                    return False
        self.game_over = True
        return True

    def get_board(self):
        """Get the current state of the board."""
        return self.board

    def get_current_player(self):
        """Get the current player."""
        return self.current_player

    def get_game_mode(self):
        """Get the game mode."""
        return self.game_mode