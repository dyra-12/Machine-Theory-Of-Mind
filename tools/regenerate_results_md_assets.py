#!/usr/bin/env python3
"""Regenerate figures + tables referenced by docs/Results.md into docs/figures/.

Important constraints (matches repo reviewer workflow)
- Does NOT run any experiments.
- Does NOT write anything under results/.
- Reads existing artifacts (JSON/CSV/JSONL/traces) and *recomputes* the plots
  and markdown tables into docs/figures/.

Modes
- Default: regenerate all supported assets into docs/figures/.
- --smoke-test: validate inputs/imports only; do not write outputs.

Notes
- A small subset of tables in docs/Results.md are not backed by a structured
  artifact in results/. For those, this script falls back to extracting the
  table block from docs/Results.md so the docs build is still one-command.
"""

from __future__ import annotations

import argparse
import json
import math
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

# NOTE: This script supports a --smoke-test mode that must not require
# heavy plotting dependencies. Imports for matplotlib (and friends) are
# therefore done lazily inside the non-smoke execution path.

import numpy as np
import pandas as pd

from src.metrics.siq import SIQ, SIQConfig, WeightConfig


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RESULTS_MD = ROOT / "docs" / "Results.md"
DEFAULT_OUT_DIR = ROOT / "docs" / "figures"


# -----------------------------
# Generic helpers
# -----------------------------


def read_json(path: Path) -> Dict:
    return json.loads(path.read_text(encoding="utf-8"))


def read_jsonl_df(path: Path) -> pd.DataFrame:
    rows: List[Dict] = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
    return pd.DataFrame(rows)


def save_fig(path: Path, dpi: int = 200) -> None:
    import matplotlib.pyplot as plt

    path.parent.mkdir(parents=True, exist_ok=True)
    plt.tight_layout()
    plt.savefig(path, dpi=dpi)
    plt.close()


def md_table(headers: Sequence[str], rows: Sequence[Sequence[object]]) -> str:
    def esc(v: object) -> str:
        s = "" if v is None else str(v)
        return s.replace("\n", " ")

    head = "| " + " | ".join(headers) + " |"
    sep = "|" + "|".join(["---"] * len(headers)) + "|"
    body = ["| " + " | ".join(esc(v) for v in row) + " |" for row in rows]
    return "\n".join([head, sep, *body]) + "\n"


# -----------------------------
# Fallback extraction (only when no structured source exists)
# -----------------------------

TABLE_HEADING_RE = re.compile(r"^#{3,4}\s+Table\s+(\d+)\.?\s*(.*)$")


def extract_table_from_results_md(results_md: Path, table_num: int) -> Optional[str]:
    lines = results_md.read_text(encoding="utf-8").splitlines()
    i = 0
    while i < len(lines):
        m = TABLE_HEADING_RE.match(lines[i])
        if not m:
            i += 1
            continue
        if int(m.group(1)) != table_num:
            i += 1
            continue

        title = m.group(2).strip()
        j = i + 1
        while j < len(lines) and not lines[j].lstrip().startswith("|"):
            j += 1
        if j >= len(lines) or not lines[j].lstrip().startswith("|"):
            return None

        table_lines: List[str] = []
        while j < len(lines):
            line = lines[j]
            if not line.strip():
                break
            if not line.lstrip().startswith("|"):
                break
            table_lines.append(line)
            j += 1

        if not table_lines:
            return None

        out = []
        out.append(f"#### Table {table_num}. {title}".rstrip())
        out.append("")
        out.extend(table_lines)
        out.append("")
        return "\n".join(out)

    return None


# -----------------------------
# Figure generators
# -----------------------------


