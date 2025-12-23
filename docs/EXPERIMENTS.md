# Experiments: Design, Execution, and Reproducibility

## 1. Purpose

This document describes the experimental design, execution protocol, and reproducibility guarantees for the Machine Theory of Mind (MToM) framework. All experiments reported in the paper are derived from the procedures documented here.

The goals of the experimental program are to:

- compare MToM agents against baseline agents,
- evaluate trade-offs between task performance and social intelligence,
- test robustness and generalization,
- and validate theoretical predictions empirically.

## 2. Experimental Environment

All experiments are conducted in a controlled negotiation environment designed to isolate social reasoning effects.

**Key properties:**

- Two-agent interaction
- Finite horizon
- Discrete action space
- Observable social feedback (warmth, competence)

Environment variants differ only in:

- total resource size,
- interaction horizon,
- or opponent behavior.

These variants are used to assess robustness and cross-context generalization, not to introduce new task mechanics.

## 3. Agent Configurations

The following agent classes are evaluated:

- **Random baseline** — stochastic action selection
- **Greedy baseline** — task reward maximization
- **Social baseline** — heuristic social optimization
- **Simple MToM** — dual-objective social + task reasoning
- **Bayesian MToM** — belief-based inference with priors
- **Learned ToM** — neural prediction of social perception

All agents operate under identical environment conditions and differ only in their internal decision-making mechanisms.

## 4. Evaluation Metrics

### 4.1 Primary Metrics

- **Task Reward:** normalized payoff from final agreement
- **Social Score:** perceived warmth and competence
- **Total Utility:** task reward + λ·social utility

### 4.2 Composite Metric

**Social Intelligence Quotient (SIQ):**

- Social alignment
- Theory-of-Mind accuracy
- Cross-context generalization
- Ethical consistency

SIQ is used exclusively for evaluation, not optimization.

## 5. Experimental Phases

### 5.1 Trade-off Exploration (Weeks 2–3)

**Purpose:**

- characterize reward–social trade-offs,
- identify Pareto-efficient regions,
- compare baseline and MToM agents.

**Method:**

- λ swept over a wide range,
- multiple random seeds per configuration,
- Pareto frontiers constructed for each agent.

### 5.2 Bayesian Hyperparameter Sweep (Week 5)

**Purpose:**

- analyze interaction between Bayesian prior strength and social weighting λ.

**Method:**

- grid search over prior strength × λ,
- aggregation across seeds,
- evaluation via SIQ and total utility.

**Outcome:**

- identification of stable performance ridge,
- avoidance of over-regularization regimes.

### 5.3 Robustness Battery (Week 6–7)

**Purpose:**

- test stability under noisy, biased, or adversarial perception.

**Conditions:**

- lenient observers
- harsh observers
- competence-biased observers
- warmth-biased observers
- adversarial observers with noise and inversion

**Metrics:**

- performance degradation
- SIQ stability
- variance across conditions

### 5.4 Generalization Tests (Week 7)

**Purpose:**

- assess transfer across unseen environments.

**Test cases:**

- new opponents
- altered resource sizes
- shorter and longer horizons
- multi-party extensions

Performance is compared relative to baseline environments.

### 5.5 Human Pilot Evaluation (Week 10)

**Purpose:**

- validate whether simulated social intelligence aligns with human perception.

**Method:**

- short dialogue evaluation,
- 7-point Likert ratings (warmth, competence, trust),
- randomized within-subject design.

This evaluation is perceptual, not behavioral or clinical.

## 6. Statistical Analysis

Analyses include:

- Welch's t-tests for agent comparisons,
- effect size estimation (Cohen's d),
- one-way ANOVA for λ sensitivity,
- Pareto dominance analysis,
- confidence interval reporting where applicable.

Significance thresholds are fixed at **α = 0.05** (two-tailed).

## 7. Reproducibility

To ensure reproducibility:

- All experiments are configuration-driven.
- Random seeds are logged and controlled.
- Results are stored in structured directories by week.
- Aggregated metrics and plots are regenerated deterministically.

Independent replication requires only:

1. cloning the repository,
2. installing dependencies,
3. executing the documented experiment runners.

No proprietary data or services are required.

## 8. Scope and Constraints

These experiments are designed as a proof of concept.

They do not claim:

- ecological completeness,
- real-world deployment readiness,
- or clinical validity.

The experimental scope is intentionally constrained to support clear causal interpretation and theoretical validation.

## 9. Relation to the Paper

This document underpins:

- the Methods section,
- the Experimental Results section,
- and the Reproducibility statement of the paper.

Figures, tables, and claims in the paper correspond directly to the experiments described here.

---

## Summary

The experimental program systematically evaluates Machine Theory of Mind agents across trade-offs, robustness, generalization, and human perception. The design prioritizes interpretability, fairness, and reproducibility, enabling rigorous comparison between belief-based social reasoning and baseline decision-making approaches.
