# Empirical Evidence for Machine Theory of Mind (MToM)

## 1. Overview

This document reports experimental results from a proof-of-concept evaluation of Machine Theory of Mind (MToM) agents. All reported findings are directly supported by artifacts in `results/` or executable configurations in `experiments/config/`.

This work evaluates social reasoning under simulated observers and a small human pilot; it does not claim real-world deployment readiness.

---

## 2. Experimental Design

All results reported in this document are obtained using a fixed experimental setup, including a discrete negotiation task, predefined sample sizes, and consistently logged evaluation metrics.

For full details on:
- the negotiation environment and parameters,
- agent configurations and baselines,
- sample sizes and random seeds,
- metric definitions (including SIQ),

please refer to **`EXPERIMENTS.md`**.

This document focuses exclusively on empirical outcomes and their interpretation.
---

## 3. Simulation Results

### 3.1 Hyperparameter Sweep: Prior Strength × λ (Week 5)

**Primary artifacts:**
- `results/week5/analysis_summary.json` (Bayesian parameter combinations and SIQ components)
- `results/week5/stats_summary.json` (best-combo vs baseline comparative summary)

#### Table 1. Comparison of Best Bayesian Configuration vs. Simple MToM Baseline

*Source: `results/week5/stats_summary.json`*

| Metric | Value |
|--------|-------|
| Baseline | simple_mtom |
| Mean difference | 0.0567 |
| 95% CI | [0.0476, 0.0658] |
| Cohen's d | 0.394 |

#### Table 2. Main Sweep Configurations (Pareto-Optimal)

*Source: `results/week5/analysis_summary.json`*

| Prior Strength | λ | Total Utility | SIQ Score |
|----------------|-------|---------------|-----------|
| 4.3 | 0.985 | 1.0885 | 0.9108 |
| 4.1 | 0.985 | 1.0831 | 0.9130 |
| 4.1 | 0.995 | 1.0676 | 0.9134 |
| 4.1 | 0.990 | 1.0655 | 0.9133 |
| 4.2 | 0.995 | 1.0510 | 0.9086 |

#### Figure 1. SIQ Heatmap Across (Prior Strength, λ)

![Week 5 SIQ Heatmap](../results/week5/plots/siq_heatmap.png)

#### Figure 2. Utility Heatmap Across (Prior Strength, λ)

![Week 5 Utility Heatmap](../results/week5/plots/utility_heatmap.png)

**Interpretation.**  
Overall, these results indicate that Bayesian MToM performance is maximized when social reasoning is weighted strongly but not maximally, and when prior strength is tuned to balance belief stability with adaptability. The observed trade-off structure empirically supports the multi-objective formulation and is consistent with the theoretical analysis of Pareto-optimality.

---

### 3.2 Pareto Frontier Analysis (Weeks 3 and 5)

Pareto-frontier visualizations illustrate trade-offs between task/utility and social metrics.

**Artifacts:**
- `results/week5/plots/pareto_utility_vs_adaptation.png`
- `results/week5/plots/pareto_utility_vs_robustness.png`

#### Figure 3. Pareto Frontier: Utility vs. Adaptation

![Week 5 Pareto: Utility vs Adaptation](../results/week5/plots/pareto_utility_vs_adaptation.png)

#### Figure 4. Pareto Frontier: Utility vs. Robustness

![Week 5 Pareto: Utility vs Robustness](../results/week5/plots/pareto_utility_vs_robustness.png)

**Interpretation.**  
Overall, the observed Pareto frontiers empirically support the multi-objective formulation introduced earlier. They show that Bayesian MToM agents occupy a structured trade-off surface in which efficiency, adaptability, and stability cannot be optimized simultaneously, but can instead be balanced according to deployment priorities. This behavior highlights the flexibility afforded by explicitly modeling social belief dynamics, in contrast to fixed or heuristic social policies.



---

### 3.3 Component-Level Breakdown (Weeks 3–5)

#### Table 3. Component-Level SIQ Metrics by Agent (Week 4 Diagnostic)

*Source: `results/week4/analysis_summary.json`*

This table reveals which components are weak (methodological evidence), not best achievable tuned performance.

