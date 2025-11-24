"""Week 4 Analysis Script

Consumes the JSONL produced by `run_week4.py` and computes
high-level generalization / robustness metrics plus a few
visualizations.

Metrics (per agent type):
- Generalization Score: mean total utility across all conditions,
  normalized by performance in the easiest reference condition.
- Adaptation Speed (proxy): change in total utility across
  negotiation horizons (short vs long) and across rounds.
- Robustness Index: variance-normalized utility across observers,
  env variants, and opponents.
- Cross-task Transfer: (placeholder) currently identical to
  generalization over env variants, ready to plug in other games.

Outputs:
- `results/week4/analysis_summary.json`
- basic plots in `results/week4/plots`.
"""

import json
from pathlib import Path
from typing import Dict, List

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats


RAW_PATH = Path("results/week4/raw/negotiation_generalization/results.jsonl")
OUT_DIR = Path("results/week4")
PLOT_DIR = OUT_DIR / "plots"


def load_results(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"No Week 4 results found at {path}")
    rows: List[Dict] = []
    with path.open("r") as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line))
    return pd.DataFrame(rows)


def compute_generalization_score(df: pd.DataFrame) -> Dict[str, float]:
    """Generalization Score per agent: mean utility relative to an easy baseline.

    Baseline condition: simple observer, small_resources env, fair opponent.
    Score = mean_utility_all_conditions / mean_utility_baseline.
    """
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
        if mean_base == 0:
            scores[agent] = float("nan")
        else:
            scores[agent] = float(mean_all / mean_base)
    return scores


def compute_robustness_index(df: pd.DataFrame) -> Dict[str, float]:
    """Robustness Index per agent: 1 / (1 + CV) of total utility across conditions.

    Lower coefficient of variation (std / mean) → higher robustness.
    """
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
    """Proxy Adaptation Speed per agent.

    We compare mean utility in `short_horizon` vs `long_horizon` envs.
    Speed = (long_horizon_mean - short_horizon_mean).
    """
    speed: Dict[str, float] = {}
    for agent in df["agent_type"].unique():
        sub = df[df["agent_type"] == agent]
        short = sub[sub["env_name"] == "short_horizon"]["total_utility"].mean()
        long = sub[sub["env_name"] == "long_horizon"]["total_utility"].mean()
        if np.isnan(short) or np.isnan(long):
            speed[agent] = float("nan")
        else:
            speed[agent] = float(long - short)
    return speed


def compute_cross_task_transfer(df: pd.DataFrame) -> Dict[str, float]:
    """Placeholder Cross-task Transfer metric.

    For now, treat distinct env_names as proxy tasks and
    compute mean utility in non-baseline envs relative to baseline env.
    """
    transfer: Dict[str, float] = {}
    for agent in df["agent_type"].unique():
        sub = df[df["agent_type"] == agent]
        base = sub[sub["env_name"] == "small_resources"]["total_utility"].mean()
        other = sub[sub["env_name"] != "small_resources"]["total_utility"].mean()
        if base == 0 or np.isnan(base) or np.isnan(other):
            transfer[agent] = float("nan")
        else:
            transfer[agent] = float(other / base)
    return transfer


def compute_adaptation_advantage(df: pd.DataFrame) -> Dict[str, float]:
    """Adaptation advantage: gain in utility from easy → hard conditions.

    We treat (simple observer, fair opponent) as an "easy" social
    context and (harsh observer, unpredictable opponent) as a "hard"
    one. For each agent we compute:

        advantage = mean_utility_hard - mean_utility_easy

    Bayesian MToM should show a larger positive advantage than
    non-MToM baselines if it adapts better to tough conditions.
    """
    adv: Dict[str, float] = {}
    easy_mask = (df["observer_type"] == "simple") & (df["opponent_type"] == "fair")
    hard_mask = (df["observer_type"] == "harsh") & (df["opponent_type"] == "unpredictable")

    for agent in df["agent_type"].unique():
        sub = df[df["agent_type"] == agent]
        easy_vals = sub.loc[easy_mask.loc[sub.index], "total_utility"]
        hard_vals = sub.loc[hard_mask.loc[sub.index], "total_utility"]
        if easy_vals.empty or hard_vals.empty:
            adv[agent] = float("nan")
        else:
            adv[agent] = float(hard_vals.mean() - easy_vals.mean())
    return adv


