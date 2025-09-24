from __future__ import annotations
from dataclasses import dataclass, field
from itertools import combinations
import random
from typing import Iterable, Tuple, List, Dict, Optional

TileSet = Tuple[int, ...]  # e.g., (1, 3, 5)


def combos_that_sum(nums: Iterable[int], target: int) -> List[TileSet]:
    nums = sorted(nums)
    out: List[TileSet] = []
    for k in range(1, len(nums) + 1):
        for c in combinations(nums, k):
            if sum(c) == target:
                out.append(c)
    # unique + sorted lexicographically (defensive; duplicates unlikely with unique tiles)
    out = sorted(set(out))
    return out


@dataclass
class Game:
    tiles_max: int = 9
    single_die_rule: bool = True
    rng: random.Random = field(default_factory=random.Random)

    tiles: Dict[int, bool] = field(init=False)  # True=open, False=closed
    over: bool = field(default=False, init=False)
    last_roll: Optional[int] = field(default=None, init=False)

    def __post_init__(self):
        if self.tiles_max < 1:
            raise ValueError("tiles_max must be >= 1")
        self.tiles = {i: True for i in range(1, self.tiles_max + 1)}

    # ---------- queries ----------
    def open_tiles(self) -> List[int]:
        return [i for i, is_open in self.tiles.items() if is_open]

    def score(self) -> int:
        return sum(self.open_tiles())

    def can_use_single_die(self) -> bool:
        if not self.single_die_rule:
            return False
        # Standard rule: once 7–9 are all closed, roll one die
        high = [i for i in (7, 8, 9) if i <= self.tiles_max]
        return all(not self.tiles.get(i, False) for i in high)

    def available_moves(self, target: int) -> List[TileSet]:
        return combos_that_sum(self.open_tiles(), target)

    # ---------- actions ----------
    def roll(self, forced: Optional[int] = None) -> int:
        if self.over:
            return self.last_roll if self.last_roll is not None else 0

        if forced is not None:
            r = forced
        else:
            if self.can_use_single_die():
                r = self.rng.randint(1, 6)
            else:
                r = self.rng.randint(1, 6) + self.rng.randint(1, 6)

        self.last_roll = r
        if not self.available_moves(r):
            self.over = True
        return r

    def move(self, chosen: Iterable[int]) -> bool:
        """
        Close the chosen tiles if they form a legal move for the *current* roll.
        Returns True if applied. False if illegal or game already over or no active roll.
        """
        if self.over or self.last_roll is None:
            return False

        chosen = tuple(sorted(int(x) for x in chosen))
        if chosen not in self.available_moves(self.last_roll):
            return False

        for t in chosen:
            self.tiles[t] = False

        # end-of-turn bookkeeping
        self.last_roll = None
        if not self.open_tiles():
            self.over = True
        return True

    def state(self) -> Dict:
        return {
            "tiles_max": self.tiles_max,
            "single_die_rule": self.single_die_rule,
            "tiles": dict(self.tiles),
            "over": self.over,
            "last_roll": self.last_roll,
            "open_tiles": self.open_tiles(),
            "score": self.score(),
        }
