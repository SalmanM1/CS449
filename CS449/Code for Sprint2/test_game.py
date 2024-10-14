# test_game.py

import unittest
from game import Game

class TestGame(unittest.TestCase):
    """Unit tests for the Game class."""

    def setUp(self):
        """Set up a game instance for testing."""
        self.game = Game(3, 'simple')
        self.game.start_new_game()

    def test_initialization_valid(self):
        """Test initializing the game with a valid board size."""
        self.assertEqual(self.game.board_size, 3)
        self.assertEqual(self.game.game_mode, 'simple')
        self.assertEqual(len(self.game.board), 3)
        self.assertEqual(len(self.game.board[0]), 3)
        self.assertEqual(self.game.current_player, 'Blue')
        self.assertFalse(self.game.game_over)

    def test_initialization_invalid(self):
        """Test initializing the game with an invalid board size."""
        with self.assertRaises(ValueError):
            invalid_game = Game(2, 'simple')

    def test_is_move_valid(self):
        """Test the move validation logic."""
        self.assertTrue(self.game.is_move_valid(0, 0))
        self.game.board[0][0] = {'letter': 'S', 'player': 'Blue'}
        self.assertFalse(self.game.is_move_valid(0, 0))
        self.assertFalse(self.game.is_move_valid(-1, 0))
        self.assertFalse(self.game.is_move_valid(0, 3))

    def test_make_move_valid(self):
        """Test making a valid move."""
        move_made = self.game.make_move(0, 0, 'S')
        self.assertTrue(move_made)
        self.assertEqual(self.game.board[0][0], {'letter': 'S', 'player': 'Blue'})
        self.assertEqual(self.game.current_player, 'Red')

    def test_make_move_invalid(self):
        """Test making an invalid move."""
        self.game.board[0][0] = {'letter': 'S', 'player': 'Blue'}
        move_made = self.game.make_move(0, 0, 'O')
        self.assertFalse(move_made)
        self.assertEqual(self.game.board[0][0], {'letter': 'S', 'player': 'Blue'})
        self.assertEqual(self.game.current_player, 'Blue')  # Player doesn't change on invalid move

    def test_switch_player(self):
        """Test that the current player switches after a valid move."""
        self.assertEqual(self.game.current_player, 'Blue')
        self.game.make_move(0, 0, 'S')
        self.assertEqual(self.game.current_player, 'Red')
        self.game.make_move(0, 1, 'O')
        self.assertEqual(self.game.current_player, 'Blue')

    def test_check_game_over_full_board(self):
        """Test the game over condition when the board is full."""
        # Fill the board
        player = 'Blue'
        for row in range(3):
            for col in range(3):
                self.game.board[row][col] = {'letter': 'S', 'player': player}
                player = 'Red' if player == 'Blue' else 'Blue'
        self.assertTrue(self.game.check_game_over())
        self.assertTrue(self.game.game_over)

    def test_check_game_not_over(self):
        """Test that the game is not over when the board is not full."""
        self.game.make_move(0, 0, 'S')
        self.assertFalse(self.game.check_game_over())
        self.assertFalse(self.game.game_over)

    def test_get_board(self):
        """Test retrieving the current state of the board."""
        self.game.make_move(0, 0, 'S')
        board = self.game.get_board()
        expected_board = [
            [{'letter': 'S', 'player': 'Blue'}, None, None],
            [None, None, None],
            [None, None, None]
        ]
        self.assertEqual(board, expected_board)

    def test_get_current_player(self):
        """Test getting the current player."""
        self.assertEqual(self.game.get_current_player(), 'Blue')
        self.game.make_move(0, 0, 'S')
        self.assertEqual(self.game.get_current_player(), 'Red')

    def test_get_game_mode(self):
        """Test getting the game mode."""
        self.assertEqual(self.game.get_game_mode(), 'simple')

if __name__ == '__main__':
    unittest.main()