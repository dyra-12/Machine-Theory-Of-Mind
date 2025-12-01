"""Week 5 Analysis Script

Ingests the Week 5 Bayesian sweep results and produces:
- Classic generalization / robustness metrics (reuse of Week 4 metrics)
- Hyperparameter grid summary per (prior_strength, lambda)
- Pareto plots highlighting trade-offs (utility vs adaptation, utility vs robustness)
- Summary JSON for downstream reporting
"""

from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, List

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

RAW_PATH = Path("results/week5/raw/bayesian_sweep/results.jsonl")
OUT_DIR = Path("results/week5")
PLOT_DIR = OUT_DIR / "plots"


# ---------------------------------------------------------------------------
# Shared metric helpers (ported from Week 4 script so Week 5 stays standalone)
# ---------------------------------------------------------------------------

def load_results(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"No Week 5 sweep results found at {path}")
    with path.open("r") as f:
        rows = [json.loads(line) for line in f if line.strip()]
    df = pd.DataFrame(rows)
    if "prior_strength" in df.columns:
        df["prior_strength"] = pd.to_numeric(df["prior_strength"], errors="coerce")
    return df


def compute_generalization_score(df: pd.DataFrame) -> Dict[str, float]:
    scores: Dict[str, float] = {}
    for agent in df["agent_type"].unique():
        sub = df[df["agent_type"] == agent]
        mean_all = sub["total_utility"].mean()
        base_mask = (
            (sub["observer_type"] == "simple")
            & (sub["env_name"] == "small_resources")
            & (sub["opponent_type"] == "fair")
        )
        if base_mask.sum() == 0:
            scores[agent] = float("nan")
            continue
        mean_base = sub.loc[base_mask, "total_utility"].mean()
        scores[agent] = float(mean_all / mean_base) if mean_base else float("nan")
    return scores


def compute_robustness_index(df: pd.DataFrame) -> Dict[str, float]:
    idx: Dict[str, float] = {}
    for agent in df["agent_type"].unique():
        vals = df.loc[df["agent_type"] == agent, "total_utility"].values
        mean = vals.mean()
        std = vals.std()
        if mean <= 0:
            idx[agent] = 0.0
        else:
            cv = std / mean
            idx[agent] = float(1.0 / (1.0 + cv))
    return idx


def compute_adaptation_speed(df: pd.DataFrame) -> Dict[str, float]:
    speed: Dict[str, float] = {}
    for agent in df["agent_type"].unique():
        sub = df[df["agent_type"] == agent]
        short = sub[sub["env_name"] == "short_horizon"]["total_utility"].mean()
        long = sub[sub["env_name"] == "long_horizon"]["total_utility"].mean()
        speed[agent] = float(long - short)
    return speed


def compute_cross_task_transfer(df: pd.DataFrame) -> Dict[str, float]:
    transfer: Dict[str, float] = {}
    for agent in df["agent_type"].unique():
        sub = df[df["agent_type"] == agent]
        base = sub[sub["env_name"] == "small_resources"]["total_utility"].mean()
        other = sub[sub["env_name"] != "small_resources"]["total_utility"].mean()
        transfer[agent] = float(other / base) if base else float("nan")
    return transfer


def compute_easy_hard_delta(sub: pd.DataFrame) -> Dict[str, float]:
    easy_mask = (sub["observer_type"] == "simple") & (sub["opponent_type"] == "fair")
    hard_mask = (sub["observer_type"] == "harsh") & (sub["opponent_type"] == "unpredictable")
    easy = sub.loc[easy_mask, "total_utility"].mean()
    hard = sub.loc[hard_mask, "total_utility"].mean()
    return {
        "easy_mean": float(easy),
        "hard_mean": float(hard),
        "delta": float(hard - easy),
    }


def adaptation_speed_subset(sub: pd.DataFrame) -> float:
    short = sub[sub["env_name"] == "short_horizon"]["total_utility"].mean()
    long = sub[sub["env_name"] == "long_horizon"]["total_utility"].mean()
    return float(long - short)


def robustness_subset(sub: pd.DataFrame) -> float:
    vals = sub["total_utility"].values
    mean = vals.mean()
    std = vals.std()
    if mean <= 0:
        return 0.0
    return float(1.0 / (1.0 + std / mean))


# ---------------------------------------------------------------------------
# Hyperparameter sweep summarization
# ---------------------------------------------------------------------------

@dataclass
class ComboSummary:
    lambda_social: float
    prior_strength: float
    mean_total_utility: float
    utility_std: float
    robustness_index: float
    adaptation_speed: float
    easy_mean: float
    hard_mean: float
    hard_delta: float
    utility_gap_vs_simple: float
    is_pareto_utility_adapt: bool = False
    is_pareto_utility_robust: bool = False


def summarize_simple_baseline(df: pd.DataFrame) -> Dict[str, float]:
    simple = df[df["agent_type"] == "simple_mtom"].copy()
    if simple.empty:
        return {"best_lambda": float("nan"), "mean_total_utility": float("nan")}
    grouped = simple.groupby("lambda_social")["total_utility"].mean()
    best_lambda = float(grouped.idxmax())
    best_utility = float(grouped.max())
    return {"best_lambda": best_lambda, "mean_total_utility": best_utility}