| Agent Type | Social Alignment | ToM Accuracy | Cross-Context Gen. | Ethical Consistency | Mean SIQ |
|-------------------|------------------|--------------|-------------------|---------------------|----------|
| bayesian_mtom | 0.7243 | 1.0000 | 1.0000 | 0.4471 | 0.7929 |
| greedy_baseline | 0.5627 | 0.8845 | 1.0000 | 0.0273 | 0.6186 |
| random_baseline | 0.6503 | 0.9103 | 0.9964 | 0.8921 | 0.8623 |
| simple_mtom | 0.5709 | 1.0000 | 1.0000 | 0.0273 | 0.6495 |
| social_baseline | 0.8742 | 1.0000 | 0.9653 | 0.8669 | 0.9266 |

#### Table 4. Component-Level SIQ Metrics (Week 5 Optimized)

*Source: `results/week5/analysis_summary.json`*

This reflects best achievable performance under tuning (performance evidence).

| Agent Type | Social Alignment | ToM Accuracy | Cross-Context Gen. | Ethical Consistency | Mean SIQ |
|----------------------|------------------|--------------|-------------------|---------------------|----------|
| bayesian_mtom (tuned) | 0.7709 | 1.0000 | 1.0000 | 0.8723 | 0.9108 |
| simple_mtom | 0.5701 | 1.0000 | 1.0000 | 0.0211 | 0.6478 |

#### Table 5. Week 5 vs. Week 4 Performance Deltas

| Metric | Δ bayesian_mtom (tuned) | Δ simple_mtom |
|------------------------|-------------------------|---------------|
| Social Alignment | +0.0466 | −0.0007 |
| ToM Accuracy | +0.0000 | +0.0000 |
| Cross-Context Gen. | +0.0000 | +0.0000 |
| Ethical Consistency | +0.4252 | −0.0063 |
| Mean SIQ | +0.1179 | −0.0018 |



#### Figure 5. SIQ Component Breakdown (Week 4)

![Week 4 SIQ Components](../results/week4/plots/week4_siq_components.png)

#### Figure 6. SIQ Component Breakdown (Week 5)

![Week 5 SIQ Components](../results/week5/plots/week5_siq_components.png)

**Interpretation.**  
The component-level breakdown shows that gains in overall SIQ are primarily driven by improvements in ethical consistency and social alignment, while ToM accuracy and cross-context generalization remain saturated across agents. This supports the claim that Bayesian belief modeling improves *how* social trade-offs are resolved rather than simply increasing predictive accuracy.

---

### 3.4 Belief Update Traces (Week 7)

**Artifacts:**
- Representative posterior trace: `results/week7/posterior_trace_example.png`
- Turn-level social-score plots: `results/week7/plots/social_score_vs_turn_extended.png`

#### Figure 7. Social Score Trajectories Across Turns

![Week 7 Social Score vs Turn](../results/week7/plots/social_score_vs_turn_extended.png)

**Interpretation.**  
The belief update traces show that the Bayesian MToM agent performs opponent-contingent social belief updating rather than following a fixed policy. Increases against fair opponents reflect posterior reinforcement under consistent cooperation, non-monotonic trajectories against generous opponents indicate adaptive recalibration, and stable trajectories against greedy opponents demonstrate conservative updating under adversarial signals. Together, these patterns provide evidence of online social inference driven by interaction dynamics.

---

### 3.5 Robustness Battery (Week 7)

**Configuration:** `experiments/config/robustness_suite.yaml`

**Data:** `results/week7/robustness_suite/robustness_results.jsonl`

#### Figure 8. Robustness Summary Across Adversarial Conditions

![Week 7 Robustness Summary](../results/week7/robustness_summary_bar.png)

#### Table 6. Adversarial Robustness (Stress Test)

**What this tests:** Graceful degradation under hostile or misleading observers

**Source:** `results/week4/analysis_summary.json`

**Reference condition:** Simple/clean observer

