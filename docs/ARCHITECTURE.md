# Bayesian Machine Theory of Mind (MToM) Architecture

This document describes the architecture of the Bayesian Machine Theory of Mind (MToM) framework for socially intelligent decision-making. The goal of the architecture is to make social reasoning **explicit, interpretable, and controllable**, rather than implicit in learned policies or reward shaping.

The system is designed to separate belief-based social inference from action selection, enabling fine-grained analysis of how perceived intent, uncertainty, and normative expectations influence agent behavior.

---

## 1. High-Level Overview

At a high level, the MToM agent operates as a **belief-conditioned decision system**. Rather than learning a parametric policy, the agent:

- Maintains probabilistic beliefs about how its behavior is socially perceived
- Predicts the social impact of candidate actions
- Trades off task performance and social alignment using an explicit control parameter

The core design principle is **modularity**: social inference, task evaluation, and decision-making are distinct components with well-defined interfaces.

```
Environment State + Social Feedback
              ↓
      Bayesian ToM Module
              ↓
   Belief over Social Perception
              ↓
   Social Scoring & Normative Mapping
              ↓
   Task Utility Evaluation
              ↓
  Risk-Adjusted Action Selection
              ↓
         Selected Action
```

---

## 2. Core Architectural Components

### 2.1 Task Utility Evaluator

**Purpose:** Quantifies instrumental task performance independently of social considerations.

**Inputs:**
- Current environment state
- Candidate action (e.g., proposed resource split)

**Output:**
- Scalar task utility: r_task(a)

**Design Choice:** Task utility is intentionally simple and transparent (e.g., normalized self-reward). No opponent modeling or acceptance prediction is embedded here.

**Rationale:** This isolates instrumental competence from social reasoning, avoiding confounding effects where "social behavior" is implicitly baked into task rewards.

---

### 2.2 Bayesian Theory-of-Mind (ToM) Module

**Purpose:** Maintains and updates probabilistic beliefs over how the agent is perceived by observers.

**Latent State:** Continuous belief distribution over social perception dimensions:
- **Warmth** (intent, cooperativeness)
- **Competence** (capability, efficiency)

**Inputs:**
- Observed social feedback (when available)
- Predicted social outcomes (when feedback is delayed or partial)
- Channel reliability estimates (for noisy or adversarial observers)

**Update Mechanism:**
- Bayesian belief updating with uncertainty propagation
- Supports provisional (anticipatory) updates under partial observability

**Key Properties:**
- Represents graded social perception, not discrete "types"
- Explicitly models epistemic uncertainty
- Enables belief convergence and cautious updating under noise

**Rationale:** Unlike heuristic or neural ToM approaches, this module makes social inference inspectable and analyzable, enabling robustness and theoretical grounding.

---

### 2.3 Social Scoring and Normative Evaluation

**Purpose:** Maps predicted social perception changes into a scalar social utility.

**Inputs:**
- Predicted change in warmth and competence
- Normative preference weights (e.g., warmth-biased vs competence-biased observers)

**Output:**
- Scalar social utility: s_social(a)

**Important Design Decision:** Ethical or fairness constraints are not enforced as hard constraints during action selection. Normative behavior is evaluated post hoc via diagnostic metrics.

**Rationale:** This avoids collapsing social intelligence into rigid rule-following and allows the system to:
- Expose ethical trade-offs
- Analyze over-socialization
- Maintain full action-space transparency

---

### 2.4 Risk-Aware Action Selection

**Purpose:** Selects actions by trading off task utility and social utility under uncertainty.

**Decision Rule (Conceptual):**
```
u(a) ≈ r_task(a) + λ · s_social(a)
```

**Implementation Details:**
- Utility estimates are uncertainty-aware
- High-variance social predictions are penalized
- Optional turn-dependent or scheduled λ

**Control Parameter:**
- λ ≥ 0: explicit task–social trade-off knob

**Key Property:** No policy parameters are learned online. Behavioral adaptation emerges solely through belief updates.

**Rationale:** This cleanly separates learning to reason socially from learning a policy, enabling interpretable trade-off analysis and theoretical validation.

---

## 3. Interaction and Decision Loop

At each timestep:

1. Observe environment state and prior social feedback
2. Update social beliefs via Bayesian inference
3. Enumerate feasible actions
4. For each action:
   - Compute task utility
   - Predict social impact
   - Estimate uncertainty-adjusted combined utility
5. Select the action maximizing risk-adjusted utility
6. Execute action and log outcomes

This loop enables adaptive social behavior without opaque policy learning.

---

## 4. Evaluation Architecture (SIQ as a Diagnostic Layer)

The **Social Intelligence Quotient (SIQ)** is not part of the decision loop. Instead, it operates as an evaluation-only layer computed from interaction traces.

**SIQ Components:**
- Social alignment
- Theory-of-Mind accuracy
- Cross-context generalization
- Ethical consistency

**Design Principle:** SIQ is non-differentiable and not optimized. Used for diagnosis, comparison, and ablation analysis.

This separation prevents metric gaming and preserves interpretability.

---

## 5. Idealized vs Implemented Architecture

| Aspect | Idealized Analysis | Implemented System |
|--------|-------------------|-------------------|
| **Objective** | Global scalarized optimization | Local per-action evaluation |
| **Beliefs** | Discrete hypotheses (theory) | Continuous distributions |
| **Updates** | Fully observed Bayesian updates | Partial + predictive updates |
| **Guarantees** | Asymptotic consistency | Empirically validated trends |

Theoretical results motivate design choices but are not claimed as formal guarantees of the full system.

---

## 6. Design Philosophy Summary

The MToM architecture is built around four commitments:

1. **Explicit social inference** over implicit reward shaping
2. **Belief uncertainty** as a first-class signal
3. **Transparent trade-offs** rather than hidden objectives
4. **Evaluation as diagnosis**, not optimization

This makes the framework suitable for:

- Human-centered AI
- Socially aligned decision systems
- Interpretable agent design
- Computational social modeling