def fig_week5_from_analysis(out_dir: Path) -> None:
    import matplotlib.pyplot as plt

    path = ROOT / "results" / "week5" / "analysis_summary.json"
    data = read_json(path)
    combos = pd.DataFrame(data.get("bayesian_combos", []))

    if combos.empty:
        raise RuntimeError("Week5 analysis_summary.json has no bayesian_combos")

    # Utility heatmap
    pivot_u = combos.pivot_table(index="prior_strength", columns="lambda_social", values="mean_total_utility", aggfunc="mean")
    plt.figure(figsize=(6, 4))
    im = plt.imshow(pivot_u.values, aspect="auto", cmap="viridis")
    plt.colorbar(im, label="Mean total utility")
    plt.xticks(range(len(pivot_u.columns)), [f"{v:.3g}" for v in pivot_u.columns])
    plt.yticks(range(len(pivot_u.index)), [f"{v:.3g}" for v in pivot_u.index])
    plt.xlabel("λ")
    plt.ylabel("Prior strength")
    plt.title("Week 5: Utility heatmap")
    save_fig(out_dir / "week5_plots_utility_heatmap.png")

    # SIQ heatmap
    pivot_s = combos.pivot_table(index="prior_strength", columns="lambda_social", values="siq_score", aggfunc="mean")
    plt.figure(figsize=(6, 4))
    im = plt.imshow(pivot_s.values, aspect="auto", cmap="magma")
    plt.colorbar(im, label="SIQ score")
    plt.xticks(range(len(pivot_s.columns)), [f"{v:.3g}" for v in pivot_s.columns])
    plt.yticks(range(len(pivot_s.index)), [f"{v:.3g}" for v in pivot_s.index])
    plt.xlabel("λ")
    plt.ylabel("Prior strength")
    plt.title("Week 5: SIQ heatmap")
    save_fig(out_dir / "week5_plots_siq_heatmap.png")

    # Pareto plots (utility vs adaptation / robustness)
    def plot_pareto(y_col: str, y_label: str, fname: str) -> None:
        plt.figure(figsize=(6, 4))
        x = combos["mean_total_utility"].astype(float)
        y = combos[y_col].astype(float)
        plt.scatter(x, y, alpha=0.7)
        plt.xlabel("Mean total utility")
        plt.ylabel(y_label)
        plt.title(f"Week 5: Utility vs {y_label}")
        save_fig(out_dir / fname)

    plot_pareto("adaptation_speed", "Adaptation speed", "week5_plots_pareto_utility_vs_adaptation.png")
    plot_pareto("robustness_index", "Robustness index", "week5_plots_pareto_utility_vs_robustness.png")

    # SIQ component bar chart (agent-level)
    siq_by_agent = data.get("siq_by_agent", {})
    if siq_by_agent:
        comp_keys = ["social_alignment", "theory_of_mind_accuracy", "cross_context_generalization", "ethical_consistency"]
        agents = list(siq_by_agent.keys())
        mat = np.array([[siq_by_agent[a].get(k, np.nan) for k in comp_keys] for a in agents], dtype=float)

        x = np.arange(len(comp_keys))
        width = 0.8 / max(1, len(agents))
        plt.figure(figsize=(8, 4))
        for idx, agent in enumerate(agents):
            plt.bar(x + idx * width, mat[idx], width=width, label=agent)
        plt.xticks(x + width * (len(agents) - 1) / 2, [k.replace("_", " ") for k in comp_keys], rotation=20, ha="right")
        plt.ylim(0, 1)
        plt.ylabel("Score")
        plt.title("Week 5: SIQ components by agent")
        plt.legend(fontsize=8)
        save_fig(out_dir / "week5_plots_week5_siq_components.png")


