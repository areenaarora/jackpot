# Shut the Box — Digital Game Engine

This repository contains a Python implementation of the **one-player Shut the Box** game, complete with automated tests and a visual demo for exploration.

## Project Structure

shutbox/
game.py # Core game engine (rules + state machine)
tests/
test_game.py # Pytest suite for game engine
scripts/
visual_demo.py # CLI demo: step-by-step episode + score histogram

## 1. Core Engine (`game.py`)

Implements the game rules:

- Tiles 1–9 (optionally more, via `tiles_max`).
- Dice rolls: must roll two dice unless 7–9 are closed, then the player may choose 1 or 2 dice.
- Valid moves: any combination of open tiles that sums to the roll.
- Game ends when no legal moves remain or all tiles are closed.
- Score = sum of uncovered tiles (0 = perfect shut).

Key methods:

- `Game.roll()` — roll dice (with optional `forced` for testing).
- `Game.move([...])` — apply a move if legal.
- `Game.available_moves(target)` — list of legal combos for a roll.
- `Game.state()` — dictionary snapshot of current state.

## 2. Tests (`test_game.py`)

Automated test suite using **pytest** to validate:

- Initial state is correct.
- Illegal vs. legal moves are handled properly.
- Must roll 2 dice until 7–9 are closed; then 1 or 2 dice allowed.
- Forced rolls behave deterministically.
- Scripted play paths run consistently.

Run tests with:

```bash
pytest -q

3. Visual Demo (scripts/visual_demo.py)

Command-line script that:

Runs one episode step-by-step (saving a timeline CSV).

Simulates many episodes to plot a final-score histogram.

Outputs summary stats (mean, std, shutout rate).

Saves episode_timeline.csv, score_summary.csv, and score_hist.png.

# Create environment
python3 -m venv .venv
source .venv/bin/activate
pip install pandas numpy matplotlib pytest

# Run demo (greedy policy, 1500 episodes, seed=21)
python scripts/visual_demo.py --episode-seed 21 --episodes 1500

# Run with random policy
python scripts/visual_demo.py --policy random

## Next Steps
This codebase is the foundation for:
- Exploring heuristics for Shut the Box.
- Collecting simulation data for strategy analysis.
- Serving as an environment for future machine-learning experiments (e.g. reinforcement learning).
- Building a frontend (Svelte/JS) version by reusing the same rules.
```
