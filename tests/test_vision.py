from vcore import BoardDetector, ExecutionController, PhysicsEngine, ShotAnalyzer, VCoreLoop
from vcore.board import BoardState, Coin


def make_demo_board() -> BoardState:
    state = BoardState(
        width=600,
        height=600,
        striker=Coin(id="striker", x=120.0, y=300.0, radius=18.0, color="white", is_striker=True),
        coins=[
            Coin(id="c1", x=300.0, y=260.0, radius=12.0, color="black"),
            Coin(id="c2", x=330.0, y=290.0, radius=12.0, color="red"),
            Coin(id="c3", x=345.0, y=260.0, radius=12.0, color="black"),
            Coin(id="c4", x=420.0, y=300.0, radius=12.0, color="red"),
        ],
    )
    state.log.append("Demo board initialized for VCore analysis.")
    return state


def main() -> None:
    board = make_demo_board()
    analyzer = ShotAnalyzer()
    best = analyzer.select_best_shot(board)
    controller = ExecutionController()
    result = controller.execute(board, best)
    print("Best shot:", best.description)
    print("Pocketed count:", sum(1 for coin in result.coins if coin.pocketed))
    print("Execution log:")
    for row in result.log:
        print(" -", row)

    loop = VCoreLoop(make_demo_board())
    final = loop.run_until_complete(max_steps=3)
    print("Loop completed after", final.turn, "turns.")


if __name__ == "__main__":
    main()