def fig_week4_from_raw(out_dir: Path) -> None:
    import matplotlib.pyplot as plt

    raw_path = ROOT / "results" / "week4" / "raw" / "negotiation_generalization" / "results.jsonl"
    df = read_jsonl_df(raw_path)

    # Generalization env curves
    order = ["small_resources", "large_resources", "short_horizon", "long_horizon"]
    plt.figure(figsize=(7, 4))
    for agent, sub in df.groupby("agent_type"):
        grouped = sub.groupby("env_name")["total_utility"].mean().reindex(order)
        plt.plot(grouped.index, grouped.values, marker="o", label=str(agent))
    plt.ylabel("Mean total utility")
    plt.xticks(rotation=25)
    plt.title("Week 4: Generalization across env variants")
    plt.legend(fontsize=7)
    save_fig(out_dir / "week4_plots_generalization_env_curves.png")

    # SIQ components by agent (from analysis_summary.json if present)
    summary_path = ROOT / "results" / "week4" / "analysis_summary.json"
    if summary_path.exists():
        summary = read_json(summary_path)
        siq_by_agent = summary.get("siq_by_agent", {})
    else:
        # Fallback: compute SIQ from raw df
        siq = SIQ(SIQConfig.from_yaml(ROOT / "experiments" / "config" / "week6_siq.yaml"))
        siq_by_agent = siq.compute_by_group(df, group_key="agent_type")

    if siq_by_agent:
        comp_keys = ["social_alignment", "theory_of_mind_accuracy", "cross_context_generalization", "ethical_consistency"]
        agents = list(siq_by_agent.keys())
        mat = np.array([[siq_by_agent[a].get(k, np.nan) for k in comp_keys] for a in agents], dtype=float)

        x = np.arange(len(comp_keys))
        width = 0.8 / max(1, len(agents))
        plt.figure(figsize=(8, 4))
        for idx, agent in enumerate(agents):
            plt.bar(x + idx * width, mat[idx], width=width, label=agent)
        plt.xticks(x + width * (len(agents) - 1) / 2, [k.replace("_", " ") for k in comp_keys], rotation=20, ha="right")
        plt.ylim(0, 1)
        plt.ylabel("Score")
        plt.title("Week 4: SIQ components by agent")
        plt.legend(fontsize=7)
        save_fig(out_dir / "week4_plots_week4_siq_components.png")


def fig_week3_from_raw(out_dir: Path) -> None:
    import matplotlib.pyplot as plt

    raw_path = ROOT / "results" / "week3" / "raw" / "latest_results.jsonl"
    df = read_jsonl_df(raw_path)

    # Lambda sensitivity: mean social_score vs lambda
    plt.figure(figsize=(7, 4))
    for agent, sub in df.groupby("agent_type"):
        grouped = sub.groupby("lambda_social")["social_score"].mean().sort_index()
        plt.plot(grouped.index, grouped.values, marker="o", label=str(agent))
    plt.xlabel("λ")
    plt.ylabel("Mean social_score")
    plt.title("Week 3: Social score vs λ")
    plt.legend(fontsize=7)
    save_fig(out_dir / "week3_plots_lambda_sensitivity.png")

    # Pareto frontiers: mean task_reward vs mean social_score per (agent, lambda)
    plt.figure(figsize=(7, 5))
    for agent, sub in df.groupby("agent_type"):
        grouped = sub.groupby("lambda_social").agg({"task_reward": "mean", "social_score": "mean"}).reset_index()
        plt.scatter(grouped["task_reward"], grouped["social_score"], label=str(agent), alpha=0.8)
    plt.xlabel("Mean task_reward")
    plt.ylabel("Mean social_score")
    plt.title("Week 3: Pareto scatter (task vs social)")
    plt.legend(fontsize=7)
    save_fig(out_dir / "week3_plots_pareto_frontiers.png")


