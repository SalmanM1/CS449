import unittest
from sos_game import is_sos_sequence

class TestSOSSequence(unittest.TestCase):
    
    def test_valid_sos(self):
        result = is_sos_sequence(['S', 'O', 'S'])
        self.assertTrue(result)

    def test_invalid_sos(self):
        result = is_sos_sequence(['S', 'O', 'X'])
        self.assertFalse(result)

if __name__ == '__main__':
    unittest.main()