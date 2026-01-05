# Theoretical Foundations: Machine Theory of Mind (MToM)

This document summarizes the theoretical foundations underlying the Machine Theory of Mind (MToM) framework. The goal is not to provide formal guarantees for the implemented system, but to justify architectural design choices, clarify assumptions, and motivate empirical analyses.

**Important:** All theoretical results are stated for idealized abstractions of the system and are used to guide interpretation of experimental behavior.

---

## 1. Social Intelligence as Belief-Conditioned Decision-Making

We formalize social intelligence as the capacity of an agent to reason about how its actions are perceived by others, and to incorporate these inferred perceptions into decision-making.

**Let:**
- **s_t** denote the observed environment state
- **a_t ∈ A(s_t)** denote a feasible action
- **h_t** denote a latent social-perception state (e.g., perceived warmth and competence)

The agent does not observe h_t directly. Instead, it maintains a belief distribution over possible values of h_t, updated through interaction.

**Key Principle:** Socially intelligent behavior emerges when action selection is conditioned on beliefs about social perception, rather than optimized solely for task reward.

---

## 2. Bayesian Modeling of Social Perception

### 2.1 Latent Mental-State Representation

We model social perception as a latent variable **h** describing how the agent is interpreted along socially meaningful dimensions. In the implemented system, h is continuous (warmth and competence), but for theoretical analysis we consider a finite hypothesis space:

```
H = {h₁, ..., h_m}
```

This abstraction allows the application of standard Bayesian consistency results while remaining conceptually compatible with continuous belief representations.

### 2.2 Bayesian Belief Updating

Given a sequence of observations O₁:t (e.g., offers, accept/reject outcomes, or social feedback), the agent maintains a posterior:

```
P(h | O₁:t) ∝ P(O_t | h) · P(h | O₁:t₋₁)
```

**Interpretation:** This belief update represents social inference—the agent revises its expectations about how it is perceived based on observed reactions.

### 2.3 Idealized Bayesian Consistency

**Proposition 1 (Posterior Concentration)**

**Assume:**
1. The hypothesis space H is identifiable (distinct hypotheses induce distinct observation likelihoods)
2. All likelihoods assign positive probability to feasible observations
3. The prior has full support on H
4. Observations satisfy standard regularity conditions (e.g., i.i.d. or ergodic)

**Then,** if h* is the true data-generating hypothesis:

```
lim_(t→∞) P(h* | O₁:t) = 1  almost surely
```

**Interpretation:** Under idealized assumptions, Bayesian social belief tracking converges to the correct region of the social-perception space over repeated interaction.

**Scope:** This result applies to an idealized discrete model with correctly specified likelihoods. The implemented system uses continuous beliefs and predictive updates, so this proposition is used as **motivation**, not as a formal guarantee.

---

## 3. Social Intelligence as Multi-Objective Optimization

### 3.1 Task and Social Objectives

**Let:**
- **R(π) = E_π[R_task]** denote expected task reward
- **S(π) = E_π[S_social]** denote expected social utility

The agent faces a multi-objective decision problem, trading off instrumental performance and social alignment.

### 3.2 Scalarization and Pareto Optimality

In an idealized setting where the set of achievable outcome pairs (R(π), S(π)) is convex:

**Proposition 2 (Scalarization Sufficiency)**

For any Pareto-optimal policy π*, there exists λ ≥ 0 such that:

```
π* ∈ argmax_π [R(π) + λS(π)]
```

Conversely, any maximizer of the scalarized objective corresponds to a Pareto-optimal solution.

**Interpretation:** A single trade-off parameter λ is sufficient to trace the supported Pareto frontier between task performance and social alignment.

**Relation to Implementation:** The implemented MToM agent does not optimize a global objective. Instead, it performs local, per-action evaluations using an analogous scalarized utility. This proposition motivates the use of λ as an interpretable control parameter.

---

## 4. First-Order Effects of Social Weighting

To analyze the introduction of social reasoning, we consider an entropy-regularized surrogate objective:

```
J_λ(π) = E_π[R_task] + λE_π[Δ_obs] - τ·KL(π || π_ref)
```

**Where:**
- **Δ_obs(a)** denotes predicted social impact
- **τ** is a temperature parameter

### 4.1 First-Order Social Utility Gain

**Theorem 1 (First-Order Improvement)**

Under standard differentiability and interior-optimum assumptions, and assuming at least one action exhibits above-average predicted social impact:

```
S(π_λ) ≥ S(π_0) + (λ/τ)·Var_{a~π_0}[Δ_obs(a)] - O(λ²)  for small λ > 0
```

**Interpretation:** Introducing a small social weighting yields a linear improvement in social performance, proportional to the variance of predicted observer responses.

**Empirical Relevance:** This result motivates the λ micro-sweep experiments, which empirically validate the predicted linear regime for small λ.

---

## 5. Separation of Belief Updating and Action Selection

A key architectural commitment of MToM is the separation between belief updating and action selection:

- **Belief updates** encode social learning
- **Action selection** applies a fixed, transparent decision rule

**This separation enables:**
- Interpretability of social inference
- Controlled trade-off analysis
- Ablation of belief uncertainty independently of policy learning

From a theoretical perspective, this design isolates the contribution of social inference dynamics from confounding effects introduced by adaptive policies.

---

## 6. Social Intelligence Quotient (SIQ) as an Evaluation Mapping

The Social Intelligence Quotient (SIQ) is a **diagnostic metric**, not a training objective.

Formally, SIQ is a mapping:

```
SIQ: {interaction traces} → [0, 1]
```

**Decomposed into:**
- Social alignment
- Theory-of-Mind accuracy
- Cross-context generalization
- Ethical consistency

This design avoids reward hacking and preserves SIQ as an interpretive lens rather than a control signal.

---

## 7. Theory–Implementation Gap

Theoretical results in this framework serve three purposes:

1. **Justification** of Bayesian belief tracking for social inference
2. **Interpretation** of empirical trade-offs induced by λ
3. **Prediction** of qualitative trends (e.g., small-λ behavior)

They do **not** constitute formal guarantees for the implemented system, which includes:

- Greedy per-step decisions
- Uncertainty penalties
- Predictive belief updates under partial observability

**Empirical validation is therefore essential and explicitly reported.**

---

## 8. Summary

The theoretical framework underlying MToM supports the view that:

1. Social intelligence is fundamentally **belief-conditioned decision-making**
2. Bayesian inference provides a **principled mechanism** for modeling social perception
3. Scalarized objectives **expose interpretable trade-offs** rather than hiding them
4. Modest social weighting yields **predictable first-order gains**
5. Evaluation should remain **diagnostic rather than prescriptive**

Together, these principles motivate the MToM architecture as a transparent, analyzable, and human-aligned approach to social reasoning in artificial agents.