def fig_week7_from_traces(out_dir: Path) -> None:
    import matplotlib.pyplot as plt

    trace_dir = ROOT / "results" / "week7" / "traces"
    traces = sorted(trace_dir.glob("trace_*.json"))
    if not traces:
        raise FileNotFoundError(f"No trace_*.json files found under {trace_dir}")

    # Posterior trace example
    data = json.loads(traces[0].read_text(encoding="utf-8"))
    steps = data.get("steps", [])
    turns = [int(s.get("turn", 0)) for s in steps]
    warmth = [float(s.get("beliefs", {}).get("warmth", np.nan)) for s in steps]
    competence = [float(s.get("beliefs", {}).get("competence", np.nan)) for s in steps]

    plt.figure(figsize=(6, 4))
    plt.plot(turns, warmth, marker="o", label="Warmth")
    plt.plot(turns, competence, marker="s", label="Competence")
    plt.ylim(0, 1)
    plt.xlabel("Turn")
    plt.ylabel("Posterior")
    plt.title("Week 7: Example posterior trace")
    plt.legend()
    save_fig(out_dir / "week7_posterior_trace_example.png")

    # Social score vs turn (extended): aggregate across traces by opponent_policy
    rows: Dict[Tuple[str, int], List[float]] = {}
    for tpath in traces:
        tj = json.loads(tpath.read_text(encoding="utf-8"))
        meta = tj.get("metadata", {})
        opp = str(meta.get("opponent_policy", "unknown"))
        for step in tj.get("steps", []):
            turn = int(step.get("turn", 0))
            sc = step.get("social_score")
            if sc is None:
                continue
            rows.setdefault((opp, turn), []).append(float(sc))

    plt.figure(figsize=(8, 5))
    for opp in sorted({k[0] for k in rows.keys()}):
        pts = sorted([(turn, rows[(opp, turn)]) for (_, turn) in rows.keys() if _ == opp], key=lambda x: x[0])
        xs = [p[0] for p in pts]
        means = [float(np.mean(p[1])) for p in pts]
        stderrs = [float(np.std(p[1]) / math.sqrt(len(p[1]))) if len(p[1]) > 1 else 0.0 for p in pts]
        plt.errorbar(xs, means, yerr=stderrs, marker="o", capsize=3, label=opp)

    plt.xlabel("Turn")
    plt.ylabel("Mean social_score")
    plt.title("Week 7: Social score vs turn (regenerated)")
    plt.legend(fontsize=8)
    plt.grid(True, alpha=0.3)
    save_fig(out_dir / "week7_plots_social_score_vs_turn_extended.png")


def fig_week7_from_robustness(out_dir: Path) -> None:
    import matplotlib.pyplot as plt

    path = ROOT / "results" / "week7" / "robustness_suite" / "robustness_results.jsonl"
    df = read_jsonl_df(path)

    # Flatten channel.profile for grouping
    df["channel_profile"] = df["channel"].apply(lambda c: (c or {}).get("profile", "unknown"))

    # Bar chart: mean total_utility per channel profile, split by agent
    grouped = df.groupby(["channel_profile", "agent_type"])["total_utility"].mean().unstack(fill_value=np.nan)

    plt.figure(figsize=(7, 4))
    x = np.arange(len(grouped.index))
    agents = list(grouped.columns)
    width = 0.8 / max(1, len(agents))
    for idx, agent in enumerate(agents):
        plt.bar(x + idx * width, grouped[agent].values, width=width, label=str(agent))
    plt.xticks(x + width * (len(agents) - 1) / 2, grouped.index, rotation=15, ha="right")
    plt.ylabel("Mean total_utility")
    plt.title("Week 7: Robustness summary (utility)")
    plt.legend(fontsize=8)
    save_fig(out_dir / "week7_robustness_summary_bar.png")


def fig_week10_human_pilot(out_dir: Path) -> None:
    import matplotlib.pyplot as plt

    path = ROOT / "results" / "week10" / "pilot_ratings_combined.csv"
    df = pd.read_csv(path)

    # Bar plot of mean ratings by agent_type
    metrics = ["warmth", "competence", "trust"]
    agent_types = list(df["agent_type"].unique())

    means = df.groupby("agent_type")[metrics].mean()
    stds = df.groupby("agent_type")[metrics].std(ddof=1)
    ns = df.groupby("agent_type")[metrics].count()

    x = np.arange(len(metrics))
    width = 0.8 / max(1, len(agent_types))
    plt.figure(figsize=(8, 4))
    for idx, agent in enumerate(agent_types):
        y = means.loc[agent].values.astype(float)
        err = (stds.loc[agent].values / np.sqrt(ns.loc[agent].values)).astype(float)
        plt.bar(x + idx * width, y, width=width, label=str(agent), yerr=err, capsize=3)

    plt.xticks(x + width * (len(agent_types) - 1) / 2, metrics)
    plt.ylim(0, 7)
    plt.ylabel("Mean rating (± stderr)")
    plt.title("Week 10: Human pilot ratings")
    plt.legend()
    save_fig(out_dir / "week10_agent_comparison.png")


