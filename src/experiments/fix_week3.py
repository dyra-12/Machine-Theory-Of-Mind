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
from src.metrics.siq import SIQ, SIQConfig
from src.metrics.statistical_tests import StatisticalAnalyzer

DEFAULT_SIQ_CONFIG = Path("experiments/config/week6_siq.yaml")

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