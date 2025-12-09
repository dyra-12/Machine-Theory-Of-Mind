from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "results" / "week10" / "pilot_ratings_combined.csv"
OUT_DIR = ROOT / "results" / "week10"
OUT_DIR.mkdir(parents=True, exist_ok=True)


def load_data(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Could not find responses at {path}")
    return pd.read_csv(path)


def participant_level_summary(df: pd.DataFrame) -> pd.DataFrame:
    # compute per-participant (completion_code) mean for each agent_type and metric
    grouped = df.groupby(["completion_code", "agent_type"]).agg(
        warmth_mean=("warmth", "mean"),
        competence_mean=("competence", "mean"),
        trust_mean=("trust", "mean"),
        n_items=("dialogue_id", "count"),
    ).reset_index()
    # pivot so each row is participant, columns for agent types
    pivot = grouped.pivot(index="completion_code", columns="agent_type")
    # flatten columns
    pivot.columns = [f"{a}_{m}" for m, a in pivot.columns]
    pivot = pivot.reset_index()
    return pivot


def paired_tests(pivot: pd.DataFrame, agent_a: str = "MToM", agent_b: str = "Baseline"):
    results = {}
    metrics = ["warmth", "competence", "trust"]
    for m in metrics:
        col_a = f"{agent_a}_{m}_mean"
        col_b = f"{agent_b}_{m}_mean"
        if col_a not in pivot.columns or col_b not in pivot.columns:
            results[m] = {"error": "missing_columns"}
            continue
        a = pivot[col_a].dropna()
        b = pivot[col_b].dropna()
        # align indices
        common = pivot[[col_a, col_b]].dropna()
        diffs = common[col_a] - common[col_b]

        # Paired t-test
        t_stat, p_t = stats.ttest_rel(common[col_a], common[col_b])

        # Wilcoxon signed-rank test (non-parametric)
        try:
            w_stat, p_w = stats.wilcoxon(common[col_a], common[col_b])
        except Exception:
            w_stat, p_w = float("nan"), float("nan")

        # Cohen's d for paired samples (mean diff / sd diff)
        mean_diff = float(diffs.mean())
        sd_diff = float(diffs.std(ddof=1)) if len(diffs) > 1 else float("nan")
        cohens_d = mean_diff / sd_diff if sd_diff and np.isfinite(sd_diff) else float("nan")

        # Bootstrap 95% CI for mean difference
        rng = np.random.default_rng(12345)
        n_boot = 5000
        boots = []
        arr = diffs.values
        for _ in range(n_boot):
            sample = rng.choice(arr, size=len(arr), replace=True)
            boots.append(float(np.mean(sample)))
        lower = float(np.percentile(boots, 2.5))
        upper = float(np.percentile(boots, 97.5))

        results[m] = {
            "n_pairs": int(len(diffs)),
            "mean_a": float(common[col_a].mean()),
            "mean_b": float(common[col_b].mean()),
            "mean_diff": mean_diff,
            "t_stat": float(t_stat),
            "p_t": float(p_t),
            "w_stat": float(w_stat),
            "p_w": float(p_w),
            "cohens_d": float(cohens_d) if np.isfinite(cohens_d) else None,
            "ci_lower": lower,
            "ci_upper": upper,
        }

    return results


def save_results(results: dict, out_dir: Path):
    rows = []
    for metric, statsd in results.items():
        row = {"metric": metric}
        row.update(statsd)
        rows.append(row)
    df = pd.DataFrame(rows)
    df.to_csv(out_dir / "human_pilot_stats_summary.csv", index=False)
    return df


def plot_paired(pivot: pd.DataFrame, out_dir: Path, agent_a: str = "MToM", agent_b: str = "Baseline"):
    # Melt per-participant means for plotting
    metrics = ["warmth", "competence", "trust"]
    plot_rows = []
    for _, row in pivot.iterrows():
        pid = row["completion_code" ]
        for m in metrics:
            a_col = f"{agent_a}_{m}_mean"
            b_col = f"{agent_b}_{m}_mean"
            if a_col in pivot.columns and b_col in pivot.columns:
                plot_rows.append({"participant": pid, "metric": m, "agent": agent_a, "value": row.get(a_col)})
                plot_rows.append({"participant": pid, "metric": m, "agent": agent_b, "value": row.get(b_col)})
    plot_df = pd.DataFrame(plot_rows).dropna()

    sns.set(style="whitegrid")
    for m in metrics:
        pf = plot_df[plot_df["metric"] == m]
        plt.figure(figsize=(6, 4))
        # paired lines
        for pid, g in pf.groupby("participant"):
            vals = g.sort_values("agent")["value"].values
            if len(vals) == 2:
                plt.plot([0, 1], vals, color="gray", alpha=0.6)
        # boxplot
        sns.boxplot(x="agent", y="value", data=pf, palette=["#2b8cbe", "#f03b20"])
        sns.swarmplot(x="agent", y="value", data=pf, color="k", size=4)
        plt.title(f"Paired comparison — {m.title()}")
        plt.ylabel("Rating (1-7)")
        plt.ylim(0.5, 7.5)
        plt.tight_layout()
        plt.savefig(out_dir / f"human_pilot_paired_{m}.png", dpi=300)
        plt.close()


def main():
    df = load_data(DATA_PATH)
    pivot = participant_level_summary(df)
    # write pivot
    pivot.to_csv(OUT_DIR / "human_pilot_participant_means.csv", index=False)

    results = paired_tests(pivot)
    summary_df = save_results(results, OUT_DIR)
    print(summary_df.to_string(index=False))

    plot_paired(pivot, OUT_DIR)


if __name__ == "__main__":
    main()