# -----------------------------
# Table generators
# -----------------------------


def table_01_week5_stats() -> str:
    path = ROOT / "results" / "week5" / "stats_summary.json"
    data = read_json(path)
    rows = [
        ("Baseline", data.get("baseline", {}).get("name")),
        ("Mean difference", f"{data.get('difference_mean', float('nan')):.4f}"),
        ("95% CI", str(data.get("95ci"))),
        ("Cohen's d", f"{data.get('cohens_d', float('nan')):.3f}"),
    ]
    return "#### Table 1. Comparison of Best Bayesian Configuration vs. Simple MToM Baseline\n\n" + md_table(["Metric", "Value"], rows)


def table_02_week5_pareto() -> str:
    path = ROOT / "results" / "week5" / "analysis_summary.json"
    data = read_json(path)
    combos = pd.DataFrame(data.get("bayesian_combos", []))
    if combos.empty:
        raise RuntimeError("Week5 analysis_summary.json missing bayesian_combos")

    pareto = combos[(combos.get("is_pareto_utility_adapt", False)) | (combos.get("is_pareto_utility_robust", False))].copy()
    if pareto.empty:
        pareto = combos.copy()

    pareto = pareto.sort_values(["mean_total_utility"], ascending=False).head(10)
    rows = []
    for _, r in pareto.iterrows():
        rows.append((f"{r['prior_strength']:.3g}", f"{r['lambda_social']:.3g}", f"{r['mean_total_utility']:.4f}", f"{r['siq_score']:.4f}"))

    title = "#### Table 2. Main Sweep Configurations (Pareto-Optimal)\n\n"
    return title + md_table(["Prior Strength", "λ", "Total Utility", "SIQ Score"], rows)


def table_03_week4_siq_components() -> str:
    path = ROOT / "results" / "week4" / "analysis_summary.json"
    data = read_json(path)
    siq_by_agent = data.get("siq_by_agent", {})

    headers = [
        "Agent Type",
        "Social Alignment",
        "ToM Accuracy",
        "Cross-Context Gen.",
        "Ethical Consistency",
        "Mean SIQ",
    ]
    rows = []
    for agent, vals in siq_by_agent.items():
        rows.append(
            (
                agent,
                f"{vals.get('social_alignment', float('nan')):.4f}",
                f"{vals.get('theory_of_mind_accuracy', float('nan')):.4f}",
                f"{vals.get('cross_context_generalization', float('nan')):.4f}",
                f"{vals.get('ethical_consistency', float('nan')):.4f}",
                f"{vals.get('siq', float('nan')):.4f}",
            )
        )

    title = "#### Table 3. Component-Level SIQ Metrics by Agent (Week 4 Diagnostic)\n\n"
    return title + md_table(headers, rows)


def table_04_week5_siq_components() -> str:
    path = ROOT / "results" / "week5" / "analysis_summary.json"
    data = read_json(path)

    combos = pd.DataFrame(data.get("bayesian_combos", []))
    tuned = None
    if not combos.empty:
        tuned = combos.sort_values(["siq_score", "mean_total_utility"], ascending=False).iloc[0].to_dict()

    simple = data.get("siq_by_agent", {}).get("simple_mtom", {})

    rows = []
    if tuned is not None:
        comps = tuned.get("siq_components", {}) or {}
        rows.append(
            (
                "bayesian_mtom (tuned)",
                f"{comps.get('social_alignment', float('nan')):.4f}",
                f"{comps.get('theory_of_mind_accuracy', float('nan')):.4f}",
                f"{comps.get('cross_context_generalization', float('nan')):.4f}",
                f"{comps.get('ethical_consistency', float('nan')):.4f}",
                f"{tuned.get('siq_score', float('nan')):.4f}",
            )
        )

    rows.append(
        (
            "simple_mtom",
            f"{simple.get('social_alignment', float('nan')):.4f}",
            f"{simple.get('theory_of_mind_accuracy', float('nan')):.4f}",
            f"{simple.get('cross_context_generalization', float('nan')):.4f}",
            f"{simple.get('ethical_consistency', float('nan')):.4f}",
            f"{simple.get('siq', float('nan')):.4f}",
        )
    )

    title = "#### Table 4. Component-Level SIQ Metrics (Week 5 Optimized)\n\n"
    return title + md_table(
        ["Agent Type", "Social Alignment", "ToM Accuracy", "Cross-Context Gen.", "Ethical Consistency", "Mean SIQ"],
        rows,
    )


