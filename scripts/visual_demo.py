"""
Shut the Box — Visual Demo (animated console view)
--------------------------------------------------
Runs a step-by-step episode, printing the board each turn,
and a Monte Carlo batch to plot score distribution.

Usage (random every time):
  PYTHONPATH=. python scripts/visual_demo.py --policy minscore

Optional reproducibility:
  PYTHONPATH=. python scripts/visual_demo.py --episode-seed 21 --batch-seed 7 --episodes 2000 --no-show
"""

import argparse
import random
import time
from typing import Tuple, List, Optional
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from shutbox.game import Game

TileSet = Tuple[int, ...]


# --- Policies ---
def greedy_policy(legal_moves: List[TileSet]) -> TileSet:
    """Prefer fewer tiles; if tie, prefer the move with the largest tile."""
    if not legal_moves:
        return tuple()
    legal_moves = sorted(legal_moves, key=lambda c: (len(c), -max(c)))
    return legal_moves[0]


def random_policy(legal_moves: List[TileSet], rng: random.Random) -> TileSet:
    """Pick any legal move uniformly at random."""
    return rng.choice(legal_moves) if legal_moves else tuple()


def min_score_policy(g: Game, legal_moves: List[TileSet]) -> TileSet:
    """
    Choose the legal move that minimizes the board's score after the move.
    Ties are broken by preferring fewer tiles.
    """
    if not legal_moves:
        return tuple()

    best_move: Optional[TileSet] = None
    best_score = float("inf")

    for move in legal_moves:
        # simulate: close tiles in a copy of the board and compute score
        temp_tiles = g.tiles.copy()
        for t in move:
            temp_tiles[t] = False
        score_after = sum(i for i, is_open in temp_tiles.items() if is_open)

        if (score_after < best_score) or (
            score_after == best_score
            and (best_move is None or len(move) < len(best_move))
        ):
            best_move = move
            best_score = score_after

    return best_move if best_move is not None else tuple()


# --- Helpers ---
def print_board(g: Game, roll: int, choice: TileSet, delay: float = 0.8):
    board = " ".join(str(i) if g.tiles[i] else "X" for i in range(1, g.tiles_max + 1))
    move_str = "+".join(map(str, choice)) if choice else "—"
    print(
        f"Roll: {roll:>2} | Move: {move_str:<5} | Tiles: {board} | Score: {g.score()}"
    )
    time.sleep(delay)


def choose_move(g: Game, legal: List[TileSet], policy: str) -> TileSet:
    if policy == "greedy":
        return greedy_policy(legal)
    if policy == "minscore":
        return min_score_policy(g, legal)
    # default: random
    return random_policy(legal, g.rng)


# --- Runners ---
def run_episode(
    seed: Optional[int] = None, policy: str = "greedy", animate: bool = True
) -> pd.DataFrame:
    # Random by default; seed only if provided
    rng = random.Random(seed) if seed is not None else random.Random()
    g = Game(rng=rng)

    steps = []
    t = 0
    while not g.over:
        r = g.roll()
        legal = g.available_moves(r)
        choice = choose_move(g, legal, policy)
        if animate:
            print_board(g, r, choice)
        if choice:
            g.move(choice)
        steps.append(
            {
                "t": t,
                "roll": r,
                "choice": "+".join(map(str, choice)) if choice else "",
                "open_after": "".join(str(x) for x in g.open_tiles()),
                "score_after": g.score(),
                "game_over": g.over,
            }
        )
        t += 1
        if not choice:
            break
    return pd.DataFrame(steps)


def run_many(
    n: int = 1000, seed: Optional[int] = None, policy: str = "random"
) -> np.ndarray:
    """
    Simulate n games and return final scores.
    Random by default. If 'seed' is provided, derive per-game RNGs deterministically.
    """
    scores = np.zeros(n, dtype=int)
    rng_top = random.Random(seed) if seed is not None else None

    for i in range(n):
        per_game_rng = (
            random.Random()
            if rng_top is None
            else random.Random(rng_top.randint(0, 10**9))
        )
        g = Game(rng=per_game_rng)
        while not g.over:
            r = g.roll()
            legal = g.available_moves(r)
            choice = choose_move(g, legal, policy)
            if choice:
                g.move(choice)
            else:
                break
        scores[i] = g.score()
    return scores


def main():
    p = argparse.ArgumentParser()
    p.add_argument(
        "--episode-seed",
        type=int,
        default=None,
        help="Optional seed for the single displayed episode",
    )
    p.add_argument(
        "--episodes",
        type=int,
        default=1500,
        help="How many games to simulate for the histogram",
    )
    p.add_argument(
        "--batch-seed",
        type=int,
        default=None,
        help="Optional seed for the batch simulator",
    )
    p.add_argument(
        "--policy",
        choices=["greedy", "random", "minscore"],
        default="greedy",
        help="Move selection rule",
    )
    p.add_argument("--no-show", action="store_true")
    p.add_argument("--no-animate", action="store_true")
    args = p.parse_args()

    # 1) Single episode with console animation
    print("\n=== Playing one episode ===")
    episode_df = run_episode(
        seed=args.episode_seed, policy=args.policy, animate=not args.no_animate
    )
    print("\nFinal score:", episode_df.iloc[-1]["score_after"])
    print("Game over.\n")

    # 2) Monte Carlo: many episodes, score histogram (using SAME policy)
    scores = run_many(n=args.episodes, seed=args.batch_seed, policy=args.policy)
    summary = pd.DataFrame(
        {
            "episodes": [len(scores)],
            "mean_score": [scores.mean()],
            "std_score": [scores.std(ddof=1)],
            "shutout_rate_%": [(scores == 0).mean() * 100],
        }
    )
    summary.to_csv("score_summary.csv", index=False)
    print(summary.to_string(index=False))

    plt.figure()
    plt.hist(scores, bins=range(0, 46))
    plt.title(f"Final Score Distribution ({args.policy} policy)")
    plt.xlabel("Final score (sum of uncovered tiles)")
    plt.ylabel("Frequency")
    plt.tight_layout()
    plt.savefig("score_hist.png", dpi=140)
    if not args.no_show:
        plt.show()


if __name__ == "__main__":
    main()
