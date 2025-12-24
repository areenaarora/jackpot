# scripts/policy_from_csv.py
import pandas as pd
import json
import argparse
from collections import defaultdict


def learn_policy(in_csv, min_count=3):
    df = pd.read_csv(in_csv)

    # only keep valid moves
    df = df[df["chosen_move"].notna() & (df["chosen_move"] != "")]

    # average score per state + move
    stats = (
        df.groupby(["tiles_before", "roll", "chosen_move"])["final_score"]
        .mean()
        .reset_index()
    )

    # select best move per (tiles_before, roll)
    best_moves = {}
    for (tb, roll), group in stats.groupby(["tiles_before", "roll"]):
        # pick move with lowest avg final score
        best = group.loc[group["final_score"].idxmin()]
        best_moves[f"{tb}|{int(roll)}"] = best["chosen_move"]

    return best_moves


def main(in_csv, out_json):
    best_moves = learn_policy(in_csv)
    with open(out_json, "w") as f:
        json.dump(best_moves, f, indent=2)
    print(f"✅ Learned {len(best_moves)} state→move pairs saved to {out_json}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="in_csv", default="run_results/random_runs_clean.csv")
    ap.add_argument("--out", dest="out_json", default="run_results/policy_table.json")
    args = ap.parse_args()
    main(args.in_csv, args.out_json)
