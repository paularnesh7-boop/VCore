import math
from typing import Iterable, Sequence, Tuple

from .board import BoardState, Coin


def pocket_distance(coin: Coin, pocket: Tuple[float, float]) -> float:
    return math.hypot(coin.x - pocket[0], coin.y - pocket[1])


def impact_velocity(striker_velocity: Tuple[float, float], coin_velocity: Tuple[float, float], normal: Tuple[float, float]) -> Tuple[float, float]:
    relative = (
        striker_velocity[0] - coin_velocity[0],
        striker_velocity[1] - coin_velocity[1],
    )
    normal_speed = relative[0] * normal[0] + relative[1] * normal[1]
    if normal_speed >= 0:
        return striker_velocity
    impulse = -1.2 * normal_speed
    return (
        striker_velocity[0] + impulse * normal[0],
        striker_velocity[1] + impulse * normal[1],
    )


def compute_trajectory(board: BoardState, angle_deg: float, force: float) -> Sequence[Tuple[float, float]]:
    angle = math.radians(angle_deg)
    points: list[Tuple[float, float]] = []
    x = board.striker.x
    y = board.striker.y
    vx = math.cos(angle) * force * 5.0
    vy = math.sin(angle) * force * 5.0
    for _ in range(30):
        x += vx
        y += vy
        vx *= 0.98
        vy *= 0.98
        points.append((x, y))
    return points
