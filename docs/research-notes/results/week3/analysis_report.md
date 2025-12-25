# Week 3 Analysis Report

## Performance Summary

| Agent Type | Mean Utility | Std | 95% CI |
|------------|--------------|-----|--------|
| greedy_baseline | 1.325 | 0.393 | (1.306, 1.343) |
| social_baseline | 0.606 | 0.468 | (0.584, 0.627) |
| random_baseline | 1.165 | 0.431 | (1.145, 1.185) |
| simple_mtom | 1.361 | 0.383 | (1.343, 1.379) |
| bayesian_mtom | 1.100 | 0.337 | (1.085, 1.116) |

## Statistical Significance

- greedy_baseline_vs_social_baseline: p=0.0000, d=1.663 ***
- greedy_baseline_vs_random_baseline: p=0.0000, d=0.387 ***
- greedy_baseline_vs_simple_mtom: p=0.0049, d=-0.094 ***
- greedy_baseline_vs_bayesian_mtom: p=0.0000, d=0.612 ***
- social_baseline_vs_random_baseline: p=0.0000, d=-1.244 ***
- social_baseline_vs_simple_mtom: p=0.0000, d=-1.766 ***
- social_baseline_vs_bayesian_mtom: p=0.0000, d=-1.213 ***
- random_baseline_vs_simple_mtom: p=0.0000, d=-0.481 ***
- random_baseline_vs_bayesian_mtom: p=0.0000, d=0.167 ***
- simple_mtom_vs_bayesian_mtom: p=0.0000, d=0.722 ***

## Pareto Analysis

| Agent Type | Pareto AUC | Hypervolume | Pareto Points |
|------------|------------|-------------|---------------|
| greedy_baseline | 0.000 | 0.378 | 1 |
| social_baseline | 0.000 | 0.050 | 1 |
| random_baseline | 0.000 | 0.322 | 1 |
| simple_mtom | 0.000 | 0.250 | 1 |
| bayesian_mtom | 0.185 | 0.249 | 3 |

## Generated Plots

### Pareto

![pareto](plots/pareto_frontiers.png)

### Performance

![performance](plots/performance_comparison.png)

### Lambda Sensitivity

![lambda_sensitivity](plots/lambda_sensitivity.png)

