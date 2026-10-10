from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Tuple


@dataclass
class Point:
    x: float
    y: float


@dataclass
class Coin:
    id: str
    x: float
    y: float
    radius: float = 12.0
    color: str = "black"
    pocketed: bool = False
    is_striker: bool = False


@dataclass
class BoardState:
    width: float = 600.0
    height: float = 600.0
    pockets: List[Tuple[float, float]] = field(
        default_factory=lambda: [
            (30.0, 30.0),
            (300.0, 30.0),
            (570.0, 30.0),
            (30.0, 570.0),
            (300.0, 570.0),
            (570.0, 570.0),
        ]
    )
    striker: Coin | None = None
    coins: List[Coin] = field(default_factory=list)
    turn: int = 0
    log: List[str] = field(default_factory=list)

    def clone(self) -> "BoardState":
        return BoardState(
            width=self.width,
            height=self.height,
            pockets=list(self.pockets),
            striker=Coin(
                id=self.striker.id,
                x=self.striker.x,
                y=self.striker.y,
                radius=self.striker.radius,
                color=self.striker.color,
                pocketed=self.striker.pocketed,
                is_striker=self.striker.is_striker,
            ) if self.striker else None,
            coins=[
                Coin(
                    id=c.id,
                    x=c.x,
                    y=c.y,
                    radius=c.radius,
                    color=c.color,
                    pocketed=c.pocketed,
                    is_striker=c.is_striker,
                )
                for c in self.coins
            ],
            turn=self.turn,
            log=list(self.log),
        )


@dataclass
class ShotCandidate:
    coin_id: str
    pocket_index: int
    angle: float
    force: float
    score: float
    expected_value: float
    description: str
