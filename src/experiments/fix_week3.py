"""
Quick fix for Week 3 statistical and Pareto bugs
"""
import argparse
import json
import math
from pathlib import Path
from typing import Dict, Optional

import pandas as pd

from src.metrics.pareto import ParetoAnalyzer
from src.metrics.visualization import ResultVisualizer
from src.metrics.siq import SIQ, SIQConfig
from src.metrics.statistical_tests import StatisticalAnalyzer
from src.utils.config import load_config
from src.experiments.run_week4 import Week4GeneralizationRunner

DEFAULT_SIQ_CONFIG = Path("experiments/config/week6_siq.yaml")
DEFAULT_WEEK3_CONFIG = Path("experiments/config/week3_comprehensive.yaml")

def build_siq(config_path: Optional[Path]) -> SIQ:
    if config_path is None:
        return SIQ()
    try:
        return SIQ(SIQConfig.from_yaml(config_path))
    except FileNotFoundError:
        print(f"⚠️  SIQ config {config_path} not found, using defaults")
        return SIQ()


def fix_and_rerun_analysis(siq_config: Optional[Path] = None):
    """Load existing results, fix analysis, regenerate report"""
    
    # Load existing results
    raw_dir = Path("results/week3/raw")
    results_path = raw_dir / "latest_results.jsonl"
    if not results_path.exists():
        candidates = list(raw_dir.rglob("results.jsonl"))
        if not candidates:
            print("❌ No existing results found. Run experiments first.")
            return
        results_path = max(candidates, key=lambda p: p.stat().st_mtime)
        print(f"ℹ️  Auto-discovered results file: {results_path}")
    
    # Load and parse results
    all_results = []
    with open(results_path, 'r') as f:
        for line in f:
            all_results.append(json.loads(line))
    
    print(f"📊 Loaded {len(all_results)} results for re-analysis")

    if not all_results:
        print("⚠️  latest_results.jsonl is empty; generating Week 3 raw results now...")
        all_results = _generate_week3_raw_results()
        _write_latest_results_jsonl(all_results)
        print(f"✅ Generated {len(all_results)} episode results")

    all_results = _normalize_week3_result_schema(all_results)

    df = pd.DataFrame(all_results)
    
    # FIXED: Statistical analysis
    print("🔄 Running FIXED statistical analysis...")
    analyzer = StatisticalAnalyzer()
    agent_metrics = analyzer.calculate_agent_performance(all_results)
    significance_results = analyzer.perform_significance_tests(agent_metrics)
    confidence_intervals = analyzer.calculate_confidence_intervals(agent_metrics)
    
    # FIXED: Pareto analysis  
    print("🔄 Running FIXED Pareto analysis...")
    pareto_analyzer = ParetoAnalyzer()
    
    # Group by agent type
    agent_results = {}
    for result in all_results:
        agent_type = result['agent_type']
        if agent_type not in agent_results:
            agent_results[agent_type] = []
        agent_results[agent_type].append(result)
    
    pareto_metrics = pareto_analyzer.calculate_pareto_metrics(agent_results)

    # Regenerate plots
    print("🎨 Regenerating Week 3 plots...")
    plots_dir = Path("results/week3/plots")
    visualizer = ResultVisualizer(plots_dir)
    visualizer.create_pareto_plot(pareto_metrics, all_results)
    visualizer.create_performance_comparison(agent_metrics, significance_results)
    visualizer.create_lambda_sensitivity_plot(all_results)
    
    # Generate fixed report
    print("📋 Generating FIXED analysis report...")
    siq_scores = {}
    if not df.empty:
        siq = build_siq(siq_config or DEFAULT_SIQ_CONFIG)
        siq_scores = siq.compute_by_group(df, group_key="agent_type")

    _generate_fixed_report(
        agent_metrics,
        significance_results,
        pareto_metrics,
        confidence_intervals,
        siq_scores,
    )

    if siq_scores:
        save_siq_summary(siq_scores)
    
    print("✅ Week 3 fixes applied successfully!")


def _normalize_week3_result_schema(results):
    """Normalize keys so Week 3 analyzers work across runner variants."""
    normalized = []
    for r in results:
        row = dict(r)
        # Week4 runner uses `warmth`/`competence`; Week3 analysis expects `*_final`.
        if "warmth_final" not in row and "warmth" in row:
            row["warmth_final"] = row["warmth"]
        if "competence_final" not in row and "competence" in row:
            row["competence_final"] = row["competence"]

        # Ensure required numeric fields exist (avoid KeyError downstream)
        for k in ("task_reward", "social_score", "total_utility"):
            if k in row and row[k] is None:
                row[k] = 0.0

        normalized.append(row)
    return normalized


def _write_latest_results_jsonl(results) -> None:
    raw_dir = Path("results/week3/raw")
    raw_dir.mkdir(parents=True, exist_ok=True)
    out_path = raw_dir / "latest_results.jsonl"
    with open(out_path, "w") as f:
        for row in results:
            f.write(json.dumps(row) + "\n")


