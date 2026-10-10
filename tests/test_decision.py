import unittest

from vcore import PhysicsEngine
from vcore.board import BoardState, Coin


class TestPhysics(unittest.TestCase):
    def test_simulate_shot_updates_board(self):
        board = BoardState(
            striker=Coin(id="striker", x=90.0, y=300.0, radius=18.0, color="white", is_striker=True),
            coins=[Coin(id="c1", x=290.0, y=300.0, radius=12.0, color="black")],
        )
        result = PhysicsEngine.simulate_shot(board, 0.0, 1.0)
        self.assertIsNotNone(result)
        self.assertGreaterEqual(len(result.log), 1)


if __name__ == "__main__":
    unittest.main()
