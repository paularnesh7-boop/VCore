import math
from typing import Iterable, List, Sequence, Tuple

from .board import BoardState, Coin, ShotCandidate


class BoardDetector:
    """Determine the board layout and object positions from a lightweight structured input. This is intentionally modular and does not perform real image analysis."""

    @staticmethod
    def detect_board(objects: Sequence[dict]) -> BoardState:
        if not objects:
            raise ValueError("No objects were provided for board detection.")

        xs = [float(obj["x"]) for obj in objects]
        ys = [float(obj["y"]) for obj in objects]
        board = BoardState(
            width=max(xs) - min(xs) + 80.0,
            height=max(ys) - min(ys) + 80.0,
            striker=None,
            coins=[],
        )

        for item in objects:
            coin = Coin(
                id=str(item.get("id", len(board.coins))),
                x=float(item["x"]),
                y=float(item["y"]),
                radius=float(item.get("radius", 12.0)),
                color=str(item.get("color", "black")),
                pocketed=False,
                is_striker=bool(item.get("is_striker", False)),
            )
            if coin.is_striker:
                board.striker = coin
            else:
                board.coins.append(coin)

        if board.striker is None:
            board.striker = Coin(id="striker", x=95.0, y=board.height / 2.0, radius=18.0, color="white", is_striker=True)

        board.log.append(f"Board detected with {len(board.coins)} coins and striker at ({board.striker.x:.2f}, {board.striker.y:.2f}).")
        return board


class ShotAnalyzer:
    """Generate candidate shots, score them, and choose the best target."""

    @staticmethod
    def generate_shot_candidates(board: BoardState) -> List[ShotCandidate]:
        candidates: List[ShotCandidate] = []
        for pocket_index, pocket in enumerate(board.pockets):
            for coin in board.coins:
                if coin.pocketed:
                    continue
                dx = pocket[0] - coin.x
                dy = pocket[1] - coin.y
                distance = math.hypot(dx, dy)
                if distance <= 0:
                    continue
                angle = math.atan2(dy, dx)
                force = min(1.0, max(0.2, distance / 420.0))
                score = 100.0 / (distance + 20.0)
                score += 10.0 if abs(dy) < 40 else 0.0
                score += pocket_index % 2 * 2.0
                candidates.append(
                    ShotCandidate(
                        coin_id=coin.id,
                        pocket_index=pocket_index,
                        angle=angle,
                        force=force,
                        score=score,
                        expected_value=score * 0.8,
                        description=f"Attempt to pocket coin {coin.id} into pocket {pocket_index}.",
                    )
                )
        return sorted(candidates, key=lambda c: c.score, reverse=True)

    @staticmethod
    def select_best_shot(board: BoardState) -> ShotCandidate:
        candidates = ShotAnalyzer.generate_shot_candidates(board)
        if not candidates:
            raise ValueError("No valid shot candidates are available.")
        return candidates[0]


class PhysicsEngine:
    """Simple yet concrete physics model for striker-to-coin interaction, momentum transfer, friction, and pocketing."""

    @staticmethod
    def distance(a, b):
        return math.hypot(a[0] - b[0], a[1] - b[1])

    @staticmethod
    def simulate_shot(board: BoardState, aim_angle: float, force: float, striker_offset: float = 0.0) -> BoardState:
        state = board.clone()
        striker = state.striker
        striker.x = min(max(striker.x + math.cos(aim_angle) * striker_offset, 50.0), state.width - 50.0)
        striker.y = min(max(striker.y + math.sin(aim_angle) * striker_offset, 50.0), state.height - 50.0)

        striker_velocity = (math.cos(aim_angle) * force * 30.0, math.sin(aim_angle) * force * 30.0)
        step_count = 0
        while step_count < 180:
            step_count += 1
            striker_x, striker_y = striker.x, striker.y
            striker.x += striker_velocity[0] * 0.08
            striker.y += striker_velocity[1] * 0.08
            striker_velocity = (striker_velocity[0] * 0.985, striker_velocity[1] * 0.985)

            for coin in state.coins:
                if coin.pocketed:
                    continue
                dx = coin.x - striker.x
                dy = coin.y - striker.y
                dist = math.hypot(dx, dy)
                min_dist = coin.radius + striker.radius
                if dist <= min_dist + 2.0:
                    nx = dx / dist if dist else 1.0
                    ny = dy / dist if dist else 0.0
                    relative_speed = (striker_velocity[0] * nx) + (striker_velocity[1] * ny)
                    if relative_speed < 0:
                        impulse = -(1.1 * relative_speed) / (1.0 / 1.5 + 1.0 / 1.5)
                        striker_velocity = (
                            striker_velocity[0] + (impulse * nx) / 1.5,
                            striker_velocity[1] + (impulse * ny) / 1.5,
                        )
                        coin.x += nx * 8.0
                        coin.y += ny * 8.0
                        striker.x -= nx * 4.0
                        striker.y -= ny * 4.0

            for coin in state.coins:
                if coin.pocketed:
                    continue
                for pocket in state.pockets:
                    if math.hypot(coin.x - pocket[0], coin.y - pocket[1]) <= coin.radius + 12.0:
                        coin.pocketed = True
                        state.log.append(f"Coin {coin.id} pocketed at {pocket}.")

            if math.hypot(striker_velocity[0], striker_velocity[1]) < 0.2:
                break

            if abs(striker.x - striker_x) < 0.01 and abs(striker.y - striker_y) < 0.01:
                break

        state.log.append(
            f"Shot executed with angle {math.degrees(aim_angle):.1f}° and force {force:.2f}. Current striker: ({striker.x:.2f}, {striker.y:.2f})."
        )
        state.turn += 1
        return state


class ExecutionController:
    """Translate the selected shot into action, then inspect the new board state and generate feedback."""

    def __init__(self):
        self.execution_log: List[str] = []

    def execute(self, board: BoardState, shot: ShotCandidate) -> BoardState:
        aim_angle = shot.angle
        next_state = PhysicsEngine.simulate_shot(board, aim_angle, shot.force)
        next_state.log.extend(self.execution_log)
        self.execution_log.append(f"Executed shot: {shot.description}")
        self.execution_log.append(f"Outcome: {len([c for c in next_state.coins if c.pocketed])} coins pocketed.")
        return next_state


class VCoreLoop:
    """Complete perception -> decision -> execution -> feedback loop for the local simulation."""

    def __init__(self, board: BoardState):
        self.board = board
        self.controller = ExecutionController()

    def step(self) -> BoardState:
        shot = ShotAnalyzer.select_best_shot(self.board)
        self.board.log.append(f"Selected shot: {shot.description}")
        self.board = self.controller.execute(self.board, shot)
        return self.board

    def run_until_complete(self, max_steps: int = 6) -> BoardState:
        for _ in range(max_steps):
            before = len([coin for coin in self.board.coins if coin.pocketed])
            self.step()
            after = len([coin for coin in self.board.coins if coin.pocketed])
            if after > before:
                self.board.log.append(f"Board updated after shot. Pocketed total: {after}.")
            if after >= 3:
                break
        return self.board