def table_05_week5_vs_week4_deltas() -> str:
    w4 = read_json(ROOT / "results" / "week4" / "analysis_summary.json")
    w5 = read_json(ROOT / "results" / "week5" / "analysis_summary.json")

    def get(vals: Dict, key: str) -> float:
        v = vals.get(key)
        try:
            return float(v)
        except Exception:
            return float("nan")

    # "tuned" = best week5 bayesian combo by siq_score
    combos = pd.DataFrame(w5.get("bayesian_combos", []))
    tuned = combos.sort_values(["siq_score", "mean_total_utility"], ascending=False).iloc[0].to_dict() if not combos.empty else None
    tuned_comps = (tuned or {}).get("siq_components", {}) or {}

    w4_bayes = w4.get("siq_by_agent", {}).get("bayesian_mtom", {})
    w4_simple = w4.get("siq_by_agent", {}).get("simple_mtom", {})
    w5_simple = w5.get("siq_by_agent", {}).get("simple_mtom", {})

    metrics = [
        ("Social Alignment", get(tuned_comps, "social_alignment") - get(w4_bayes, "social_alignment"), get(w5_simple, "social_alignment") - get(w4_simple, "social_alignment")),
        ("ToM Accuracy", get(tuned_comps, "theory_of_mind_accuracy") - get(w4_bayes, "theory_of_mind_accuracy"), get(w5_simple, "theory_of_mind_accuracy") - get(w4_simple, "theory_of_mind_accuracy")),
        ("Cross-Context Gen.", get(tuned_comps, "cross_context_generalization") - get(w4_bayes, "cross_context_generalization"), get(w5_simple, "cross_context_generalization") - get(w4_simple, "cross_context_generalization")),
        ("Ethical Consistency", get(tuned_comps, "ethical_consistency") - get(w4_bayes, "ethical_consistency"), get(w5_simple, "ethical_consistency") - get(w4_simple, "ethical_consistency")),
        ("Mean SIQ", get(tuned, "siq_score") - get(w4_bayes, "siq"), get(w5_simple, "siq") - get(w4_simple, "siq")),
    ]

    rows = [(name, f"{d1:+.4f}", f"{d2:+.4f}") for name, d1, d2 in metrics]
    title = "#### Table 5. Week 5 vs. Week 4 Performance Deltas\n\n"
    return title + md_table(["Metric", "Δ bayesian_mtom (tuned)", "Δ simple_mtom"], rows)


