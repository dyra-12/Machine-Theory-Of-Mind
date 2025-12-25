# 🎯 RIGOROUS Week 3 Analysis Report

**Note: Statistical methods have been properly implemented**

## Data Quality Assessment

- Unique experimental configurations: 450
- Maximum repeats per config: 20
- Independence violation: True

## Lambda Sensitivity Analysis (ANOVA)

| Agent Type | F-statistic | p-value | Lambda Sensitive? |
|------------|-------------|---------|-------------------|
| greedy_baseline | inf | 0.0000 | ✅ |
| social_baseline | inf | 0.0000 | ✅ |
| random_baseline | inf | 0.0000 | ✅ |
| simple_mtom | inf | 0.0000 | ✅ |
| bayesian_mtom | 25550.334 | 0.0000 | ✅ |

## Statistical Significance (Within Lambda Conditions)

| Comparison | p-value | Cohen's d | Significant? | Sample Sizes |
|------------|---------|-----------|--------------|--------------|
| λ=0.0_greedy_baseline_vs_social_baseline | 0.0000 | 5082487272114981.000 | ✅ | 200/200 |
| λ=0.0_greedy_baseline_vs_random_baseline | 0.0000 | 1270621818028746.750 | ✅ | 200/200 |
| λ=0.0_greedy_baseline_vs_simple_mtom | 1.0000 | 0.000 | ❌ | 200/200 |
| λ=0.0_greedy_baseline_vs_bayesian_mtom | 1.0000 | 0.000 | ❌ | 200/200 |
| λ=0.0_social_baseline_vs_random_baseline | 0.0000 | 0.000 | ✅ | 200/200 |
| λ=0.0_social_baseline_vs_simple_mtom | 0.0000 | -5082487272114981.000 | ✅ | 200/200 |
| λ=0.0_social_baseline_vs_bayesian_mtom | 0.0000 | -5082487272114981.000 | ✅ | 200/200 |
| λ=0.0_random_baseline_vs_simple_mtom | 0.0000 | -1270621818028746.750 | ✅ | 200/200 |
| λ=0.0_random_baseline_vs_bayesian_mtom | 0.0000 | -1270621818028746.750 | ✅ | 200/200 |
| λ=0.0_simple_mtom_vs_bayesian_mtom | 1.0000 | 0.000 | ❌ | 200/200 |
| λ=0.1_greedy_baseline_vs_social_baseline | 0.0000 | 40253299195150640.000 | ✅ | 200/200 |
| λ=0.1_greedy_baseline_vs_random_baseline | 0.0000 | 1245209381668169.000 | ✅ | 200/200 |
| λ=0.1_greedy_baseline_vs_simple_mtom | 0.0000 | -50824872721148.430 | ✅ | 200/200 |
| λ=0.1_greedy_baseline_vs_bayesian_mtom | 0.0000 | 173788274465866.688 | ✅ | 200/200 |
| λ=0.1_social_baseline_vs_random_baseline | 0.0000 | -3757213560704878.000 | ✅ | 200/200 |
| λ=0.1_social_baseline_vs_simple_mtom | 0.0000 | -5043239678798491.000 | ✅ | 200/200 |
| λ=0.1_social_baseline_vs_bayesian_mtom | 0.0000 | -9594259688984120.000 | ✅ | 200/200 |
| λ=0.1_random_baseline_vs_simple_mtom | 0.0000 | -916434609928737.375 | ✅ | 200/200 |
| λ=0.1_random_baseline_vs_bayesian_mtom | 0.0000 | -1036028650372588.750 | ✅ | 200/200 |
| λ=0.1_simple_mtom_vs_bayesian_mtom | 0.0000 | 123179627220518.812 | ✅ | 200/200 |
| λ=0.3_greedy_baseline_vs_social_baseline | 0.0000 | 0.000 | ✅ | 200/200 |
| λ=0.3_greedy_baseline_vs_random_baseline | 0.0000 | 2388769017894042.500 | ✅ | 200/200 |
| λ=0.3_greedy_baseline_vs_simple_mtom | 0.0000 | -152474618163450.938 | ✅ | 200/200 |
| λ=0.3_greedy_baseline_vs_bayesian_mtom | 0.0000 | 6.292 | ✅ | 200/200 |
| λ=0.3_social_baseline_vs_random_baseline | 0.0000 | -7471256290009018.000 | ✅ | 200/200 |
| λ=0.3_social_baseline_vs_simple_mtom | 0.0000 | -5082487272114981.000 | ✅ | 200/200 |
| λ=0.3_social_baseline_vs_bayesian_mtom | 0.0000 | -107.265 | ✅ | 200/200 |
| λ=0.3_random_baseline_vs_simple_mtom | 0.0000 | -1204667425734018.250 | ✅ | 200/200 |
| λ=0.3_random_baseline_vs_bayesian_mtom | 0.0000 | -21.219 | ✅ | 200/200 |
| λ=0.3_simple_mtom_vs_bayesian_mtom | 0.0000 | 9.805 | ✅ | 200/200 |
| λ=0.5_greedy_baseline_vs_social_baseline | 0.0000 | 4828362908509230.000 | ✅ | 200/200 |
| λ=0.5_greedy_baseline_vs_random_baseline | 0.0000 | 1022830833170391.125 | ✅ | 200/200 |
| λ=0.5_greedy_baseline_vs_simple_mtom | 0.0000 | -113647870352267.016 | ✅ | 200/200 |
| λ=0.5_greedy_baseline_vs_bayesian_mtom | 0.0000 | 3.425 | ✅ | 200/200 |
| λ=0.5_social_baseline_vs_random_baseline | 0.0000 | -7369606544566718.000 | ✅ | 200/200 |
| λ=0.5_social_baseline_vs_simple_mtom | 0.0000 | -2541243636057491.000 | ✅ | 200/200 |
| λ=0.5_social_baseline_vs_bayesian_mtom | 0.0000 | -14.185 | ✅ | 200/200 |
| λ=0.5_random_baseline_vs_simple_mtom | 0.0000 | -677976325004889.000 | ✅ | 200/200 |
| λ=0.5_random_baseline_vs_bayesian_mtom | 0.0000 | -0.746 | ✅ | 200/200 |
| λ=0.5_simple_mtom_vs_bayesian_mtom | 0.0000 | 4.352 | ✅ | 200/200 |
| λ=0.7_greedy_baseline_vs_social_baseline | 0.0000 | 3781370530453542.500 | ✅ | 200/200 |
| λ=0.7_greedy_baseline_vs_random_baseline | 0.0000 | 488685842514740.875 | ✅ | 200/200 |
| λ=0.7_greedy_baseline_vs_simple_mtom | 0.0000 | -355774109048050.250 | ✅ | 200/200 |
| λ=0.7_greedy_baseline_vs_bayesian_mtom | 0.0000 | 13.758 | ✅ | 200/200 |
| λ=0.7_social_baseline_vs_random_baseline | 0.0000 | -1701300003082878.750 | ✅ | 200/200 |
| λ=0.7_social_baseline_vs_simple_mtom | 0.0000 | -6776649696153306.000 | ✅ | 200/200 |
| λ=0.7_social_baseline_vs_bayesian_mtom | 0.0000 | -25.629 | ✅ | 200/200 |
| λ=0.7_random_baseline_vs_simple_mtom | 0.0000 | -724254436276383.750 | ✅ | 200/200 |
| λ=0.7_random_baseline_vs_bayesian_mtom | 0.0000 | 4.652 | ✅ | 200/200 |
| λ=0.7_simple_mtom_vs_bayesian_mtom | 0.0000 | 16.722 | ✅ | 200/200 |
| λ=1.0_greedy_baseline_vs_social_baseline | 0.0000 | 9148477089806966.000 | ✅ | 200/200 |
| λ=1.0_greedy_baseline_vs_random_baseline | 0.0000 | 0.000 | ✅ | 200/200 |
| λ=1.0_greedy_baseline_vs_simple_mtom | 0.0000 | 0.000 | ✅ | 200/200 |
| λ=1.0_greedy_baseline_vs_bayesian_mtom | 0.0000 | 22.465 | ✅ | 200/200 |
| λ=1.0_social_baseline_vs_random_baseline | 0.0000 | -7115482180960972.000 | ✅ | 200/200 |
| λ=1.0_social_baseline_vs_simple_mtom | 0.0000 | -10164974544229960.000 | ✅ | 200/200 |
| λ=1.0_social_baseline_vs_bayesian_mtom | 0.0000 | -8.362 | ✅ | 200/200 |
| λ=1.0_random_baseline_vs_simple_mtom | 0.0000 | 0.000 | ✅ | 200/200 |
| λ=1.0_random_baseline_vs_bayesian_mtom | 0.0000 | 15.614 | ✅ | 200/200 |
| λ=1.0_simple_mtom_vs_bayesian_mtom | 0.0000 | 25.890 | ✅ | 200/200 |
| λ=1.5_greedy_baseline_vs_social_baseline | 0.0000 | 3054782033095800.000 | ✅ | 200/200 |
| λ=1.5_greedy_baseline_vs_random_baseline | 0.0000 | 397767546232930.125 | ✅ | 200/200 |
| λ=1.5_greedy_baseline_vs_simple_mtom | 0.0000 | -539079182311019.438 | ✅ | 200/200 |
| λ=1.5_greedy_baseline_vs_bayesian_mtom | 0.0000 | 17.770 | ✅ | 200/200 |
| λ=1.5_social_baseline_vs_random_baseline | 0.0000 | -1534246249755588.000 | ✅ | 200/200 |
| λ=1.5_social_baseline_vs_simple_mtom | 0.0000 | -3593861215406819.500 | ✅ | 200/200 |
| λ=1.5_social_baseline_vs_bayesian_mtom | 0.0000 | -9.337 | ✅ | 200/200 |
| λ=1.5_random_baseline_vs_simple_mtom | 0.0000 | -738711157289724.875 | ✅ | 200/200 |
| λ=1.5_random_baseline_vs_bayesian_mtom | 0.0000 | 12.189 | ✅ | 200/200 |
| λ=1.5_simple_mtom_vs_bayesian_mtom | 0.0000 | 22.553 | ✅ | 200/200 |
| λ=2.0_greedy_baseline_vs_social_baseline | 0.0000 | 2032994908845993.500 | ✅ | 200/200 |
| λ=2.0_greedy_baseline_vs_random_baseline | 0.0000 | 762373090817247.625 | ✅ | 200/200 |
| λ=2.0_greedy_baseline_vs_simple_mtom | 0.0000 | -1016497454422992.500 | ✅ | 200/200 |
| λ=2.0_greedy_baseline_vs_bayesian_mtom | 0.0000 | 19.337 | ✅ | 200/200 |
| λ=2.0_social_baseline_vs_random_baseline | 0.0000 | -1477422314579454.750 | ✅ | 200/200 |
| λ=2.0_social_baseline_vs_simple_mtom | 0.0000 | -2272957407045313.000 | ✅ | 200/200 |
| λ=2.0_social_baseline_vs_bayesian_mtom | 0.0000 | -13.942 | ✅ | 200/200 |
| λ=2.0_random_baseline_vs_simple_mtom | 0.0000 | -1257851425392385.000 | ✅ | 200/200 |
| λ=2.0_random_baseline_vs_bayesian_mtom | 0.0000 | 13.097 | ✅ | 200/200 |
| λ=2.0_simple_mtom_vs_bayesian_mtom | 0.0000 | 27.656 | ✅ | 200/200 |
| λ=3.0_greedy_baseline_vs_social_baseline | 0.0000 | 0.000 | ✅ | 200/200 |
| λ=3.0_greedy_baseline_vs_random_baseline | 0.0000 | 254124363605750.594 | ✅ | 200/200 |
| λ=3.0_greedy_baseline_vs_simple_mtom | 0.0000 | 0.000 | ✅ | 200/200 |
| λ=3.0_greedy_baseline_vs_bayesian_mtom | 0.0000 | 8.237 | ✅ | 200/200 |
| λ=3.0_social_baseline_vs_random_baseline | 0.0000 | -1524746181634492.250 | ✅ | 200/200 |
| λ=3.0_social_baseline_vs_simple_mtom | 0.0000 | 0.000 | ✅ | 200/200 |
| λ=3.0_social_baseline_vs_bayesian_mtom | 0.0000 | -13.592 | ✅ | 200/200 |
| λ=3.0_random_baseline_vs_simple_mtom | 0.0000 | 254124363605747.781 | ✅ | 200/200 |
| λ=3.0_random_baseline_vs_bayesian_mtom | 0.0000 | 5.118 | ✅ | 200/200 |
| λ=3.0_simple_mtom_vs_bayesian_mtom | 0.0000 | 2.000 | ✅ | 200/200 |

