"""
Main Week 3 execution script - runs comprehensive analysis
"""
import argparse
from pathlib import Path

from src.utils.config import load_config
from src.experiments.advanced_runner import AdvancedExperimentRunner
from src.metrics.statistical_tests import StatisticalAnalyzer
from src.metrics.pareto import ParetoAnalyzer
from src.metrics.visualization import ResultVisualizer

def main():
    parser = argparse.ArgumentParser(description='Run Week 3 comprehensive analysis')
    parser.add_argument('--config', type=str, required=True,
                       help='Path to config YAML file')
    
    args = parser.parse_args()
    
    # Load configuration
    config = load_config(args.config)
    
    print("🚀 Starting Week 3 Comprehensive Analysis")
    print("=" * 60)
    
    # Step 1: Run experiments
    print("📊 Step 1: Running parameter sweep...")
    runner = AdvancedExperimentRunner(config)
    all_results = runner.run_parameter_sweep()
    
    print(f"✅ Collected {len(all_results)} experiment results")
    
    # Step 2: Statistical analysis
    print("📈 Step 2: Performing statistical analysis...")
    analyzer = StatisticalAnalyzer()
    agent_metrics = analyzer.calculate_agent_performance(all_results)
    significance_results = analyzer.perform_significance_tests(agent_metrics)
    confidence_intervals = analyzer.calculate_confidence_intervals(agent_metrics)
    
    # Step 3: Pareto analysis
    print("🎯 Step 3: Calculating Pareto frontiers...")
    pareto_analyzer = ParetoAnalyzer()
    
    # Group results by agent type for Pareto analysis
    agent_results = {}
    for result in all_results:
        agent_type = result['agent_type']
        if agent_type not in agent_results:
            agent_results[agent_type] = []
        agent_results[agent_type].append(result)
    
    pareto_metrics = pareto_analyzer.calculate_pareto_metrics(agent_results)
    
    # Step 4: Visualization
    print("🎨 Step 4: Generating visualizations...")
    output_dir = Path(config['output']['directory']) / "plots"
    visualizer = ResultVisualizer(output_dir)
    
    plots = {
        'pareto': visualizer.create_pareto_plot(pareto_metrics, all_results),
        'performance': visualizer.create_performance_comparison(agent_metrics, significance_results),
        'lambda_sensitivity': visualizer.create_lambda_sensitivity_plot(all_results)
    }
    
    # Step 5: Generate summary report
    print("📋 Step 5: Generating analysis report...")
    _generate_summary_report(agent_metrics, significance_results, pareto_metrics, 
                           confidence_intervals, plots, config)
    
    print("🎉 Week 3 analysis complete!")
    print(f"📁 Results saved to: {config['output']['directory']}")

def _generate_summary_report(agent_metrics, significance_results, pareto_metrics,
                           confidence_intervals, plots, config):
    """Generate comprehensive analysis report"""
    report_path = Path(config['output']['directory']) / "analysis_report.md"
    
    with open(report_path, 'w') as f:
        f.write("# Week 3 Analysis Report\n\n")
        
        # Performance summary
        f.write("## Performance Summary\n\n")
        f.write("| Agent Type | Mean Utility | Std | 95% CI |\n")
        f.write("|------------|--------------|-----|--------|\n")
        
        for agent_type, metrics in agent_metrics.items():
            ci_data = confidence_intervals[agent_type]['total_utilities']
            f.write(f"| {agent_type} | {ci_data['mean']:.3f} | {ci_data['std']:.3f} | "
                   f"({ci_data['ci_lower']:.3f}, {ci_data['ci_upper']:.3f}) |\n")
        
        # Significance results
        f.write("\n## Statistical Significance\n\n")
        for comparison, results in significance_results.items():
            sig_symbol = "***" if results['significant_0.01'] else "**" if results['significant_0.05'] else ""
            f.write(f"- {comparison}: p={results['p_value']:.4f}, d={results['cohens_d']:.3f} {sig_symbol}\n")
        
        # Pareto analysis
        f.write("\n## Pareto Analysis\n\n")
        f.write("| Agent Type | Pareto AUC | Hypervolume | Pareto Points |\n")
        f.write("|------------|------------|-------------|---------------|\n")
        
        for agent_type, metrics in pareto_metrics.items():
            f.write(f"| {agent_type} | {metrics['auc']:.3f} | {metrics['hypervolume']:.3f} | "
                   f"{metrics['num_pareto_points']} |\n")
        
        # Plots section
        f.write("\n## Generated Plots\n\n")
        for plot_name, plot_path in plots.items():
            f.write(f"### {plot_name.replace('_', ' ').title()}\n\n")
            f.write(f"![{plot_name}]({plot_path.relative_to(Path(config['output']['directory']))})\n\n")

if __name__ == "__main__":
    main()