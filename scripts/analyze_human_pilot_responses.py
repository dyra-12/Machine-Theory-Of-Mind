from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "human_pilot" / "pilot_ratings.csv"
RESULTS_DIR = Path(__file__).resolve().parent.parent / "results" / "week10"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

if not DATA_PATH.exists():
    raise FileNotFoundError(f"Could not find responses at {DATA_PATH}")

print(f"Loading responses from {DATA_PATH}")
responses = pd.read_csv(DATA_PATH)
responses.to_csv(RESULTS_DIR / "pilot_ratings_combined.csv", index=False)

averages = (
    responses.groupby("agent_type")[["warmth", "competence", "trust"]]
    .mean()
    .round(2)
)
averages.to_csv(RESULTS_DIR / "agent_means.csv")

print("Average ratings by agent type:")
print(averages)

fig, ax = plt.subplots(figsize=(8, 5))
averages.plot(kind="bar", ax=ax)
ax.set_ylabel("Average rating")
ax.set_xlabel("Agent type")
ax.set_title("Average warmth, competence, and trust by agent type")
ax.set_ylim(0, 7.5)
ax.legend(title="Metric")
plt.tight_layout()
plot_path = RESULTS_DIR / "agent_comparison.png"
fig.savefig(plot_path)
print(f"Saved comparison plot to {plot_path}")
