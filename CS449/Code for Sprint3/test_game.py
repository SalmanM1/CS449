# test_game.py

import unittest
from game import BaseGame, SimpleGame, GeneralGame

class TestBaseGame(unittest.TestCase):
    """Unit tests for the BaseGame class."""

    def test_initialization_valid(self):
        """Test initializing the game with a valid board size."""
        game = SimpleGame(3)  # Using SimpleGame to test BaseGame methods
        self.assertEqual(game.board_size, 3)
        self.assertEqual(len(game.board), 3)
        self.assertEqual(len(game.board[0]), 3)
        self.assertEqual(game.current_player, 'Blue')
        self.assertFalse(game.game_over)

    def test_initialization_invalid(self):
        """Test initializing the game with an invalid board size."""
        with self.assertRaises(ValueError):
            SimpleGame(2)  # Should raise ValueError

    def test_is_move_valid(self):
        """Test the move validation logic."""
        game = SimpleGame(3)
        self.assertTrue(game.is_move_valid(0, 0))
        game.board[0][0] = {'letter': 'S', 'player': 'Blue'}
        self.assertFalse(game.is_move_valid(0, 0))
        self.assertFalse(game.is_move_valid(-1, 0))
        self.assertFalse(game.is_move_valid(0, 3))

class TestSimpleGame(unittest.TestCase):
    """Unit tests for the SimpleGame class."""

    def setUp(self):
        """Set up a simple game instance for testing."""
        self.game = SimpleGame(3)
        self.game.start_new_game()

    def test_initialization(self):
        """Test initializing the game."""
        self.assertEqual(self.game.board_size, 3)
        self.assertFalse(self.game.game_over)
        self.assertEqual(self.game.current_player, 'Blue')

    def test_make_move_valid(self):
        """Test making a valid move."""
        move_made = self.game.make_move(0, 0, 'S')
        self.assertTrue(move_made)
        self.assertEqual(self.game.board[0][0], {'letter': 'S', 'player': 'Blue'})
        self.assertEqual(self.game.current_player, 'Red')  # Switches player since no SOS

    def test_make_move_invalid(self):
        """Test making an invalid move."""
        self.game.board[0][0] = {'letter': 'S', 'player': 'Blue'}
        move_made = self.game.make_move(0, 0, 'O')
        self.assertFalse(move_made)
        self.assertEqual(self.game.current_player, 'Blue')  # Player doesn't change on invalid move

    def test_switch_player(self):
        """Test that the current player switches after a valid move."""
        self.assertEqual(self.game.current_player, 'Blue')
        self.game.make_move(0, 0, 'S')
        self.assertEqual(self.game.current_player, 'Red')
        self.game.make_move(0, 1, 'O')
        self.assertEqual(self.game.current_player, 'Blue')

    def test_check_game_over_full_board(self):
        """Test the game over condition when the board is full without any SOS sequences."""
        # Fill the board without any SOS sequences
        moves = [
            (0, 0, 'O'), (0, 1, 'S'), (0, 2, 'O'),
            (1, 0, 'S'), (1, 1, 'O'), (1, 2, 'O'),  # Changed 'S' to 'O' at (1,2)
            (2, 0, 'O'), (2, 1, 'O'), (2, 2, 'O')
        ]
        for move in moves:
            self.game.make_move(*move)
        self.game.check_game_over()
        self.assertTrue(self.game.game_over)
        self.assertEqual(self.game.winner, 'Draw')

    def test_check_game_not_over(self):
        """Test that the game is not over when the board is not full and no winner."""
        self.game.make_move(0, 0, 'S')
        self.assertFalse(self.game.check_game_over())
        self.assertFalse(self.game.game_over)
        self.assertIsNone(self.game.winner)

    def test_sos_detection(self):
        """Test that the game correctly detects SOS sequences."""
        # Blue's turn
        self.game.make_move(0, 0, 'S')
        # Red's turn
        self.game.make_move(1, 1, 'O')
        # Blue's turn
        self.game.make_move(2, 2, 'S')
        # Should detect an SOS diagonally
        self.assertTrue(self.game.game_over)
        self.assertEqual(self.game.winner, 'Blue')
        expected_sequence = [((0, 0), (2, 2))]
        self.assertEqual(self.game.blue_sequences, expected_sequence)

    def test_make_move_invalid_letter(self):
        """Test making a move with an invalid letter."""
        move_made = self.game.make_move(0, 0, 'X')
        self.assertFalse(move_made)
        self.assertEqual(self.game.current_player, 'Blue')

    def test_make_move_lower_case_letter(self):
        """Test making a move with a lower-case letter."""
        move_made = self.game.make_move(0, 0, 's')
        self.assertTrue(move_made)
        self.assertEqual(self.game.board[0][0], {'letter': 'S', 'player': 'Blue'})
        self.assertEqual(self.game.current_player, 'Red')

    def test_is_move_valid_out_of_bounds(self):
        """Test that the game correctly handles out of bounds moves."""
        self.assertFalse(self.game.is_move_valid(-1, 0))
        self.assertFalse(self.game.is_move_valid(0, -1))
        self.assertFalse(self.game.is_move_valid(3, 0))
        self.assertFalse(self.game.is_move_valid(0, 3))

    def test_game_over_with_winner(self):
        """Test that the game correctly identifies when it's over with a winner."""
        # Blue makes moves to form an SOS
        self.game.make_move(0, 0, 'S')  # Blue
        self.game.make_move(1, 0, 'O')  # Red
        self.game.make_move(2, 0, 'S')  # Blue
        self.game.check_game_over()
        self.assertTrue(self.game.game_over)
        self.assertEqual(self.game.winner, 'Blue')

    def test_current_player_does_not_change_on_invalid_move(self):
        """Test that the current player does not change on invalid move."""
        self.assertEqual(self.game.current_player, 'Blue')
        self.game.make_move(0, 0, 'S')  # Blue's valid move
        self.assertEqual(self.game.current_player, 'Red')
        move_made = self.game.make_move(0, 0, 'O')  # Red's invalid move
        self.assertFalse(move_made)
        self.assertEqual(self.game.current_player, 'Red')  # Should still be Red's turn

