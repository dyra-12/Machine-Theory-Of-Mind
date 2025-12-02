"""Run a small sweep over seeds and opponent policies and plot social_score vs turn.

Produces a CSV summary and a PNG plot under `results/week7/plots` and stores traces
under `results/week7/traces` (existing behavior).
"""
from pathlib import Path
import sys
import json
import statistics
import matplotlib.pyplot as plt

# Ensure `src` package is importable when running this script directly
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.experiments.week7_trace_runner import run_traceable_episode, TraceConfig


def run_sweep(seeds=(1, 2, 3, 4, 5), opponents=("fair", "greedy", "generous")):
    out_dir = Path("results/week7")
    plots_dir = out_dir / "plots"
    plots_dir.mkdir(parents=True, exist_ok=True)

    # Collect per-turn social scores across episodes
    per_turn_scores = {}
    episodes = []

    for opp in opponents:
        for s in seeds:
            cfg = TraceConfig()
            cfg.opponent_type = opp
            info = run_traceable_episode(seed=s, config=cfg)
            path = Path(info["trace_path"])
            data = json.load(path.open())
            episodes.append((opp, s, data))

            for step in data.get("steps", []):
                t = int(step.get("turn", 0))
                score = step.get("social_score")
                if score is None:
                    continue
                per_turn_scores.setdefault((opp, t), []).append(float(score))

    # Build a simple aggregated series per opponent: mean social_score per turn
    series = {}
    max_turn = 0
    for (opp, t), vals in per_turn_scores.items():
        series.setdefault(opp, {})[t] = statistics.mean(vals)
        max_turn = max(max_turn, t)

    # Plot
    fig, ax = plt.subplots(figsize=(6, 4))
    for opp, mapping in series.items():
        xs = sorted(mapping.keys())
        ys = [mapping[x] for x in xs]
        ax.plot(xs, ys, marker='o', label=opp)

    ax.set_xlabel('Turn index')
    ax.set_ylabel('Mean social_score')
    ax.set_title('Social score vs turn (mean across seeds)')
    ax.legend()
    ax.grid(True)

    plot_path = plots_dir / 'social_score_vs_turn.png'
    fig.savefig(plot_path, dpi=150)
    print('Saved plot to', plot_path)


if __name__ == '__main__':
    run_sweep()
