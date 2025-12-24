#!/usr/bin/env python3
import csv
import random
from pathlib import Path
from typing import Iterable, Optional, Tuple, List
from tqdm import tqdm

from shutbox.game import Game, TileSet


N_PER = 200_000
OUT = Path("strategy_simulations.csv")

rng = random.Random()  # optional: seed for reproducibility (e.g., random.Random(42))


# --- policies for *your* Game API -------------------------------------


def policy_random(game: Game) -> Optional[TileSet]:
    r = game.roll()
    moves = game.available_moves(r)
    return rng.choice(moves) if moves else None


def policy_greedy_min_remaining(game: Game) -> Optional[TileSet]:
    r = game.roll()
    moves = game.available_moves(r)
    if not moves:
        return None
    # minimize remaining sum after closing chosen tiles
    return min(moves, key=lambda mv: sum(game.open_tiles()) - sum(mv))


def policy_human_like(game: Game) -> Optional[TileSet]:
    r = game.roll()
    moves = game.available_moves(r)
    if not moves:
        return None
    multi = [mv for mv in moves if len(mv) >= 2]
    if multi:
        return min(multi, key=lambda mv: sum(game.open_tiles()) - sum(mv))
    return policy_greedy_min_remaining(game)


STRATEGIES = [
    ("random", policy_random),
    ("greedy", policy_greedy_min_remaining),
    ("human", policy_human_like),
]


def run_one(policy_fn) -> int:
    g = Game()
    while not g.over:
        mv = policy_fn(g)  # policy rolls + picks move
        if mv is None:
            break
        ok = g.move(mv)  # apply chosen tiles to current roll
        if not ok:
            # should never happen; if it does, it's a bug worth surfacing
            raise RuntimeError(
                f"Illegal move {mv} for last_roll={g.last_roll} open={g.open_tiles()}"
            )
    return g.score()


def main():
    with OUT.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["run_id", "strategy", "score"])

        run_id = 0
        for name, fn in STRATEGIES:
            for _ in tqdm(range(N_PER), desc=f"{name} ({N_PER})"):
                score = run_one(fn)
                w.writerow([run_id, name, score])
                run_id += 1

    print(f"Saved: {OUT.resolve()}")


if __name__ == "__main__":
    main()