def table_06_week7_adversarial_deltas() -> str:
    # Build a small SIQ proxy focused on social_alignment only.
    cfg = SIQConfig(weights=WeightConfig(social_alignment=1.0, theory_of_mind_accuracy=0.0, cross_context_generalization=0.0, ethical_consistency=0.0))
    siq = SIQ(cfg)

    df = read_jsonl_df(ROOT / "results" / "week7" / "robustness_suite" / "robustness_results.jsonl")
    df["channel_profile"] = df["channel"].apply(lambda c: (c or {}).get("profile", "unknown"))

    # Reference = clean_reference
    ref_prof = "clean_reference"
    ref = df[df["channel_profile"] == ref_prof]

    def mean_siq(sub: pd.DataFrame) -> float:
        try:
            return float(siq.compute(sub).get("siq", float("nan")))
        except Exception:
            return float("nan")

    ref_u = float(ref["total_utility"].mean())
    ref_s = mean_siq(ref)

    rows = []
    for prof in sorted(df["channel_profile"].unique()):
        if prof == ref_prof:
            continue
        sub = df[df["channel_profile"] == prof]
        u = float(sub["total_utility"].mean())
        s = mean_siq(sub)
        du = 100.0 * (u - ref_u) / ref_u if ref_u else float("nan")
        ds = 100.0 * (s - ref_s) / ref_s if ref_s else float("nan")
        rows.append((prof, f"{du:+.2f}", f"{ds:+.2f}", ""))

    title = "#### Table 6. Adversarial Robustness (Stress Test)\n\n"
    return title + md_table(["Condition", "Δ Utility (%)", "Δ SIQ (%)", "Notes"], rows)


def table_07_week4_norm_shift() -> str:
    siq = SIQ(SIQConfig.from_yaml(ROOT / "experiments" / "config" / "week6_siq.yaml"))
    df = read_jsonl_df(ROOT / "results" / "week4" / "raw" / "negotiation_generalization" / "results.jsonl")

    ref_obs = "simple"
    ref = df[df["observer_type"] == ref_obs]
    ref_u = float(ref["total_utility"].mean())
    ref_s = float(siq.compute(ref).get("siq", float("nan")))

    rows = []
    for obs in ["lenient", "competence_biased", "warmth_biased"]:
        sub = df[df["observer_type"] == obs]
        u = float(sub["total_utility"].mean())
        s = float(siq.compute(sub).get("siq", float("nan")))
        du = 100.0 * (u - ref_u) / ref_u if ref_u else float("nan")
        ds = 100.0 * (s - ref_s) / ref_s if ref_s else float("nan")
        rows.append((obs, f"{du:+.2f}", f"{ds:+.2f}", ""))

    title = "#### Table 7. Norm-Shift Sensitivity (Alignment Test)\n\n"
    return title + md_table(["Condition", "Δ Utility (%)", "Δ SIQ (%)", "Notes"], rows)


def table_08_small_lambda_validation() -> str:
    data = read_json(ROOT / "results" / "week7" / "first_order_delta_obs_validation.json")
    # Maintain the names used in docs/Results.md
    rows = [
        ("τ (temperature)", data.get("tau")),
        ("Var₍π₀₎(Δ_obs)", data.get("var_delta_obs")),
        ("Predicted slope (Var / τ)", data.get("predicted_slope")),
        ("Observed slope (finite difference)", data.get("observed_slope")),
        ("Relative error (%)", data.get("relative_error_percent")),
    ]
    title = "#### Table 8. Small-λ Validation Results\n\n"
    return title + md_table(["Quantity", "Value"], rows)


def table_10_week5_generalization() -> str:
    data = read_json(ROOT / "results" / "week5" / "analysis_summary.json")
    rows = [
        ("Simple MToM", f"{data['generalization_score'].get('simple_mtom', float('nan')):.4f}", f"{data['cross_task_transfer'].get('simple_mtom', float('nan')):.4f}", f"{data['adaptation_speed'].get('simple_mtom', float('nan')):.4f}", "1.0"),
        ("Bayesian MToM", f"{data['generalization_score'].get('bayesian_mtom', float('nan')):.4f}", f"{data['cross_task_transfer'].get('bayesian_mtom', float('nan')):.4f}", f"{data['adaptation_speed'].get('bayesian_mtom', float('nan')):.4f}", "1.0"),
    ]
    title = "#### Table 10. Aggregate Generalization Metrics Across Held-Out Contexts\n\n"
    return title + md_table(["Agent", "Generalization Score", "Cross-Task Transfer", "Adaptation Speed", "SIQ: Cross-Context Gen."], rows)


