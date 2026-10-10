import unittest

from vcore import BoardDetector


class TestVision(unittest.TestCase):
    def test_detect_board_builds_state(self):
        objects = [
            {"id": "striker", "x": 80, "y": 300, "radius": 18, "is_striker": True},
            {"id": "c1", "x": 280, "y": 250, "radius": 12},
            {"id": "c2", "x": 320, "y": 300, "radius": 12},
        ]
        board = BoardDetector.detect_board(objects)
        self.assertEqual(board.striker.id, "striker")
        self.assertEqual(len(board.coins), 2)
        self.assertGreater(board.width, 0)
        self.assertGreater(board.height, 0)


if __name__ == "__main__":
    unittest.main()
