# Experimental Design for Bayesian Machine Theory of Mind (MToM)

This document describes the experimental design used to evaluate the Bayesian Machine Theory of Mind (MToM) framework. The experiments are designed to assess whether explicit belief-based social reasoning improves social alignment, robustness, and interpretability, and to characterize trade-offs between task performance and social intelligence.

---

## 1. Experimental Goals

The experiments address four core questions:

1. Does belief-based social reasoning improve social intelligence relative to non-social and heuristic baselines?
2. How does the task–social trade-off parameter (λ) shape behavior and performance?
3. Does Bayesian belief modeling improve robustness and adaptation under uncertainty and norm shifts?
4. Do simulated social intelligence gains translate into human-perceived warmth, competence, and trust?

**Important:** No experiment optimizes for the Social Intelligence Quotient (SIQ). All social metrics are computed post hoc for evaluation and diagnosis.

---

## 2. Environment

### 2.1 Negotiation Task

All experiments are conducted in a controlled two-agent negotiation environment:

- **Total divisible resources:** R (default: 10)
- **Maximum turns per episode:** T (default: 3)
- **Agents alternate proposer roles**
- **Episodes terminate upon agreement or timeout**

### 2.2 Action Space

An action corresponds to a proposed resource split:

```
(x₀, x₁) such that x₀ + x₁ = R
```

To avoid degenerate solutions, agents enumerate all valid splits allocating at least one unit to each agent.

### 2.3 Rewards and Termination

**If an agreement is reached:**
```
rᵢ = xᵢ / R
```

**If no agreement is reached:** reward = 0

- No shaping rewards or auxiliary penalties are used

### 2.4 Acceptance Model

For simulation-based experiments, accept/reject behavior is modeled stochastically using a fixed acceptance function that increases with the receiver's share. This ensures controlled comparability across agent types.

---

## 3. Agent Configurations

### 3.1 Baselines

The following baselines establish performance and social reasoning controls:

- **Greedy baseline:** maximizes self-share only
- **Random baseline:** uniformly samples valid splits
- **Social baseline:** maximizes observer-derived social score using a fixed heuristic mental state

### 3.2 MToM Agents

**Simple MToM:**
- Uses a point-estimate social belief and linear task–social scalarization

**Bayesian MToM:**
- Maintains probabilistic beliefs over perceived warmth and competence
- Estimates expected utility via Monte Carlo sampling
- Applies uncertainty-aware, risk-adjusted action selection

**Note:** No agent learns a policy online. Behavioral adaptation arises solely from belief updates.

---

## 4. Observer Models

Observers evaluate agent actions along two dimensions:

- **Warmth** (intent, cooperativeness)
- **Competence** (capability, efficiency)

### Observer Profiles

Multiple observer profiles are used to test robustness:

- Lenient (forgiving)
- Harsh (punitive)
- Warmth-biased
- Competence-biased
- Adversarial (noisy, inverted, or dropped signals)

Bayesian agents receive both social feedback and a channel reliability estimate, enabling uncertainty-aware belief updates.

---

## 5. Evaluation Metrics

### 5.1 Task Performance

- Mean task reward per episode
- Mean total utility (task + social)

### 5.2 Social Intelligence Quotient (SIQ)

SIQ is a **diagnostic evaluation metric**, not an optimization objective. It decomposes social intelligence into:

- Social alignment
- Theory-of-Mind accuracy
- Cross-context generalization
- Ethical consistency

Each component is normalized to [0, 1] and aggregated post hoc from interaction logs.

---

## 6. Hyperparameter Sweeps

### 6.1 Social Trade-off Parameter (λ)

The social weighting parameter λ is swept over:

```
λ ∈ {0.0, 0.1, 0.3, 0.5, 0.7, 1.0, 1.5, 2.0, 3.0}
```

This sweep traces empirical Pareto frontiers between task performance and social alignment.

### 6.2 Bayesian Prior Strength

Bayesian prior concentration is varied to assess:

- Belief stability
- Adaptation speed
- Robustness to noise

---

## 7. Robustness Experiments

### 7.1 Adversarial Perception Channels

Agents are evaluated under:

- Noisy feedback
- Inverted social signals
- Unreliable observer channels

Performance degradation is compared relative to clean conditions.

### 7.2 Norm-Shift Sensitivity

Observer norms are systematically altered (e.g., warmth-biased vs competence-biased) to test whether agents adapt rationally to changing social expectations.

---

## 8. Ablation Studies

Controlled ablations isolate component contributions:

- **No MToM (λ = 0):** removes social reasoning
- **No Bayesian priors:** removes belief uncertainty
- **Over-socialized (λ = 2.0):** tests excessive social weighting

Each ablation is compared against the full Bayesian MToM agent.

---

## 9. Generalization Tests

Agents are evaluated on held-out environment variants:

- Smaller and larger resource pools
- Shorter and longer negotiation horizons

Generalization is assessed using:

- Mean task utility
- Adaptation speed
- SIQ cross-context stability

---

## 10. Human Evaluation

A pilot human-in-the-loop study evaluates whether simulated social reasoning translates into human perception.

**Study Design:**
- **Participants:** N = 25
- **Interface:** Gradio-based web UI
- **Ratings:** 7-point Likert scales for Warmth, Competence, Trust
- **Conditions:** MToM vs reward-only baseline
- **Analysis:** Paired tests with effect size reporting

**Note:** No demographic data are collected to preserve anonymity.

---

## 11. Statistical Analysis

- Episode-level comparisons use **Welch's t-tests**
- Effect sizes reported via **Cohen's d**
- λ-sensitivity analyzed using **one-way ANOVA**
- Pareto trade-offs summarized descriptively (frontiers, hypervolume)
- Human ratings analyzed at participant level

---

## 12. Reproducibility

- All experiments are configured via **YAML files**
- Random seeds are explicitly controlled
- Simulation sweeps are parallelized
- SIQ is computed offline from logged traces

---

## 13. Experimental Scope and Limitations

The experiments are intentionally conducted in a **stylized environment** to isolate the role of belief-based social reasoning. Results demonstrate mechanistic plausibility and structured trade-offs, not guarantees of real-world social alignment.

---

## Summary

Together, these experiments demonstrate that explicit, probabilistic social belief modeling yields agents that are more socially aligned, robust, and interpretable than reward-only or heuristic baselines, while exposing transparent trade-offs between efficiency and social intelligence.