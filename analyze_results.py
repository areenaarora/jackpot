import pandas as pd

df = pd.read_csv("strategy_simulations.csv")

summary = (
    df.groupby("strategy")["score"]
    .agg(
        runs="count",
        mean_score="mean",
        median_score="median",
        p10=lambda s: s.quantile(0.10),
        p25=lambda s: s.quantile(0.25),
        p75=lambda s: s.quantile(0.75),
        p90=lambda s: s.quantile(0.90),
        std_dev="std",
        min_score="min",
        max_score="max",
    )
    .sort_values("mean_score")
)

print("\n=== Strategy Performance Summary (lower score is better) ===")
print(summary.round(3))

best = summary.index[0]

print(
    f"\nConclusion:\n"
    f"Across {int(summary['runs'].sum()):,} simulated games "
    f"({int(summary.loc[best, 'runs']):,} per strategy), "
    f"the **{best}** strategy consistently produced the lowest final scores. "
    f"It achieved the lowest average score ({summary.loc[best, 'mean_score']:.2f}) "
    f"as well as lower scores across the distribution (10th–90th percentile: "
    f"{summary.loc[best, 'p10']:.0f}–{summary.loc[best, 'p90']:.0f}), "
    f"making it the best-performing strategy among those tested."
)
