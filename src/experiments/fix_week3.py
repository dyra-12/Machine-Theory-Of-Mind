"""
Quick fix for Week 3 statistical and Pareto bugs
"""
from src.metrics.statistical_tests import StatisticalAnalyzer
from src.metrics.pareto import ParetoAnalyzer
import json
from pathlib import Path

def fix_and_rerun_analysis():
    """Load existing results, fix analysis, regenerate report"""
    
    # Load existing results
    results_path = Path("results/week3/raw") / "latest_results.jsonl"
    if not results_path.exists():
        print("❌ No existing results found. Run experiments first.")
        return
    
    # Load and parse results
    all_results = []
    with open(results_path, 'r') as f:
        for line in f:
            all_results.append(json.loads(line))
    
    print(f"📊 Loaded {len(all_results)} results for re-analysis")
    
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
    _generate_fixed_report(agent_metrics, significance_results, pareto_metrics, confidence_intervals)
    
    print("✅ Week 3 fixes applied successfully!")

def _generate_fixed_report(agent_metrics, significance_results, pareto_metrics, confidence_intervals):
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

if __name__ == "__main__":
    fix_and_rerun_analysis()