"""SIQ-focused plotting helpers used across week analyses."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Iterable, List, Mapping, Optional

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

plt.style.use("seaborn-v0_8-whitegrid")


SIQ_COMPONENT_KEYS = [
    "social_alignment",
    "theory_of_mind_accuracy",
    "cross_context_generalization",
    "ethical_consistency",
]


def _ensure_dir(path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def collect_weekly_siq_history(upto_week: int = 5) -> Dict[int, Dict[str, Dict[str, float]]]:
    """Load SIQ summaries from available week folders up to ``upto_week``."""

    history: Dict[int, Dict[str, Dict[str, float]]] = {}
    for week in range(3, upto_week + 1):
        summary_paths = [
            Path(f"results/week{week}/analysis_summary.json"),
            Path(f"results/week{week}/siq_summary.json"),
        ]
        siq_payload: Optional[Dict[str, Dict[str, float]]] = None
        for path in summary_paths:
            if not path.exists():
                continue
            try:
                data = json.loads(path.read_text())
            except json.JSONDecodeError:
                continue
            candidate = data.get("siq_by_agent") or data.get("siq_scores")
            if candidate:
                siq_payload = candidate
                break
        if siq_payload:
            history[week] = siq_payload
    return history


def plot_weekly_siq_trend(
    history: Mapping[int, Mapping[str, Mapping[str, float]]], output_path: Path
) -> Optional[Path]:
    """Plot SIQ over weeks for each agent type."""

    if not history:
        return None

    df_rows = []
    for week, agents in history.items():
        for agent, metrics in agents.items():
            siq_val = metrics.get("siq") or metrics.get("siq_score") or metrics.get("siq_value")
            if siq_val is None:
                siq_val = metrics.get("siq", np.nan)
            df_rows.append({"week": week, "agent_type": agent, "siq": float(siq_val)})

    df = pd.DataFrame(df_rows)
    if df.empty:
        return None

    fig, ax = plt.subplots(figsize=(7, 4))
    sns.lineplot(data=df, x="week", y="siq", hue="agent_type", marker="o", ax=ax)
    ax.set_xticks(sorted(df["week"].unique()))
    ax.set_ylim(0, 1)
    ax.set_ylabel("SIQ")
    ax.set_title("SIQ progression over weeks")
    ax.legend(bbox_to_anchor=(1.02, 1), loc="upper left")
    plt.tight_layout()
    out = _ensure_dir(output_path)
    fig.savefig(out, dpi=300)
    plt.close(fig)
    return out


def plot_task_vs_siq_scatter(
    combos: Iterable[Mapping[str, float]], output_path: Path, label_key: str = "lambda_social"
) -> Optional[Path]:
    """Scatter plot showing trade-off between task utility and SIQ."""

    records = [
        {
            "mean_total_utility": combo.get("mean_total_utility"),
            "siq_score": combo.get("siq_score"),
            "lambda_social": combo.get("lambda_social"),
            "prior_strength": combo.get("prior_strength"),
        }
        for combo in combos
    ]
    df = pd.DataFrame(records).dropna(subset=["mean_total_utility", "siq_score"])
    if df.empty:
        return None

    fig, ax = plt.subplots(figsize=(6, 4))
    scatter = ax.scatter(
        df["mean_total_utility"],
        df["siq_score"],
        c=df[label_key] if label_key in df.columns else None,
        cmap="viridis",
        alpha=0.8,
    )
    ax.set_xlabel("Mean total utility")
    ax.set_ylabel("SIQ")
    ax.set_title("Task utility vs SIQ")
    if label_key in df.columns:
        cbar = fig.colorbar(scatter, ax=ax)
        cbar.set_label(label_key)
    plt.tight_layout()
    out = _ensure_dir(output_path)
    fig.savefig(out, dpi=300)
    plt.close(fig)
    return out


def plot_siq_components_bar(
    siq_by_agent: Mapping[str, Mapping[str, float]], output_path: Path
) -> Optional[Path]:
    """Bar chart highlighting SIQ component contributions per agent."""

    if not siq_by_agent:
        return None
    rows = []
    for agent, metrics in siq_by_agent.items():
        for component in SIQ_COMPONENT_KEYS:
            value = metrics.get(component)
            if value is None:
                continue
            rows.append({"agent_type": agent, "component": component, "value": float(value)})
    df = pd.DataFrame(rows)
    if df.empty:
        return None

    fig, ax = plt.subplots(figsize=(7, 4))
    sns.barplot(data=df, x="component", y="value", hue="agent_type", ax=ax)
    ax.set_ylim(0, 1)
    ax.set_ylabel("Component score")
    ax.set_xlabel("SIQ component")
    ax.set_title("SIQ component breakdown by agent")
    ax.legend(bbox_to_anchor=(1.02, 1), loc="upper left")
    plt.tight_layout()
    out = _ensure_dir(output_path)
    fig.savefig(out, dpi=300)
    plt.close(fig)
    return out


def plot_siq_heatmap(
    combos: Iterable[Mapping[str, float]], output_path: Path
) -> Optional[Path]:
    """Heatmap mapping (lambda, prior_strength) to SIQ."""

    records = [
        {
            "lambda_social": combo.get("lambda_social"),
            "prior_strength": combo.get("prior_strength"),
            "siq_score": combo.get("siq_score"),
        }
        for combo in combos
    ]
    df = pd.DataFrame(records).dropna(subset=["lambda_social", "prior_strength", "siq_score"])
    if df.empty:
        return None

    pivot = df.pivot_table(
        index="prior_strength",
        columns="lambda_social",
        values="siq_score",
        aggfunc="mean",
    )
    fig, ax = plt.subplots(figsize=(6, 4))
    sns.heatmap(pivot, annot=True, fmt=".3f", cmap="magma", cbar_kws={"label": "SIQ"}, ax=ax)
    ax.set_xlabel("lambda_social")
    ax.set_ylabel("prior_strength")
    ax.set_title("SIQ heatmap: priors vs λ")
    plt.tight_layout()
    out = _ensure_dir(output_path)
    fig.savefig(out, dpi=300)
    plt.close(fig)
    return out