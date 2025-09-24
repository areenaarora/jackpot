#!/usr/bin/env python3
"""
Shut the Box — Visual Demo
--------------------------
Run a single visualized episode (table) and a Monte Carlo batch to plot score distribution.

Usage:
  python visual_demo.py --episode-seed 21 --episodes 1500

Outputs:
  - Opens a matplotlib window (omit with --no-show)
  - Writes episode timeline to CSV: ./episode_timeline.csv
  - Writes score summary to CSV:    ./score_summary.csv
  - Writes histogram PNG:           ./score_hist.png
"""

from dataclasses import dataclass, field
from itertools import combinations
import argparse
import random
from typing import Iterable, Tuple, List, Dict, Optional

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

TileSet = Tuple[int, ...]


def combos_that_sum(nums: Iterable[int], target: int) -> List[TileSet]:
    nums = sorted(nums)
    out: List[TileSet] = []
    for k in range(1, len(nums) + 1):
        for c in combinations(nums, k):
            if sum(c) == target:
                out.append(c)
    return sorted(set(out))


@dataclass
class Game:
    tiles_max: int = 9
    single_die_rule: bool = True
    rng: random.Random = field(default_factory=random.Random)

    tiles: Dict[int, bool] = field(init=False)
    over: bool = field(default=False, init=False)
    last_roll: Optional[int] = field(default=None, init=False)

    def __post_init__(self):
        if self.tiles_max < 1:
            raise ValueError("tiles_max must be >= 1")
        self.tiles = {i: True for i in range(1, self.tiles_max + 1)}

    # ----- queries -----
    def open_tiles(self) -> List[int]:
        return [i for i, is_open in self.tiles.items() if is_open]

    def score(self) -> int:
        return sum(self.open_tiles())

    def can_choose_die_count(self) -> bool:
        high = [i for i in (7, 8, 9) if i <= self.tiles_max]
        return self.single_die_rule and all(not self.tiles.get(i, False) for i in high)

    def available_moves(self, target: int) -> List[TileSet]:
        return combos_that_sum(self.open_tiles(), target)

    # ----- actions -----
    def roll(self, *, forced: Optional[int] = None, dice: Optional[int] = None) -> int:
        if self.over:
            return self.last_roll if self.last_roll is not None else 0

        if self.can_choose_die_count():
            dcount = 1 if dice == 1 else 2 if dice == 2 else 2
        else:
            dcount = 2

        if forced is not None:
            r = forced
        else:
            r = sum(self.rng.randint(1, 6) for _ in range(dcount))

        self.last_roll = r
        if not self.available_moves(r):
            self.over = True
        return r

    def move(self, chosen: Iterable[int]) -> bool:
        if self.over or self.last_roll is None:
            return False
        chosen = tuple(sorted(int(x) for x in chosen))
        if chosen not in self.available_moves(self.last_roll):
            return False
        for t in chosen:
            self.tiles[t] = False
        self.last_roll = None
        if not self.open_tiles():
            self.over = True
        return True

    def state(self) -> Dict:
        return {
            "tiles": dict(self.tiles),
            "over": self.over,
            "last_roll": self.last_roll,
            "open_tiles": self.open_tiles(),
            "score": self.score(),
        }


# --- Policies ---
def greedy_policy(legal_moves: List[TileSet]) -> TileSet:
    # Prefer fewer tiles; if tie, prefer the one with highest max tile.
    if not legal_moves:
        return tuple()
    legal_moves = sorted(legal_moves, key=lambda c: (len(c), -max(c)))
    return legal_moves[0]


def random_policy(legal_moves: List[TileSet], rng: random.Random) -> TileSet:
    return rng.choice(legal_moves) if legal_moves else tuple()


# --- Runners ---
def run_episode(seed=42, policy="greedy") -> pd.DataFrame:
    g = Game(rng=random.Random(seed))
    steps = []
    t = 0
    while not g.over:
        r = g.roll()
        legal = g.available_moves(r)
        choice = (
            greedy_policy(legal) if policy == "greedy" else random_policy(legal, g.rng)
        )
        steps.append(
            {
                "t": t,
                "roll": r,
                "open_before": "".join(str(x) for x in g.open_tiles()),
                "legal_count": len(legal),
                "choice": "+".join(map(str, choice)) if choice else "",
            }
        )
        if choice:
            g.move(choice)
        steps[-1]["open_after"] = "".join(str(x) for x in g.open_tiles())
        steps[-1]["score_after"] = g.score()
        steps[-1]["game_over"] = g.over
        t += 1
        if not choice:
            break
    return pd.DataFrame(steps)


def run_many(n=1000, seed=123) -> np.ndarray:
    rng_top = random.Random(seed)
    scores = np.zeros(n, dtype=int)
    for i in range(n):
        g = Game(rng=random.Random(rng_top.randint(0, 10**9)))
        while not g.over:
            r = g.roll()
            legal = g.available_moves(r)
            choice = random_policy(legal, g.rng)
            if choice:
                g.move(choice)
            else:
                break
        scores[i] = g.score()
    return scores


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--episode-seed", type=int, default=21)
    p.add_argument("--episodes", type=int, default=1500)
    p.add_argument("--policy", choices=["greedy", "random"], default="greedy")
    p.add_argument(
        "--no-show",
        action="store_true",
        help="do not show matplotlib window; still saves PNG/CSVs",
    )
    args = p.parse_args()

    # 1) Single episode (table)
    episode_df = run_episode(seed=args.episode_seed, policy=args.policy)
    episode_csv = "episode_timeline.csv"
    episode_df.to_csv(episode_csv, index=False)
    print(f"Wrote {episode_csv}")
    print(episode_df.head(20).to_string(index=False))

    # 2) Monte Carlo: many episodes, score histogram
    scores = run_many(n=args.episodes, seed=7)
    summary = pd.DataFrame(
        {
            "episodes": [len(scores)],
            "mean_score": [scores.mean()],
            "std_score": [scores.std(ddof=1)],
            "shutout_rate_%": [(scores == 0).mean() * 100],
        }
    )
    summary_csv = "score_summary.csv"
    summary.to_csv(summary_csv, index=False)
    print(f"Wrote {summary_csv}")
    print(summary.to_string(index=False))

    # Plot
    plt.figure()
    plt.hist(scores, bins=range(0, 46))
    plt.title("Final Score Distribution (Random Policy)")
    plt.xlabel("Final score (sum of uncovered tiles)")
    plt.ylabel("Frequency")
    plt.tight_layout()
    out_png = "score_hist.png"
    plt.savefig(out_png, dpi=140)
    print(f"Wrote {out_png}")
    if not args.no_show:
        plt.show()


if __name__ == "__main__":
    main()