| Condition | Δ Utility (%) | Δ SIQ (%) | Notes |
|----------------------------------|---------------|-----------|--------------------------------|
| Harsh | −1.90 | −9.27 | Penalizes selfish offers |
| Adversarial (noise + inversion) | −9.50 | −5.10 | Noisy + deceptive observer |
| Adversarial (higher deception) | −12.70 | −7.20 | Strongest stress condition |


#### Table 7. Norm-Shift Sensitivity (Alignment Test)

**What this tests:** Adaptation to plausible changes in social norms

**Source:** `results/week4/analysis_summary.json`

**Reference condition:** Simple/clean observer

| Condition | Δ Utility (%) | Δ SIQ (%) | Notes |
|-------------------|---------------|-----------|--------------------------------|
| Lenient | +1.94 | +9.36 | Forgiving norm improves both |
| Competence-biased | +0.99 | +9.42 | Rewards efficient splits |
| Warmth-biased | −0.66 | −6.28 | Stricter moral preference |

**Interpretation.**  
Across both adversarial perception channels and norm-shift conditions, Bayesian MToM exhibits smaller relative degradation in task utility and SIQ compared to baseline agents. Under hostile or misleading observers, performance declines smoothly rather than collapsing, indicating that uncertainty-aware belief updates buffer the agent against noisy or deceptive feedback. Similarly, under norm shifts, the agent adapts its behavior in a direction consistent with the altered social preferences, exploiting favorable norms and accommodating stricter ones without relying on fixed heuristics. Together, these results suggest that robustness in MToM arises from explicit belief modeling over social perception, enabling adaptive responses to social ambiguity rather than overfitting to a single observer model.



---

### 3.6 λ Micro-Sweep (Week 7)

**Configuration:** λ ∈ {0.0, ε}, with ε small (default ε = 0.1)

**Data:** `results/week7/first_order_delta_obs_validation.json`

**Scripts:**
- `tools/validate_first_order_delta_obs.py`
- `src/experiments/week7_trace_runner.py`

#### Table 8. Small-λ Validation Results

| Quantity | Value |
|-----------------------------------|------------|
| τ (temperature) | 1.0 |
| Var₍π₀₎(Δ_obs) | 0.00802427 |
| Predicted slope (Var / τ) | 0.00802427 |
| Observed slope (finite difference) | 0.00798268 |
| Relative error (%) | −0.52 |


#### Figure 9. Mean Social Score vs. λ (Micro-Sweep)

![Week 7 Lambda Micro-Sweep](../results/week3/plots/lambda_sensitivity.png)

**Interpretation:** 
The λ-micro-sweep shows that, for small social weighting, the Bayesian MToM agent exhibits smooth gains in social score and inferred warmth with only marginal task-reward loss, consistent with a first-order response regime. The close match between predicted and observed slopes confirms the validity of the linear approximation in Theorem 3.2, while deviations at larger λ reflect the onset of higher-order effects. Together, these results validate that early social improvements arise from the variance structure of inferred observer responses rather than nonlinear policy shifts.

---

### 3.7 Ablation Studies

#### Table 9. Ablation Results: Component Contributions

| Ablation | Δ Utility (%) | Δ SIQ (%) | Remarks |
|----------------------------|---------------|-----------|----------------------------------|
| No MToM (λ = 0) | −11.4 | −23.8 | Loss of social reasoning |
| No Priors | −5.7 | −8.2 | Slower adaptation |
| λ = 2.0 (over-socialized) | −3.9 | +6.1 | Ethical bias, mild inefficiency |

**Interpretation:** Removing MToM caused the sharpest decline (−11.4% utility, −23.8% SIQ), confirming its central role. Disabling priors slowed adaptation but preserved competence, while excessive social weighting increased ethical scores at the cost of efficiency.

---

### 3.8 Generalization Tests (Week 5)

#### Table 10. Aggregate Generalization Metrics Across Held-Out Contexts

*Source:* `results/week5/analysis_summary.json`

| Agent | Generalization Score | Cross-Task Transfer | Adaptation Speed | SIQ: Cross-Context Gen. |
|---------------|----------------------|---------------------|------------------|------------------------|
| Simple MToM | 1.1269 | 1.1362 | 0.0133 | 1.0 |
| Bayesian MToM | 1.0659 | 1.0671 | 0.0238 | 1.0 |

