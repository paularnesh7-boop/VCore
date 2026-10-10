import unittest

from vcore import ShotAnalyzer
from vcore.board import BoardState, Coin


class TestDecision(unittest.TestCase):
    def test_select_best_shot(self):
        board = BoardState(
            striker=Coin(id="striker", x=100.0, y=300.0, radius=18.0, color="white", is_striker=True),
            coins=[
                Coin(id="c1", x=280.0, y=300.0, radius=12.0, color="black"),
                Coin(id="c2", x=350.0, y=230.0, radius=12.0, color="red"),
            ],
        )
        shot = ShotAnalyzer.select_best_shot(board)
        self.assertTrue(shot.score > 0)
        self.assertIn(shot.coin_id, {"c1", "c2"})


if __name__ == "__main__":
    unittest.main()