def summarize_bayesian_grid(df: pd.DataFrame, simple_ref: float) -> List[ComboSummary]:
    bayes = df[df["agent_type"] == "bayesian_mtom"].copy()
    bayes = bayes.dropna(subset=["prior_strength"])
    summaries: List[ComboSummary] = []

    for (lam, prior), sub in bayes.groupby(["lambda_social", "prior_strength"]):
        mean_utility = float(sub["total_utility"].mean())
        utility_std = float(sub["total_utility"].std())
        robustness = robustness_subset(sub)
        adapt = adaptation_speed_subset(sub)
        easy_hard = compute_easy_hard_delta(sub)
        gap_vs_simple = mean_utility - simple_ref if np.isfinite(simple_ref) else float("nan")

        summaries.append(
            ComboSummary(
                lambda_social=float(lam),
                prior_strength=float(prior),
                mean_total_utility=mean_utility,
                utility_std=utility_std,
                robustness_index=robustness,
                adaptation_speed=adapt,
                easy_mean=easy_hard["easy_mean"],
                hard_mean=easy_hard["hard_mean"],
                hard_delta=easy_hard["delta"],
                utility_gap_vs_simple=gap_vs_simple,
            )
        )
    return summaries


def mark_pareto_front(points: List[ComboSummary], x_key: str, y_key: str, attr_name: str) -> None:
    finite_points = [p for p in points if np.isfinite(getattr(p, x_key)) and np.isfinite(getattr(p, y_key))]
    sorted_pts = sorted(finite_points, key=lambda p: getattr(p, x_key), reverse=True)
    best_y = -np.inf
    for p in sorted_pts:
        y = getattr(p, y_key)
        if y >= best_y - 1e-9:
            setattr(p, attr_name, True)
            best_y = max(best_y, y)
        else:
            setattr(p, attr_name, False)


def plot_pareto(points: List[ComboSummary], x_key: str, y_key: str, filename: Path, label_y: str, attr_name: str):
    PLOT_DIR.mkdir(parents=True, exist_ok=True)
    plt.figure(figsize=(6, 4))
    for p in points:
        x = getattr(p, x_key)
        y = getattr(p, y_key)
        if not np.isfinite(x) or not np.isfinite(y):
            continue
        is_pareto = getattr(p, attr_name, False)
        marker = "o" if is_pareto else "x"
        alpha = 1.0 if is_pareto else 0.5
        label = f"λ={p.lambda_social:.1f}, prior={p.prior_strength:.1f}"
        plt.scatter(x, y, marker=marker, alpha=alpha, label=label if is_pareto else None)
    plt.xlabel("Mean total utility")
    plt.ylabel(label_y)
    plt.title(f"Pareto: {y_key.replace('_', ' ')}")
    if any(getattr(p, attr_name, False) for p in points):
        plt.legend(fontsize=7, bbox_to_anchor=(1.02, 1), loc="upper left")
    plt.tight_layout()
    plt.savefig(filename)
    plt.close()


def plot_heatmap(points: List[ComboSummary], value_key: str, filename: Path, title: str):
    pivot = pd.DataFrame([asdict(p) for p in points])
    table = pivot.pivot_table(
        index="prior_strength",
        columns="lambda_social",
        values=value_key,
        aggfunc="mean",
    )
    plt.figure(figsize=(6, 4))
    im = plt.imshow(table.values, aspect="auto", cmap="viridis")
    plt.colorbar(im, label=value_key.replace("_", " ").title())
    plt.xticks(range(len(table.columns)), [f"{v:.1f}" for v in table.columns])
    plt.yticks(range(len(table.index)), [f"{v:.1f}" for v in table.index])
    plt.xlabel("lambda_social")
    plt.ylabel("prior_strength")
    plt.title(title)
    plt.tight_layout()
    plt.savefig(filename)
    plt.close()


def save_summary(
    generalization: Dict[str, float],
    robustness: Dict[str, float],
    adaptation: Dict[str, float],
    transfer: Dict[str, float],
    simple_ref: Dict[str, float],
    combos: List[ComboSummary],
):
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "generalization_score": generalization,
        "robustness_index": robustness,
        "adaptation_speed": adaptation,
        "cross_task_transfer": transfer,
        "simple_baseline": simple_ref,
        "bayesian_combos": [asdict(c) for c in combos],
    }
    (OUT_DIR / "analysis_summary.json").write_text(json.dumps(payload, indent=2))


def main():
    df = load_results(RAW_PATH)

    generalization = compute_generalization_score(df)
    robustness = compute_robustness_index(df)
    adaptation = compute_adaptation_speed(df)
    transfer = compute_cross_task_transfer(df)

    simple_ref = summarize_simple_baseline(df)
    combos = summarize_bayesian_grid(df, simple_ref["mean_total_utility"])

    mark_pareto_front(combos, "mean_total_utility", "adaptation_speed", "is_pareto_utility_adapt")
    mark_pareto_front(combos, "mean_total_utility", "robustness_index", "is_pareto_utility_robust")

    plot_pareto(
        combos,
        "mean_total_utility",
        "adaptation_speed",
        PLOT_DIR / "pareto_utility_vs_adaptation.png",
        label_y="Adaptation speed (long-short)",
        attr_name="is_pareto_utility_adapt",
    )
    plot_pareto(
        combos,
        "mean_total_utility",
        "robustness_index",
        PLOT_DIR / "pareto_utility_vs_robustness.png",
        label_y="Robustness index",
        attr_name="is_pareto_utility_robust",
    )
    plot_heatmap(
        combos,
        "mean_total_utility",
        PLOT_DIR / "utility_heatmap.png",
        title="Mean utility across priors/lambdas",
    )

    save_summary(generalization, robustness, adaptation, transfer, simple_ref, combos)
    print(f"Saved Week 5 analysis summary + plots to {OUT_DIR}")


if __name__ == "__main__":
    main()