def table_11_week10_unpaired() -> str:
    path = ROOT / "results" / "week10" / "human_pilot_unpaired_stats.csv"
    df = pd.read_csv(path)
    rows = []
    for _, r in df.iterrows():
        rows.append((r["metric"], int(r["n1"]), int(r["n2"]), f"{float(r['cohens_d']):.2f}", f"{float(r['p_value']):.6g}"))
    title = "#### Table 11. Unpaired Human Evaluation Results\n\n"
    return title + md_table(["Metric", "n₁", "n₂", "Cohen's d", "p-value"], rows)


# -----------------------------
# Main
# -----------------------------


def validate_inputs(results_md: Path) -> None:
    required_files = [
        results_md,
        ROOT / "results" / "week5" / "analysis_summary.json",
        ROOT / "results" / "week5" / "stats_summary.json",
        ROOT / "results" / "week4" / "raw" / "negotiation_generalization" / "results.jsonl",
        ROOT / "results" / "week3" / "raw" / "latest_results.jsonl",
        ROOT / "results" / "week7" / "robustness_suite" / "robustness_results.jsonl",
        ROOT / "results" / "week7" / "traces",
        ROOT / "results" / "week7" / "first_order_delta_obs_validation.json",
        ROOT / "results" / "week10" / "pilot_ratings_combined.csv",
        ROOT / "results" / "week10" / "human_pilot_unpaired_stats.csv",
    ]
    missing = [p for p in required_files if not p.exists()]
    if missing:
        raise FileNotFoundError("Missing required inputs:\n" + "\n".join([str(p) for p in missing]))


def main() -> int:
    parser = argparse.ArgumentParser(description="Regenerate docs/Results.md assets into docs/figures")
    parser.add_argument("--results-md", type=Path, default=DEFAULT_RESULTS_MD)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    parser.add_argument("--smoke-test", action="store_true", help="Validate only; do not write outputs")
    args = parser.parse_args()

    results_md = args.results_md.resolve()
    out_dir = args.out_dir.resolve()

    validate_inputs(results_md)

    if args.smoke_test:
        print("Smoke test OK: required inputs present; no outputs written.")
        return 0

    # Figures
    fig_week5_from_analysis(out_dir)
    fig_week4_from_raw(out_dir)
    fig_week3_from_raw(out_dir)
    fig_week7_from_traces(out_dir)
    fig_week7_from_robustness(out_dir)
    fig_week10_human_pilot(out_dir)

    # Tables (programmatic where possible)
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "table_01_week5_stats.md").write_text(table_01_week5_stats(), encoding="utf-8")
    (out_dir / "table_02_week5_pareto.md").write_text(table_02_week5_pareto(), encoding="utf-8")
    (out_dir / "table_03_week4_siq_components.md").write_text(table_03_week4_siq_components(), encoding="utf-8")
    (out_dir / "table_04_week5_siq_components.md").write_text(table_04_week5_siq_components(), encoding="utf-8")
    (out_dir / "table_05_week5_vs_week4_deltas.md").write_text(table_05_week5_vs_week4_deltas(), encoding="utf-8")
    (out_dir / "table_06_week7_adversarial_deltas.md").write_text(table_06_week7_adversarial_deltas(), encoding="utf-8")
    (out_dir / "table_07_week4_norm_shift.md").write_text(table_07_week4_norm_shift(), encoding="utf-8")
    (out_dir / "table_08_week7_small_lambda_validation.md").write_text(table_08_small_lambda_validation(), encoding="utf-8")
    (out_dir / "table_10_week5_generalization.md").write_text(table_10_week5_generalization(), encoding="utf-8")
    (out_dir / "table_11_week10_unpaired.md").write_text(table_11_week10_unpaired(), encoding="utf-8")

    # Fallback-only tables: 9 and 12 (and any others missing)
    for num in (9, 12):
        extracted = extract_table_from_results_md(results_md, num)
        if extracted:
            (out_dir / f"table_{num:02d}_from_results_md.md").write_text(extracted, encoding="utf-8")

    print(f"Regenerated figures + tables into {out_dir}")
    print("Note: No files under results/ were modified.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