class TestGeneralGame(unittest.TestCase):
    """Unit tests for the GeneralGame class."""

    def setUp(self):
        """Set up a general game instance for testing."""
        self.game = GeneralGame(3)
        self.game.start_new_game()

    def test_make_move_with_sos(self):
        """Test that a player gets another turn after forming an SOS."""
        # Blue's turn
        self.game.make_move(0, 0, 'S')
        self.assertEqual(self.game.current_player, 'Red')  # No SOS, switch player

        # Red's turn
        self.game.make_move(0, 1, 'O')
        self.assertEqual(self.game.current_player, 'Blue')  # No SOS, switch player

        # Blue's turn
        self.game.make_move(0, 2, 'S')
        # Should detect an SOS horizontally
        self.assertEqual(len(self.game.blue_sequences), 1)
        self.assertEqual(self.game.current_player, 'Blue')  # Blue gets another turn

    def test_game_over_and_winner(self):
        """Test that the game correctly determines the winner in general game."""
        # Sequence of moves where Red is expected to win
        moves = [
            (0, 0, 'S'),  # Blue
            (1, 1, 'O'),  # Red
            (0, 1, 'S'),  # Blue
            (2, 2, 'S'),  # Red
            (0, 2, 'S'),  # Blue
            (1, 2, 'S'),  # Red
        ]
        for move in moves:
            self.game.make_move(*move)
        # Red's turn; Red forms SOS sequences
        self.game.make_move(2, 0, 'S')  # Red
        # Ensure the SOS was detected
        self.assertEqual(len(self.game.red_sequences), 2)
        self.assertEqual(len(self.game.blue_sequences), 0)
        self.assertEqual(self.game.current_player, 'Red')  # Red gets another turn
        # Fill remaining cells to end the game
        self.game.make_move(1, 0, 'O')  # Red
        self.game.make_move(2, 1, 'O')  # Red
        # Call check_game_over
        self.game.check_game_over()
        self.assertTrue(self.game.game_over)
        self.assertEqual(self.game.winner, 'Red')

    def test_make_move_invalid(self):
        """Test making an invalid move in GeneralGame."""
        self.game.board[0][0] = {'letter': 'S', 'player': 'Blue'}
        move_made = self.game.make_move(0, 0, 'O')
        self.assertFalse(move_made)
        self.assertEqual(self.game.current_player, 'Blue')  # Player doesn't change on invalid move

    def test_switch_player_after_no_sos(self):
        """Test that the current player switches after a move with no SOS in GeneralGame."""
        self.assertEqual(self.game.current_player, 'Blue')
        self.game.make_move(0, 0, 'S')  # No SOS
        self.assertEqual(self.game.current_player, 'Red')

    def test_current_player_does_not_change_after_sos(self):
        """Test that the current player does not change after forming an SOS in GeneralGame."""
        self.game.make_move(0, 0, 'S')  # Blue
        self.game.make_move(1, 1, 'O')  # Red
        self.game.make_move(0, 1, 'O')  # Blue
        self.game.make_move(1, 0, 'S')  # Red
        self.game.make_move(0, 2, 'S')  # Blue, forms SOS horizontally
        self.assertEqual(self.game.current_player, 'Blue')  # Should still be Blue's turn

if __name__ == '__main__':
    unittest.main()