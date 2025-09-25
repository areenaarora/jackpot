#!/usr/bin/env python3
"""
Shut the Box — Print Demo
-------------------------
Plays the game in text mode and prints every step.

Usage:
  PYTHONPATH=. python scripts/print_demo.py --games 5 --policy minscore
"""

import argparse
import random
from shutbox.game import Game


# --- Policies ---
def greedy_policy(legal_moves):
    if not legal_moves:
        return tuple()
    return sorted(legal_moves, key=lambda c: (len(c), -max(c)))[0]


def random_policy(legal_moves, rng):
    return rng.choice(legal_moves) if legal_moves else tuple()


def min_score_policy(g: Game, legal_moves):
    if not legal_moves:
        return tuple()
    best_move = None
    best_score = float("inf")
    for move in legal_moves:
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
    return best_move


def choose_move(g: Game, legal, policy, rng):
    if policy == "greedy":
        return greedy_policy(legal)
    if policy == "minscore":
        return min_score_policy(g, legal)
    return random_policy(legal, rng)


# --- Gameplay ---
def play_once(seed=None, policy="greedy"):
    rng = random.Random(seed) if seed is not None else random.Random()
    g = Game(rng=rng)
    step = 0
    print(f"\n=== New Game (policy={policy}) ===")
    while not g.over:
        roll = g.roll()
        legal = g.available_moves(roll)
        choice = choose_move(g, legal, policy, g.rng)
        tiles_str = " ".join(
            str(i) if g.tiles[i] else "X" for i in range(1, g.tiles_max + 1)
        )
        move_str = "+".join(map(str, choice)) if choice else "—"
        print(
            f"Step {step:>2} | Roll: {roll:>2} | Move: {move_str:<5} | Tiles: {tiles_str} | Score: {g.score()}"
        )
        if choice:
            g.move(choice)
        step += 1
    print(f"Game over! Final score = {g.score()}\n")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--games", type=int, default=2, help="Number of games to play")
    parser.add_argument(
        "--policy", choices=["greedy", "random", "minscore"], default="greedy"
    )
    args = parser.parse_args()
    for i in range(args.games):
        play_once(seed=None, policy=args.policy)


if __name__ == "__main__":
    main()
