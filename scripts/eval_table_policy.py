# scripts/eval_table_policy.py
import argparse
from shutbox.game import Game
from shutbox.policies import table_policy_loader
from statistics import mean, pstdev


def find_move_fn(g):
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
        fn = getattr(g, name, None)
        if callable(fn):
            return fn
    raise AttributeError("No move function found on Game")


def run(episodes, table_path):
    pick_move = table_policy_loader(table_path)
    scores = []

    for _ in range(episodes):
        g = Game()
        do_move = find_move_fn(g)
        while True:
            mv = pick_move(g)
            if not mv:
                break
            do_move(mv)
        score = g.score() if callable(getattr(g, "score", None)) else g.score
        scores.append(int(score))

    print(
        f"episodes {episodes}  mean_score {mean(scores):.3f}  std {pstdev(scores):.3f}  shutout_rate_% {100 * sum(s == 0 for s in scores) / len(scores):.1f}"
    )


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--policy-file", required=True)
    ap.add_argument("--episodes", type=int, default=1000)
    args = ap.parse_args()
    run(args.episodes, args.policy_file)
