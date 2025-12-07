#!/usr/bin/env python3
"""Generate a belief-updates figure from a representative trace JSON.

Saves `docs/figures/belief_updates.png` illustrating posterior trajectories
for warmth and competence across turns for a single example episode.
"""
from __future__ import annotations

import json
from pathlib import Path
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
TRACE_DIR = ROOT / "results" / "week7" / "traces"
OUT = ROOT / "docs" / "figures" / "belief_updates.png"


def pick_trace(trace_dir: Path) -> Path:
    traces = sorted(trace_dir.glob("trace_*.json"))
    if not traces:
        raise FileNotFoundError("No trace files found in " + str(trace_dir))
    return traces[0]


def load_beliefs(trace_path: Path):
    with trace_path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    warmth = [step["beliefs"]["warmth"] for step in data.get("steps", [])]
    competence = [step["beliefs"]["competence"] for step in data.get("steps", [])]
    turns = list(range(1, len(warmth) + 1))
    return turns, warmth, competence, data.get("episode_id", trace_path.stem)


def plot_beliefs(turns, warmth, competence, episode_id):
    try:
        plt.style.use("seaborn-whitegrid")
    except Exception:
        # Fallback to default style if seaborn is not available
        pass
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot(turns, warmth, marker="o", label="Warmth", color="#1f77b4")
    ax.plot(turns, competence, marker="s", label="Competence", color="#ff7f0e")
    ax.set_xlabel("Turn")
    ax.set_ylabel("Posterior (probability)")
    ax.set_title(f"Belief Trajectories — {episode_id}")
    ax.set_ylim(0, 1)
    ax.legend()
    fig.tight_layout()
    return fig


def main():
    trace = pick_trace(TRACE_DIR)
    turns, warmth, competence, eid = load_beliefs(trace)
    fig = plot_beliefs(turns, warmth, competence, eid)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT, dpi=300)
    print(f"Saved belief figure to {OUT}")


if __name__ == "__main__":
    main()
