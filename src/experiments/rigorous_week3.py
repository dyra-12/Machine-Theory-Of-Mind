"""
Rigorous Week 3 analysis with proper statistics
"""
from src.metrics.statistical_tests_fixed import FixedStatisticalAnalyzer
from src.metrics.pareto import ParetoAnalyzer
from src.experiments.data_validator import DataValidator
import json
from pathlib import Path

def run_rigorous_analysis():
    """Run comprehensive, statistically sound analysis"""
    
    # Load results: prefer a dedicated latest_results file, otherwise auto-discover
    raw_dir = Path("results/week3/raw")
    results_path = raw_dir / "latest_results.jsonl"

    if not results_path.exists():
        # Search for any results.jsonl inside subfolders and pick the newest
        candidates = list(raw_dir.rglob("results.jsonl"))
        if not candidates:
            print("❌ No results found. Run experiments first.")
            return
        # choose most recently modified
        results_path = max(candidates, key=lambda p: p.stat().st_mtime)
        print(f"ℹ️  Auto-discovered results file: {results_path}")
    
    # Load and validate data
    all_results = []
    with open(results_path, 'r') as f:
        for line in f:
            all_results.append(json.loads(line))
    
    print(f"📊 Loaded {len(all_results)} raw results")
    
    # Validate data structure
    validator = DataValidator()
    valid_results = validator.validate_results_structure(all_results)
    independence_checks = validator.check_independence_assumptions(valid_results)
    
    print(f"🔍 Data independence: {independence_checks}")
    
    # Group by agent type for analysis
    agent_results = {}
    for result in valid_results:
        agent_type = result['agent_type']
        if agent_type not in agent_results:
            agent_results[agent_type] = []
        agent_results[agent_type].append(result)
    
    print(f"🤖 Analyzing {len(agent_results)} agent types")
    
    # FIXED: Statistical analysis
    print("\n🎯 RUNNING FIXED STATISTICAL ANALYSIS...")
    fixed_analyzer = FixedStatisticalAnalyzer()
    
    # Test within lambda conditions
    within_lambda_tests = fixed_analyzer.perform_corrected_significance_tests(agent_results)
    
    # Test lambda sensitivity
    anova_results = fixed_analyzer.perform_anova_across_lambdas(agent_results)
    
    # Pareto analysis (this was already working)
    print("\n📈 RUNNING PARETO ANALYSIS...")
    pareto_analyzer = ParetoAnalyzer()
    pareto_metrics = pareto_analyzer.calculate_pareto_metrics(agent_results)
    
    # Generate rigorous report
    _generate_rigorous_report(within_lambda_tests, anova_results, pareto_metrics, 
                            independence_checks, agent_results)
    
    print("✅ RIGOROUS ANALYSIS COMPLETE!")

def _generate_rigorous_report(within_lambda_tests, anova_results, pareto_metrics, 
                            independence_checks, agent_results):
    """Generate statistically rigorous report"""
    report_path = Path("results/week3/rigorous_analysis_report.md")
    
    with open(report_path, 'w') as f:
        f.write("# 🎯 RIGOROUS Week 3 Analysis Report\n\n")
        f.write("**Note: Statistical methods have been properly implemented**\n\n")
        
        # Data quality
        f.write("## Data Quality Assessment\n\n")
        f.write(f"- Unique experimental configurations: {independence_checks['unique_configs']}\n")
        f.write(f"- Maximum repeats per config: {independence_checks['max_repeats']}\n")
        f.write(f"- Independence violation: {independence_checks['independence_violation']}\n\n")
        
        # Lambda sensitivity (ANOVA)
        f.write("## Lambda Sensitivity Analysis (ANOVA)\n\n")
        f.write("| Agent Type | F-statistic | p-value | Lambda Sensitive? |\n")
        f.write("|------------|-------------|---------|-------------------|\n")
        
        for agent_type, results in anova_results.items():
            sensitive = "✅" if results['lambda_sensitivity'] else "❌"
            f.write(f"| {agent_type} | {results['f_statistic']:.3f} | {results['p_value']:.4f} | {sensitive} |\n")
        
        # Within-lambda comparisons
        f.write("\n## Statistical Significance (Within Lambda Conditions)\n\n")
        f.write("| Comparison | p-value | Cohen's d | Significant? | Sample Sizes |\n")
        f.write("|------------|---------|-----------|--------------|--------------|\n")
        
        for comparison, results in within_lambda_tests.items():
            sig_symbol = "✅" if results['significant_0.05'] else "❌"
            f.write(f"| {comparison} | {results['p_value']:.4f} | {results['cohens_d']:.3f} | {sig_symbol} | {results['n1']}/{results['n2']} |\n")
        
        # Pareto analysis
        f.write("\n## Pareto Analysis\n\n")
        f.write("| Agent Type | Pareto AUC | Hypervolume | Pareto Points | Lambda Sensitive? |\n")
        f.write("|------------|------------|-------------|---------------|-------------------|\n")
        
        for agent_type, metrics in pareto_metrics.items():
            lambda_sensitive = anova_results.get(agent_type, {}).get('lambda_sensitivity', False)
            sensitive_symbol = "✅" if lambda_sensitive else "❌"
            f.write(f"| {agent_type} | {metrics['auc']:.3f} | {metrics['hypervolume']:.3f} | "
                   f"{metrics['num_pareto_points']} | {sensitive_symbol} |\n")
        
        # Key findings
        f.write("\n## Key Scientific Findings\n\n")
        
        # Count significant lambda-sensitive agents
        sensitive_agents = [agent for agent, results in anova_results.items() 
                          if results.get('lambda_sensitivity', False)]
        f.write(f"- **Lambda-sensitive agents**: {len(sensitive_agents)}/{len(anova_results)}\n")
        
        # Count multi-point Pareto agents
        multi_pareto_agents = [agent for agent, metrics in pareto_metrics.items() 
                             if metrics['num_pareto_points'] > 1]
        f.write(f"- **Multi-point Pareto agents**: {len(multi_pareto_agents)}/{len(pareto_metrics)}\n")
        
        # Bayesian MToM assessment
        bayesian_results = anova_results.get('bayesian_mtom', {})
        bayesian_pareto = pareto_metrics.get('bayesian_mtom', {})
        
        if bayesian_results.get('lambda_sensitivity', False) and bayesian_pareto.get('num_pareto_points', 0) > 1:
            f.write("- **✅ Bayesian MToM**: Demonstrates both lambda sensitivity AND multi-point Pareto optimization\n")
        else:
            f.write("- **❌ Bayesian MToM**: Does not demonstrate expected trade-off behavior\n")

if __name__ == "__main__":
    run_rigorous_analysis()