def _generate_week3_raw_results():
    """Generate a small but sufficient Week 3 dataset to enable plotting."""
    # Load the Week 3 config if present, but run a smaller sweep for speed.
    if DEFAULT_WEEK3_CONFIG.exists():
        base_cfg = load_config(str(DEFAULT_WEEK3_CONFIG))
    else:
        base_cfg = {
            "experiment": {"num_seeds": 3, "runs_per_config": 5},
            "environment": {"type": "negotiation_v1", "total_resources": 10, "max_turns": 3},
            "sweep_parameters": {
                "agent_types": ["greedy_baseline", "social_baseline", "random_baseline", "simple_mtom", "bayesian_mtom"],
                "lambda_values": [0.0, 0.5, 1.0],
            },
            "social_config": {"score_type": "linear", "warmth_weight": 0.6, "competence_weight": 0.4},
            "output": {"directory": "results/week3"},
        }

    agent_types = base_cfg.get("sweep_parameters", {}).get("agent_types", [])
    lambda_values = base_cfg.get("sweep_parameters", {}).get("lambda_values", [0.0, 0.5, 1.0])

    # Keep a small set of lambdas for speed, but include both 0 and >0.
    chosen_lambdas = []
    for v in lambda_values:
        if v in (0.0, 0.5, 1.0):
            chosen_lambdas.append(float(v))
    if not chosen_lambdas:
        chosen_lambdas = [0.0, 0.5, 1.0]

    exp_cfg = {
        "experiment": {
            "num_seeds": int(min(3, base_cfg.get("experiment", {}).get("num_seeds", 3))),
            "runs_per_config": int(min(5, base_cfg.get("experiment", {}).get("runs_per_config", 5))),
        },
        "environment": base_cfg.get("environment", {"total_resources": 10, "max_turns": 3}),
        "sweep_parameters": {
            "agent_types": agent_types,
            "lambda_values": chosen_lambdas,
            "observer_types": ["simple"],
            "env_variants": [{"name": "base"}],
            "opponent_types": ["fair"],
        },
        "social_config": base_cfg.get("social_config", {"score_type": "linear", "warmth_weight": 0.6, "competence_weight": 0.4}),
        "output": {"directory": "results/week3"},
    }

    runner = Week4GeneralizationRunner(exp_cfg)
    results = runner.run()
    return results


def save_siq_summary(siq_scores: Dict[str, Dict[str, float]]):
    out_dir = Path("results/week3")
    out_dir.mkdir(parents=True, exist_ok=True)
    payload = {"siq_by_agent": _sanitize_for_json(siq_scores)}
    (out_dir / "siq_summary.json").write_text(json.dumps(payload, indent=2))


def _sanitize_for_json(value):
    if isinstance(value, dict):
        return {k: _sanitize_for_json(v) for k, v in value.items()}
    if isinstance(value, float):
        if math.isnan(value) or math.isinf(value):
            return None
    return value

def _generate_fixed_report(
    agent_metrics,
    significance_results,
    pareto_metrics,
    confidence_intervals,
    siq_scores: Dict[str, Dict[str, float]],
):
    """Generate corrected analysis report"""
    report_path = Path("results/week3/fixed_analysis_report.md")
    
    with open(report_path, 'w') as f:
        f.write("# 🔧 FIXED Week 3 Analysis Report\n\n")
        f.write("**Note: Statistical and Pareto bugs have been fixed**\n\n")
        
        # Performance summary
        f.write("## Performance Summary\n\n")
        f.write("| Agent Type | Mean Utility | Std | 95% CI | Sample Size |\n")
        f.write("|------------|--------------|-----|--------|-------------|\n")
        
        for agent_type, metrics in agent_metrics.items():
            ci_data = confidence_intervals[agent_type]['total_utilities']
            n = len(metrics['total_utilities'])
            f.write(f"| {agent_type} | {ci_data['mean']:.3f} | {ci_data['std']:.3f} | "
                   f"({ci_data['ci_lower']:.3f}, {ci_data['ci_upper']:.3f}) | {n} |\n")
        
        # Significance results
        f.write("\n## Statistical Significance (FIXED)\n\n")
        for comparison, results in significance_results.items():
            sig_symbol = "***" if results['significant_0.01'] else "**" if results['significant_0.05'] else "ns"
            f.write(f"- {comparison}: p={results['p_value']:.4f}, d={results['cohens_d']:.3f} {sig_symbol}\n")
        
        # Pareto analysis
        f.write("\n## Pareto Analysis (FIXED)\n\n")
        f.write("| Agent Type | Pareto AUC | Hypervolume | Pareto Points | Total Points |\n")
        f.write("|------------|------------|-------------|---------------|--------------|\n")
        
        for agent_type, metrics in pareto_metrics.items():
            f.write(f"| {agent_type} | {metrics['auc']:.3f} | {metrics['hypervolume']:.3f} | "
                   f"{metrics['num_pareto_points']} | {metrics['total_points']} |\n")

        if siq_scores:
            f.write("\n## SIQ Breakdown\n\n")
            f.write("| Agent Type | SIQ | Social Alignment | ToM Accuracy | Cross-Context | Ethical Consistency |\n")
            f.write("|------------|-----|------------------|--------------|---------------|---------------------|\n")
            for agent_type, metrics in siq_scores.items():
                f.write(
                    f"| {agent_type} | {metrics.get('siq', float('nan')):.3f} | "
                    f"{metrics.get('social_alignment', float('nan')):.3f} | "
                    f"{metrics.get('theory_of_mind_accuracy', float('nan')):.3f} | "
                    f"{metrics.get('cross_context_generalization', float('nan')):.3f} | "
                    f"{metrics.get('ethical_consistency', float('nan')):.3f} |\n"
                )

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fix Week 3 analysis and recompute SIQ")
    parser.add_argument("--siq-config", type=Path, default=DEFAULT_SIQ_CONFIG, help="Path to SIQ YAML config")
    args = parser.parse_args()
    fix_and_rerun_analysis(args.siq_config)