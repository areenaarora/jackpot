# scripts/collect_runs.py
import csv, argparse, random
from pathlib import Path
from shutbox.game import Game


# ---------- helpers ----------
def _call_or_val(x):
    return x() if callable(x) else x


def _find_move_fn(game):
    # try common names
    for name in [
        "apply",
        "move",
        "make_move",
        "play",
        "step",
        "apply_move",
        "play_move",
        "take_move",
        "act",
    ]:
        fn = getattr(game, name, None)
        if callable(fn):
            return fn
    # helpful error
    avail = [
        m for m in dir(game) if callable(getattr(game, m)) and not m.startswith("_")
    ]
    raise AttributeError(
        f"Game has no known move function. Available callables: {avail}"
    )


def open_tiles_list(game):
    tiles = game.tiles
    if isinstance(tiles, dict):
        return [t for t, is_open in tiles.items() if is_open]
    return [t for t in tiles if t is not None]


def tiles_to_str(game):
    tiles_max = getattr(game, "tiles_max", 9)
    tiles = game.tiles
    if isinstance(tiles, dict):
        return "".join(
            str(i) if tiles.get(i, False) else "X" for i in range(1, tiles_max + 1)
        )
    present = set(t for t in tiles if t is not None)
    return "".join(str(i) if i in present else "X" for i in range(1, tiles_max + 1))


def compute_legal_moves(game, roll_val):
    opens = open_tiles_list(game)
    moves = [[t] for t in opens if t == roll_val]
    n = len(opens)
    for i in range(n):
        for j in range(i + 1, n):
            a, b = opens[i], opens[j]
            if a + b == roll_val:
                moves.append([a, b])
    return moves


def remaining_sum_after(game, mv):
    opens = open_tiles_list(game)
    return sum(opens) - sum(mv or [])


# ---------- main ----------
def run(episodes, out_csv):
    out = Path(out_csv)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(
            [
                "episode",
                "step",
                "roll",
                "tiles_before",
                "legal_moves",
                "chosen_move",
                "tiles_after",
                "remaining_sum_after",
                "terminal",
                "final_score",
            ]
        )

        for ep in range(episodes):
            g = Game()
            do_move = _find_move_fn(g)
            step = 0
            while True:
                roll_val = int(_call_or_val(getattr(g, "roll")))
                legal = compute_legal_moves(g, roll_val)
                tiles_before = tiles_to_str(g)

                if not legal:
                    w.writerow(
                        [
                            ep,
                            step,
                            roll_val,
                            tiles_before,
                            "",
                            "",
                            tiles_before,
                            remaining_sum_after(g, None),
                            True,
                            int(_call_or_val(getattr(g, "score"))),
                        ]
                    )
                    break

                mv = random.choice(legal)
                do_move(mv)  # <- call the detected move method
                tiles_after = tiles_to_str(g)

                legal_str = ";".join("+".join(map(str, m)) for m in legal)
                chosen_str = "+".join(map(str, mv))
                w.writerow(
                    [
                        ep,
                        step,
                        roll_val,
                        tiles_before,
                        legal_str,
                        chosen_str,
                        tiles_after,
                        remaining_sum_after(g, mv),
                        False,
                        int(_call_or_val(getattr(g, "score"))),
                    ]
                )
                step += 1


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--episodes", type=int, default=100)
    ap.add_argument("--out", default="run_results/random_runs.csv")
    args = ap.parse_args()
    print(f"Simulating {args.episodes} episodes …")
    run(args.episodes, args.out)
    print(f"Done. Wrote {args.out}")