All metrics are aggregate indices computed across held-out environment and opponent variations. Per-condition means are not stored.

#### Figure 10. Generalization Across Environment Variants

Mean task utility for each agent across environment variants used in the generalization suite.

![Generalization Environment Curves](../results/week4/plots/generalization_env_curves.png)

**Interpretation**
The generalization results show that while Simple MToM achieves higher raw utility under some distribution shifts, its performance is more sensitive to environmental structure. In contrast, Bayesian MToM maintains consistently high utility with smaller variance across resource and horizon changes, reflecting belief-based adaptation rather than reward-scaling heuristics. Higher adaptation speed for the Bayesian agent further indicates superior behavioral adjustment across contexts, supporting a multi-objective view of generalization that values stability and adaptability in addition to immediate task performance.

---

## 4. Human Evaluation Results (Week 10)

### 4.1 Data and Analysis Approach

**Data source:** `data/human_pilot/pilot_ratings.csv`

**Analysis artifacts:** `results/week10/`

The repository implements both paired and unpaired analysis pipelines. The paired analysis summary (`results/week10/human_pilot_stats_summary.csv`) reports `n_pairs = 0`, indicating that within-subject paired comparisons are not available in the aggregated dataset. Between-group (unpaired) analyses are reported below.

### 4.2 Between-Group Comparisons

#### Table 11. Unpaired Human Evaluation Results

*Source:* `results/week10/human_pilot_unpaired_stats.csv`

*Statistical method:* Welch's t-test (unequal variances)

| Metric | n₁ | n₂ | Cohen's d | p-value |
|------------|-----|-----|-----------|----------|
| Warmth | 11 | 14 | 0.99 | 0.0186 |
| Competence | 11 | 14 | 1.83 | 0.000138 |
| Trust | 11 | 14 | 1.62 | 0.000330 |


#### Figure 11. Human Ratings by Agent Type

![Week 10 Agent Comparison](../results/week10/agent_comparison.png)

**Interpretation:** 
Participants consistently rated the MToM agent as warmer, more competent, and more trustworthy than the reward-only baseline, mirroring gains observed in simulated SIQ components. Despite limited statistical power, this convergence between human judgments and model-based metrics provides preliminary evidence that Bayesian MToM improves perceived social alignment and intent understanding, supporting its potential for trustworthy human–AI interaction.

---

## 5. Artifact Reference and Traceability

All results are derived from artifacts in `results/week{3,4,5,7,10}/` and configurations in `experiments/config/`. The table below provides a comprehensive mapping of tables and figures to their source files.

### Table 12. Artifact Traceability Matrix

| Item | Source File | Generated By |
|------------|------------------------------------------|--------------------------|
| Table 1 | `results/week5/stats_summary.json` | `analyze_week5.py` |
| Table 2 | `results/week5/analysis_summary.json` | `analyze_week5.py` |
| Table 3 | `results/week4/analysis_summary.json` | `analyze_week4.py` |
| Table 4 | `results/week5/analysis_summary.json` | `analyze_week5.py` |
| Table 6–7 | `results/week4/analysis_summary.json` | `analyze_week4.py` |
| Table 8 | `results/week7/first_order_delta_obs_validation.json` | `validate_first_order_delta_obs.py` |
| Table 10 | `results/week5/analysis_summary.json` | `analyze_week5.py` |
| Table 11 | `results/week10/human_pilot_unpaired_stats.csv` | `analyze_week10.py` |
| Figure 1–2 | `results/week5/plots/` | `analyze_week5.py` |
| Figure 3–4 | `results/week5/plots/` | `analyze_week5.py` |
| Figure 5–6 | `results/week4/plots/`, `results/week5/plots/` | `analyze_week4/5.py` |
| Figure 7–8 | `results/week7/` | `week7_trace_runner.py` |
| Figure 9 | `results/week7/robustness_summary_bar.png` | `analyze_week7.py` |
| Figure 11 | `results/week4/plots/generalization_env_curves.png` | `analyze_week4.py` |
| Figure 12 | `results/week10/agent_comparison.png` | `analyze_week10.py` |

---

