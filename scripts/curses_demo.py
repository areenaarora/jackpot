"""
Shut the Box — Curses Demo (log + step mode)
--------------------------------------------
Visual curses-based demo with live board and scrolling log.

Usage examples:
  PYTHONPATH=. python scripts/curses_demo.py --policy greedy
  PYTHONPATH=. python scripts/curses_demo.py --policy minscore --games 3
  PYTHONPATH=. python scripts/curses_demo.py --policy random --speed 0.8
  PYTHONPATH=. python scripts/curses_demo.py --policy greedy --manual
"""

import argparse, curses, random, time
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


# --- Drawing helpers ---
def draw_board(win, g: Game, roll, choice, step):
    win.erase()
    move_str = "+".join(map(str, choice)) if choice else "—"
    tiles = " ".join(
        f"[{i}]" if g.tiles[i] else "[X]" for i in range(1, g.tiles_max + 1)
    )
    win.addstr(0, 0, f"Step: {step}")
    win.addstr(1, 0, f"Roll: {roll}")
    win.addstr(2, 0, f"Move: {move_str}")
    win.addstr(3, 0, f"Score: {g.score()}")
    win.addstr(5, 0, "Tiles:")
    win.addstr(6, 0, tiles)
    win.box()
    win.noutrefresh()


# --- Core loop ---
def curses_game(stdscr, seed, policy, speed, manual):
    curses.curs_set(0)
    stdscr.nodelay(False)
    stdscr.keypad(True)
    H, W = stdscr.getmaxyx()

    header_h = 9
    board = curses.newwin(header_h, W, 0, 0)

    # Log pad
    log_h = max(5, H - header_h - 2)
    logpad = curses.newpad(1000, max(80, W))
    log_start = 0
    log_row = 0

    def log(line):
        nonlocal log_row, log_start
        logpad.addstr(log_row, 0, line[: W - 1])
        log_row += 1
        if log_row > log_h:
            log_start = log_row - log_h
        logpad.noutrefresh(log_start, 0, header_h, 0, header_h + log_h, W - 1)

    def draw_help():
        help_text = (
            "Manual: n/SPACE=next  ↑/↓=scroll  q=quit"
            if manual
            else "Auto: ↑/↓ scroll log, q quits"
        )
        stdscr.addstr(H - 1, 0, help_text.ljust(W - 1))
        stdscr.noutrefresh()

    rng = random.Random(seed) if seed is not None else random.Random()
    g = Game(rng=rng)
    step = 0
    last_choice = tuple()
    last_roll = 0

    while not g.over:
        last_roll = g.roll()
        legal = g.available_moves(last_roll)
        last_choice = choose_move(g, legal, policy, g.rng)

        draw_board(board, g, last_roll, last_choice, step)
        log(
            f"Step {step:>2} | Roll {last_roll:>2} | Move {('+'.join(map(str, last_choice))) if last_choice else '—'} | Open: {''.join(map(str, g.open_tiles()))} | Score: {g.score()}"
        )

        draw_help()
        curses.doupdate()

        if manual:
            while True:
                ch = stdscr.getch()
                if ch in (ord("q"), 27):  # quit
                    return g.score()
                if ch in (ord("n"), ord(" "), curses.KEY_ENTER, 10, 13):
                    break
                if ch == curses.KEY_UP:
                    log_start = max(0, log_start - 1)
                elif ch == curses.KEY_DOWN:
                    log_start = min(max(0, log_row - log_h), log_start + 1)
                logpad.noutrefresh(log_start, 0, header_h, 0, header_h + log_h, W - 1)
                curses.doupdate()
        else:
            # auto mode
            t0 = time.time()
            while time.time() - t0 < speed:
                stdscr.nodelay(True)
                ch = stdscr.getch()
                stdscr.nodelay(False)
                if ch == ord("q"):
                    return g.score()
                if ch == curses.KEY_UP:
                    log_start = max(0, log_start - 1)
                elif ch == curses.KEY_DOWN:
                    log_start = min(max(0, log_row - log_h), log_start + 1)
                logpad.noutrefresh(log_start, 0, header_h, 0, header_h + log_h, W - 1)
                curses.doupdate()
                time.sleep(0.02)

        if last_choice:
            g.move(last_choice)
        step += 1

    draw_board(board, g, last_roll, last_choice, step)
    log(f"Game over. Final score: {g.score()}")
    draw_help()
    stdscr.refresh()
    time.sleep(1.5)  # short pause before auto-advance
    return g.score()


# --- Entrypoint ---
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--games", type=int, default=1, help="Number of games to play")
    ap.add_argument("--seed", type=int, default=None)
    ap.add_argument(
        "--policy", choices=["greedy", "random", "minscore"], default="greedy"
    )
    ap.add_argument(
        "--speed", type=float, default=0.8, help="seconds between steps (auto mode)"
    )
    ap.add_argument(
        "--manual", action="store_true", help="press a key to advance each step"
    )
    args = ap.parse_args()

    scores = []
    for g in range(args.games):
        score = curses.wrapper(
            curses_game,
            seed=args.seed,
            policy=args.policy,
            speed=args.speed,
            manual=args.manual,
        )
        scores.append(score)

    print("\n=== Summary ===")
    print(f"Games played: {len(scores)}")
    print(f"Average score: {sum(scores) / len(scores):.2f}")
    print(f"Shutouts (score=0): {sum(s == 0 for s in scores)}")


if __name__ == "__main__":
    main()
