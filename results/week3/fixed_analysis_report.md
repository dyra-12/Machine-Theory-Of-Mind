# 🔧 FIXED Week 3 Analysis Report

**Note: Statistical and Pareto bugs have been fixed**

## Performance Summary

| Agent Type | Mean Utility | Std | 95% CI | Sample Size |
|------------|--------------|-----|--------|-------------|
| greedy_baseline | 0.873 | 0.100 | (0.843, 0.904) | 45 |
| social_baseline | 0.307 | 0.208 | (0.243, 0.370) | 45 |
| random_baseline | 0.627 | 0.181 | (0.572, 0.682) | 45 |
| simple_mtom | 1.066 | 0.182 | (1.011, 1.121) | 45 |
| bayesian_mtom | 0.967 | 0.186 | (0.911, 1.024) | 45 |

## Statistical Significance (FIXED)

- greedy_baseline_vs_social_baseline: p=0.0000, d=3.434 ***
- greedy_baseline_vs_random_baseline: p=0.0000, d=1.672 ***
- greedy_baseline_vs_simple_mtom: p=0.0000, d=-1.299 ***
- greedy_baseline_vs_bayesian_mtom: p=0.0043, d=-0.623 ***
- social_baseline_vs_random_baseline: p=0.0000, d=-1.624 ***
- social_baseline_vs_simple_mtom: p=0.0000, d=-3.844 ***
- social_baseline_vs_bayesian_mtom: p=0.0000, d=-3.310 ***
- random_baseline_vs_simple_mtom: p=0.0000, d=-2.397 ***
- random_baseline_vs_bayesian_mtom: p=0.0000, d=-1.837 ***
- simple_mtom_vs_bayesian_mtom: p=0.0140, d=0.529 **

## Pareto Analysis (FIXED)

| Agent Type | Pareto AUC | Hypervolume | Pareto Points | Total Points |
|------------|------------|-------------|---------------|--------------|
| greedy_baseline | 0.000 | 0.286 | 1 | 45 |
| social_baseline | 0.000 | 0.000 | 1 | 45 |
| random_baseline | 0.143 | 0.286 | 2 | 45 |
| simple_mtom | 0.000 | 0.226 | 1 | 45 |
| bayesian_mtom | 0.124 | 0.306 | 2 | 45 |

## SIQ Breakdown

| Agent Type | SIQ | Social Alignment | ToM Accuracy | Cross-Context | Ethical Consistency |
|------------|-----|------------------|--------------|---------------|---------------------|
| bayesian_mtom | 0.796 | 0.765 | 1.000 | nan | 0.622 |
| greedy_baseline | 0.524 | 0.561 | 0.945 | nan | 0.067 |
| random_baseline | 0.850 | 0.626 | 0.923 | nan | 1.000 |
| simple_mtom | 0.539 | 0.550 | 1.000 | nan | 0.067 |
| social_baseline | 0.989 | 0.968 | 1.000 | nan | 1.000 |
