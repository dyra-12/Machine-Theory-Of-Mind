"""Extended sweep to improve statistical reliability.

Runs more seeds across opponent policies, aggregates mean/std/n per turn,
flags outliers (z-score) and writes CSV + plot with error bars.
"""
from pathlib import Path
import sys
import json
import statistics
import csv
import math
import matplotlib.pyplot as plt

# Ensure `src` importable
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.experiments.week7_trace_runner import run_traceable_episode, TraceConfig


def run_extended_sweep(seeds=range(1, 51), opponents=("fair", "greedy", "generous")):
    out_dir = Path("results/week7")
    plots_dir = out_dir / "plots"
    csv_dir = out_dir / "summaries"
    plots_dir.mkdir(parents=True, exist_ok=True)
    csv_dir.mkdir(parents=True, exist_ok=True)

    per_turn = {}
    traces = []

    for opp in opponents:
        for s in seeds:
            cfg = TraceConfig()
            cfg.opponent_type = opp
            info = run_traceable_episode(seed=int(s), config=cfg)
            path = Path(info["trace_path"]).resolve()
            data = json.load(open(path))
            traces.append((opp, s, data))

            for step in data.get("steps", []):
                t = int(step.get("turn", 0))
                sc = step.get("social_score")
                if sc is None:
                    continue
                per_turn.setdefault((opp, t), []).append(float(sc))

    # Aggregate and compute z-scores to flag outliers (per opponent-turn)
    rows = []
    for (opp, t), vals in sorted(per_turn.items()):
        n = len(vals)
        meanv = statistics.mean(vals)
        stdv = statistics.pstdev(vals) if n > 1 else 0.0
        # compute z-scores for each sample relative to group
        outlier_flags = []
        if stdv > 0:
            for v in vals:
                z = (v - meanv) / stdv
                outlier_flags.append(abs(z) > 3.0)
        else:
            outlier_flags = [False] * n

        rows.append({
            "opponent": opp,
            "turn": t,
            "n": n,
            "mean": meanv,
            "std": stdv,
            "num_outliers": sum(outlier_flags),
        })

    # Write CSV summary
    csv_path = csv_dir / "social_score_summary_extended.csv"
    with csv_path.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["opponent", "turn", "n", "mean", "std", "num_outliers"])
        w.writeheader()
        for r in rows:
            w.writerow(r)

    # Plot mean +/- stderr by opponent
    fig, ax = plt.subplots(figsize=(8, 5))
    opp_grouped = {}
    for r in rows:
        opp_grouped.setdefault(r["opponent"], []).append(r)

    for opp, vals in opp_grouped.items():
        vals_sorted = sorted(vals, key=lambda x: x["turn"])
        xs = [v["turn"] for v in vals_sorted]
        ys = [v["mean"] for v in vals_sorted]
        errs = [ (v["std"] / math.sqrt(v["n"])) if v["n"]>0 else 0.0 for v in vals_sorted]
        ax.errorbar(xs, ys, yerr=errs, marker='o', capsize=3, label=f"{opp} (n~{int(sum(v['n'] for v in vals)/len(vals))})")

    ax.set_xlabel('Turn index')
    ax.set_ylabel('Mean social_score')
    ax.set_title('Social score vs turn (extended sweep)')
    ax.legend()
    ax.grid(True)
    plot_path = plots_dir / 'social_score_vs_turn_extended.png'
    fig.savefig(plot_path, dpi=150)

    print('Wrote CSV summary to', csv_path)
    print('Saved extended plot to', plot_path)


if __name__ == '__main__':
    run_extended_sweep()
