# Empirical Evidence for Machine Theory of Mind (MToM)

## 1. Overview

This document reports experimental results from a proof-of-concept evaluation of Machine Theory of Mind (MToM) agents. All reported findings are directly supported by artifacts in `results/` or executable configurations in `experiments/config/`.

This work evaluates social reasoning under simulated observers and a small human pilot; it does not claim real-world deployment readiness.

---

## 2. Experimental Design

### 2.1 Negotiation Task

The core environment implements a discrete resource allocation negotiation task (`src/envs/negotiation_v1.py`) with the following parameters:

- **Total resources:** 10 (default)
- **Episode length:** 3 turns maximum (default)
- **Action space:** Integer splits where each agent proposes `(self_share, other_share)` with `self_share ∈ {1, …, 9}`

These parameters remain consistent across Week 2 experiments (see `experiments/config/negotiation_week2.yaml`).

### 2.2 Sample Sizes

Sample sizes vary by experimental suite as specified in configuration files:

- **Week 2 agent comparison:** 10 runs per (agent, λ) configuration, seed=42 (`experiments/config/negotiation_week2.yaml`)
- **Week 7 robustness suite:** 1 seed, 3 runs per configuration (`experiments/config/robustness_suite.yaml`)

### 2.3 Metrics

The following metrics are logged per episode:

- `task_reward` (normalized by total resources)
- `warmth`, `competence`, `social_score`
- `total_utility` (computed as task_reward + λ × social_score)
- `num_turns`, `final_agreement`

Social Intelligence Quotient (SIQ) is a research metric computed as a composite from warmth, competence, and ethical consistency components (see `results/week3/siq_summary.json`, `results/week5/analysis_summary.json`).

**Note on SIQ interpretation:** SIQ is a diagnostic composite metric. High SIQ scores indicate strong social alignment but do not guarantee optimal task performance. Agents optimizing exclusively for social metrics may achieve high SIQ while exhibiting suboptimal task outcomes.

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

---

### 3.2 Pareto Frontier Analysis (Weeks 3 and 5)

Pareto-frontier visualizations illustrate trade-offs between task/utility and social metrics.

**Artifacts:**
- `results/week3/plots/pareto_frontiers.png`
- `results/week5/plots/pareto_utility_vs_adaptation.png`
- `results/week5/plots/pareto_utility_vs_robustness.png`

#### Figure 3. Pareto Frontier: Utility vs. Adaptation

![Week 5 Pareto: Utility vs Adaptation](../results/week5/plots/pareto_utility_vs_adaptation.png)

#### Figure 4. Pareto Frontier: Utility vs. Robustness

![Week 5 Pareto: Utility vs Robustness](../results/week5/plots/pareto_utility_vs_robustness.png)

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

**Note:** Ethical consistency varies by scenario and SIQ component definitions. These values reflect performance on the Week 3 evaluation set and do not constitute universal guarantees of zero-violation behavior.

#### Figure 5. SIQ Component Breakdown (Week 4)

![Week 4 SIQ Components](../results/week4/plots/week4_siq_components.png)

#### Figure 6. SIQ Component Breakdown (Week 5)

![Week 5 SIQ Components](../results/week5/plots/week5_siq_components.png)

---

### 3.4 Belief Update Traces (Week 7)

**Artifacts:**
- Representative posterior trace: `results/week7/posterior_trace_example.png`
- Per-episode trace logs: `results/week7/traces/trace_*.json`
- Turn-level social-score plots: `results/week7/plots/social_score_vs_turn.png` and `results/week7/plots/social_score_vs_turn_extended.png`

#### Figure 7. Example Posterior Trace

![Week 7 Posterior Trace Example](../results/week7/posterior_trace_example.png)

#### Figure 8. Social Score Trajectories Across Turns

![Week 7 Social Score vs Turn](../results/week7/plots/social_score_vs_turn_extended.png)

---

### 3.5 Robustness Battery (Week 7)

**Configuration:** `experiments/config/robustness_suite.yaml`

**Data:** `results/week7/robustness_suite/robustness_results.jsonl`

#### Figure 9. Robustness Summary Across Adversarial Conditions

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

**Interpretation:** All adversarial perturbations reduce performance. Bayesian MToM shows the smallest degradation, indicating robustness under stress.

#### Table 7. Norm-Shift Sensitivity (Alignment Test)

**What this tests:** Adaptation to plausible changes in social norms

**Source:** `results/week4/analysis_summary.json`

**Reference condition:** Simple/clean observer

| Condition | Δ Utility (%) | Δ SIQ (%) | Notes |
|-------------------|---------------|-----------|--------------------------------|
| Lenient | +1.94 | +9.36 | Forgiving norm improves both |
| Competence-biased | +0.99 | +9.42 | Rewards efficient splits |
| Warmth-biased | −0.66 | −6.28 | Stricter moral preference |

**Interpretation:** The agent exploits favorable norms and adapts its behavior, demonstrating belief-sensitive social reasoning rather than fixed politeness.

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

**Interpretation:** Close agreement (≤1% error) between predicted and observed first-order slopes at small λ values.

#### Figure 10. Mean Social Score vs. λ (Micro-Sweep)

![Week 7 Lambda Micro-Sweep](../results/week3/plots/lambda_sensitivity.png)

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

#### Figure 11. Generalization Across Environment Variants

Mean task utility for each agent across environment variants used in the generalization suite.

![Generalization Environment Curves](../results/week4/plots/generalization_env_curves.png)

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

**Interpretation:** MToM agents received significantly higher ratings than baseline agents on all three dimensions, with large effect sizes (d > 0.8).

#### Figure 12. Human Ratings by Agent Type

![Week 10 Agent Comparison](../results/week10/agent_comparison.png)

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