def compute_easy_hard_stats(df: pd.DataFrame) -> Dict[str, Dict[str, float]]:
    """Return per-agent mean utilities in easy vs hard social contexts."""
    easy_mask = (df["observer_type"] == "simple") & (df["opponent_type"] == "fair")
    hard_mask = (df["observer_type"] == "harsh") & (df["opponent_type"] == "unpredictable")

    stats_dict: Dict[str, Dict[str, float]] = {}
    for agent in df["agent_type"].unique():
        sub = df[df["agent_type"] == agent]
        easy_vals = sub.loc[easy_mask.loc[sub.index], "total_utility"]
        hard_vals = sub.loc[hard_mask.loc[sub.index], "total_utility"]

        easy_mean = float(easy_vals.mean()) if not easy_vals.empty else float("nan")
        hard_mean = float(hard_vals.mean()) if not hard_vals.empty else float("nan")
        delta = float(hard_mean - easy_mean) if not np.isnan(easy_mean) and not np.isnan(hard_mean) else float("nan")

        stats_dict[agent] = {
            "easy_mean": easy_mean,
            "hard_mean": hard_mean,
            "delta": delta,
        }

    return stats_dict


def plot_generalization_curves(df: pd.DataFrame):
    PLOT_DIR.mkdir(parents=True, exist_ok=True)

    # Utility vs env variant per agent
    plt.figure(figsize=(6, 4))
    for agent in df["agent_type"].unique():
        sub = df[df["agent_type"] == agent]
        grouped = sub.groupby("env_name")["total_utility"].mean().reindex(
            ["small_resources", "large_resources", "short_horizon", "long_horizon"],
            fill_value=np.nan,
        )
        plt.plot(grouped.index, grouped.values, marker="o", label=agent)
    plt.ylabel("Mean total utility")
    plt.xticks(rotation=30)
    plt.title("Generalization across env variants")
    plt.legend(fontsize=8)
    out = PLOT_DIR / "generalization_env_curves.png"
    plt.tight_layout()
    plt.savefig(out)
    plt.close()

    # Heatmap: observer x opponent for Bayesian MToM
    bayes = df[df["agent_type"].str.contains("bayesian", case=False)]
    if not bayes.empty:
        pivot = bayes.pivot_table(
            index="observer_type",
            columns="opponent_type",
            values="total_utility",
            aggfunc="mean",
        )
        plt.figure(figsize=(5, 4))
        im = plt.imshow(pivot.values, aspect="auto", cmap="viridis")
        plt.colorbar(im, label="Mean total utility")
        plt.xticks(range(len(pivot.columns)), pivot.columns, rotation=30)
        plt.yticks(range(len(pivot.index)), pivot.index)
        plt.title("Bayesian MToM: observer x opponent")
        out2 = PLOT_DIR / "bayesian_observer_opponent_heatmap.png"
        plt.tight_layout()
        plt.savefig(out2)
        plt.close()


def plot_easy_vs_hard(stats_dict: Dict[str, Dict[str, float]]):
    """Create a bar chart comparing easy vs hard mean utilities per agent."""
    PLOT_DIR.mkdir(parents=True, exist_ok=True)
    agents = list(stats_dict.keys())
    easy_means = [stats_dict[a]["easy_mean"] for a in agents]
    hard_means = [stats_dict[a]["hard_mean"] for a in agents]

    x = np.arange(len(agents))
    width = 0.35

    plt.figure(figsize=(7, 4))
    plt.bar(x - width / 2, easy_means, width, label="Easy (simple+fair)")
    plt.bar(x + width / 2, hard_means, width, label="Hard (harsh+unpredictable)")
    plt.xticks(x, agents, rotation=20)
    plt.ylabel("Mean total utility")
    plt.title("Easy vs hard social conditions")
    plt.legend(fontsize=8)
    plt.tight_layout()
    out = PLOT_DIR / "easy_vs_hard_bar.png"
    plt.savefig(out)
    plt.close()


def save_summary_json(
    generalization: Dict[str, float],
    robustness: Dict[str, float],
    adaptation: Dict[str, float],
    transfer: Dict[str, float],
    adaptation_advantage: Dict[str, float],
    easy_hard_stats: Dict[str, Dict[str, float]],
    bayes_vs_baselines: Dict[str, Dict[str, float]],
    bayes_significance: Dict[str, Dict[str, float]],
):
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out = OUT_DIR / "analysis_summary.json"
    payload = {
        "generalization_score": generalization,
        "robustness_index": robustness,
        "adaptation_speed": adaptation,
        "cross_task_transfer": transfer,
        "adaptation_advantage": adaptation_advantage,
        "easy_hard_stats": easy_hard_stats,
        "bayesian_vs_baselines": bayes_vs_baselines,
        "bayesian_significance": bayes_significance,
    }
    out.write_text(json.dumps(payload, indent=2))


