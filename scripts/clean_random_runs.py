import pandas as pd

df = pd.read_csv("run_results/random_runs.csv")

# Remove stray bound method text
df["roll"] = df["roll"].astype(str).str.extract(r"(\d+)").astype(float)
df["final_score"] = df["final_score"].astype(str).str.extract(r"(\d+)").astype(float)

df.to_csv("run_results/random_runs_clean.csv", index=False)
print("✅ Cleaned and saved to run_results/random_runs_clean.csv")
