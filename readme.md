# Shut the Box: Recreated with Python!

## Description

**Shut the Box** is a dice game where you roll two dice and close numbered tiles that add up to your roll. The goal is to shut all the tiles, or at least leave the lowest possible total uncovered.

I built this project because I wanted to explore the best strategy to win the game, and learn about:

- **Probability**
- **Randomization**
- **Simple game development in Python**

Quick Start

If you just want to see the game in action right away:

# Play one quick text-based game with random moves

`PYTHONPATH=. python scripts/print_demo.py --games 1 --policy random`

---

## Contents

- [Dependencies](#dependencies)
- [Project structure](#project-structure)
- [How to run the game](#how-to-run-the-game)
- [What’s next](#whats-next-for-this-project)

---

## Dependencies needed

This project uses only a few, commonly used Python libraries:

- **pandas**
- **numpy**
- **matplotlib**
- **pytest**

If you want to install everything at once:

`pip install -r requirements.txt`

---

## Project structure

Here’s what each file does:

- `shutbox/game.py` — This is the core game. It handles the rules, rolls dice, tracks which tiles are open/closed after each dice roll, rolls dice, makes moves, and ends the game when no moves remain.

- `tests/test_game.py` — These are automated tests that make sure the rules always work as expected (e.g. illegal moves are rejected, scores are calculated correctly). If I change the game later, tests will catch mistakes.

- `scripts/print_demo.py` — Runs the game in plain text and prints each step (roll, move, tiles left, score).

- `scripts/visual_demo.py` — Data + chart demo. Plays one game step by step in the console and can be used to simulate n number of games. It shows a histogram of final scores and shows how different strategies perform on average.

- `scripts/curses_demo.py` — An animated version in the terminal using `curses`. You can watch the tiles flip down as the game progresses, scroll through the log, or even step through moves manually.

### Strategies (Policies)

The project includes a few ways to “play” automatically:

- **Random policy** — picks any valid move at random.
- **Greedy policy** — prefers the smallest set of tiles, preferring higher numbers when tied.
- **Min-score policy** — picks the move that leaves the lowest possible board score after the turn.

---

## How to run the game

1. **Set up a virtual environment**:

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install pandas numpy matplotlib pytest
   ```

   _(On Windows, you may also need pip install windows-curses if you want to use the curses demo.)_

2. **Run the tests (optional)**  
   To check everything is working before you start playing:

   ```bash
   pytest -q
   ```

3. **Run the visual demo**  
   This version plays one game in the console and then simulates many more to show a histogram of scores.

   ```bash
   PYTHONPATH=. python scripts/visual_demo.py --policy minscore --episodes 500
   ```

   - Use `--policy` to pick a strategy: `random`, `greedy`, or `minscore` (defined above).
   - Use `--episodes` to control how many games to simulate (default is 1500).
   - Add `--no-show` if you want to skip the histogram window and just save the image to `score_hist.png`.

4. **Run the curses demo**  
   This version animates the game in your terminal with a live board and scrolling log.

```bash
   PYTHONPATH=. python scripts/curses_demo.py --policy greedy --games 3
```

- Use `--policy` to pick a strategy: `random`, `greedy`, or `minscore` (defined above).
- Use `--games` to set how many games to play one after another.
- Use `--speed` to adjust the speed of auto-play (default is 0.8 seconds per step).
- Use `--manual` to press a key (n or space) for each step instead of auto-playing.