def summarize_bayesian_vs_baselines(df: pd.DataFrame) -> Dict[str, Dict[str, float]]:
    """Directly compare Bayesian MToM to each baseline.

    Returns a nested dict with mean total utility differences in:
    - 'all_conditions'
    - 'harsh_observer'
    - 'unpredictable_opponent'
    - 'harsh_unpredictable_combo'
    for each baseline agent.
    """
    summaries: Dict[str, Dict[str, float]] = {}

    bayes = df[df["agent_type"].str.contains("bayesian", case=False)]
    if bayes.empty:
        return summaries

    baselines = [a for a in df["agent_type"].unique() if "bayesian" not in a.lower()]

    # Helper to get mean utility for a frame with same condition mask
    def mean_util(frame: pd.DataFrame, mask: pd.Series) -> float:
        vals = frame.loc[mask, "total_utility"]
        return float(vals.mean()) if not vals.empty else float("nan")

    for base in baselines:
        base_df = df[df["agent_type"] == base]
        if base_df.empty:
            continue

        all_mask = df["agent_type"].notna()  # all rows
        harsh_mask = df["observer_type"] == "harsh"
        unpred_mask = df["opponent_type"] == "unpredictable"
        combo_mask = harsh_mask & unpred_mask

        # Align masks to each subset
        bayes_all = mean_util(bayes, bayes.index.to_series().isin(df.index[all_mask]))
        base_all = mean_util(base_df, base_df.index.to_series().isin(df.index[all_mask]))

        bayes_harsh = mean_util(bayes, bayes["observer_type"] == "harsh")
        base_harsh = mean_util(base_df, base_df["observer_type"] == "harsh")

        bayes_unpred = mean_util(bayes, bayes["opponent_type"] == "unpredictable")
        base_unpred = mean_util(base_df, base_df["opponent_type"] == "unpredictable")

        bayes_combo = mean_util(
            bayes,
            (bayes["observer_type"] == "harsh") & (bayes["opponent_type"] == "unpredictable"),
        )
        base_combo = mean_util(
            base_df,
            (base_df["observer_type"] == "harsh") & (base_df["opponent_type"] == "unpredictable"),
        )

        summaries[base] = {
            "delta_all": bayes_all - base_all,
            "delta_harsh": bayes_harsh - base_harsh,
            "delta_unpredictable": bayes_unpred - base_unpred,
            "delta_harsh_unpredictable": bayes_combo - base_combo,
        }

    return summaries


def bayesian_significance_tests(df: pd.DataFrame) -> Dict[str, Dict[str, float]]:
    """Welch t-tests comparing Bayesian MToM to each baseline in easy & hard contexts."""
    results: Dict[str, Dict[str, float]] = {}
    bayes = df[df["agent_type"].str.contains("bayesian", case=False)]
    if bayes.empty:
        return results

    easy_mask = (df["observer_type"] == "simple") & (df["opponent_type"] == "fair")
    hard_mask = (df["observer_type"] == "harsh") & (df["opponent_type"] == "unpredictable")

    bayes_easy = bayes.loc[easy_mask.loc[bayes.index], "total_utility"]
    bayes_hard = bayes.loc[hard_mask.loc[bayes.index], "total_utility"]

    baselines = [a for a in df["agent_type"].unique() if "bayesian" not in a.lower()]

    for base in baselines:
        base_df = df[df["agent_type"] == base]
        base_easy = base_df.loc[easy_mask.loc[base_df.index], "total_utility"]
        base_hard = base_df.loc[hard_mask.loc[base_df.index], "total_utility"]

        easy_p = float("nan")
        hard_p = float("nan")
        if not bayes_easy.empty and not base_easy.empty:
            easy_p = float(stats.ttest_ind(bayes_easy, base_easy, equal_var=False).pvalue)
        if not bayes_hard.empty and not base_hard.empty:
            hard_p = float(stats.ttest_ind(bayes_hard, base_hard, equal_var=False).pvalue)

        results[base] = {
            "easy_p_value": easy_p,
            "hard_p_value": hard_p,
        }

    return results


def main():
    df = load_results(RAW_PATH)

    gen = compute_generalization_score(df)
    rob = compute_robustness_index(df)
    ada = compute_adaptation_speed(df)
    trf = compute_cross_task_transfer(df)
    adv = compute_adaptation_advantage(df)
    easy_hard = compute_easy_hard_stats(df)
    bayes_vs = summarize_bayesian_vs_baselines(df)
    bayes_sig = bayesian_significance_tests(df)

    save_summary_json(gen, rob, ada, trf, adv, easy_hard, bayes_vs, bayes_sig)
    plot_generalization_curves(df)
    plot_easy_vs_hard(easy_hard)
    print(f"Saved Week 4 analysis summary and plots to {OUT_DIR}")


if __name__ == "__main__":
    main()