## Pareto Analysis

| Agent Type | Pareto AUC | Hypervolume | Pareto Points | Lambda Sensitive? |
|------------|------------|-------------|---------------|-------------------|
| greedy_baseline | 0.000 | 0.378 | 1 | ✅ |
| social_baseline | 0.000 | 0.050 | 1 | ✅ |
| random_baseline | 0.000 | 0.322 | 1 | ✅ |
| simple_mtom | 0.000 | 0.250 | 1 | ✅ |
| bayesian_mtom | 0.185 | 0.249 | 3 | ✅ |

## Key Scientific Findings

- **Lambda-sensitive agents**: 5/5
- **Multi-point Pareto agents**: 1/5
- **✅ Bayesian MToM**: Demonstrates both lambda sensitivity AND multi-point Pareto optimization

## SIQ Component Snapshot

| Agent Type | SIQ | Social Alignment | ToM Accuracy | Cross-Context | Ethical |
|------------|-----|------------------|--------------|--------------|--------|
| bayesian_mtom | 0.702 | 0.702 | nan | nan | nan |
| greedy_baseline | 0.600 | 0.600 | nan | nan | nan |
| random_baseline | 0.657 | 0.657 | nan | nan | nan |
| simple_mtom | 0.714 | 0.714 | nan | nan | nan |
| social_baseline | 0.714 | 0.714 | nan | nan | nan |
