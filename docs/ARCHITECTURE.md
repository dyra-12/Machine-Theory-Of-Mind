# System Architecture: Bayesian Machine Theory of Mind (MToM)

## 1. Overview

This document describes the system architecture of the proposed Bayesian Machine Theory of Mind (MToM) agent. The architecture is designed to support explicit reasoning about human belief formation, while maintaining task effectiveness, interpretability, and robustness.

At a high level, the agent integrates:

- a task-oriented decision core,
- a Bayesian Theory-of-Mind (ToM) inference module,
- culturally and contextually informed social-norm priors,
- an ethical-constraint handler,
- and an external evaluation layer computing the Social Intelligence Quotient (SIQ).

Information flows bidirectionally between these components, enabling belief-driven decision-making rather than purely reactive or reward-only behavior.

## 2. High-Level Architecture

The system consists of the following principal modules:

1. **Environment**
2. **RL Core / Policy Optimizer**
3. **Bayesian Theory-of-Mind Module**
4. **Social-Norm Priors**
5. **Ethical-Constraint Handler**
6. **Social Intelligence Quotient (SIQ) Evaluator**

The architecture is intentionally modular to support:

- interpretability,
- ablation analysis,
- controlled experimentation,
- and future extension to clinical or real-world interaction settings.

## 3. Component Descriptions

### 3.1 Environment

The environment represents the external interaction context, including:

- the task structure (e.g., negotiation),
- other agents or human observers,
- observable outcomes and feedback.

The environment emits:

- state information relevant for task execution,
- social feedback signals reflecting how actions are perceived (e.g., warmth and competence changes).

The environment does not contain any social reasoning; it serves as the source of observations and constraints.

### 3.2 RL Core / Policy Optimizer

The RL Core is responsible for action selection. It optimizes a scalarized objective combining:

- task reward, and
- expected social utility informed by the ToM module.

**Key characteristics:**

- The policy does not learn social behavior implicitly.
- Instead, it consumes inferred beliefs produced by the Bayesian ToM module.
- Decision-making is explicit, transparent, and analyzable.

The RL Core interacts bidirectionally with:

- the Bayesian ToM module (belief-conditioned decisions),
- the Ethical-Constraint Handler (feasible action filtering).

### 3.3 Bayesian Theory-of-Mind (ToM) Module

The Bayesian ToM module is the cognitive core of the system.

**Its responsibilities are to:**

- maintain a belief distribution over latent human mental states,
- update beliefs using Bayesian inference based on observed feedback,
- predict how candidate actions will be perceived by human observers.

Mental states are defined over interpretable dimensions such as:

- warmth,
- competence,
- and derived social scores.

Beliefs are represented probabilistically, enabling:

- uncertainty awareness,
- gradual adaptation,
- and explainable reasoning trajectories.

The ToM module provides expected perception outcomes to the RL Core, influencing action selection.

### 3.4 Social-Norm Priors

Social-Norm Priors encode contextual and cultural expectations about social behavior.

**These priors:**

- regularize Bayesian belief updates,
- stabilize inference under noisy or adversarial feedback,
- capture differences in social norms across environments.

They influence:

- initial belief distributions,
- belief-update dynamics,
- and sensitivity to perceived deviations.

Importantly, priors are configurable and explicit, allowing controlled experimentation and cross-context generalization analysis.

### 3.5 Ethical-Constraint Handler

The Ethical-Constraint Handler enforces hard and soft constraints on decision-making.

**Its role is to:**

- prevent actions violating minimum fairness or safety criteria,
- bias decisions toward ethically acceptable regions of the action space,
- maintain consistency with normative assumptions.

Ethical constraints operate before or during policy evaluation, ensuring that optimization does not exploit socially undesirable strategies even if they yield higher task reward.

This separation allows ethical reasoning to remain transparent and auditable.

### 3.6 Social Intelligence Quotient (SIQ) Evaluator

The SIQ Evaluator is an external assessment module, not part of the agent's internal optimization loop.

**It computes a composite score capturing:**

- social alignment,
- Theory-of-Mind accuracy,
- cross-context generalization,
- ethical consistency.

**SIQ serves three roles:**

1. Evaluation metric for experiments,
2. Comparative benchmark across agents,
3. Interpretability aid linking behavior to social outcomes.

By design, SIQ is not directly optimized, preventing metric overfitting and preserving scientific validity.

## 4. Information Flow

A single interaction cycle proceeds as follows:

1. The environment provides the current task state.
2. The Bayesian ToM module maintains and updates beliefs based on prior observations.
3. For each candidate action:
   - the ToM module predicts perceived social impact,
   - the Ethical-Constraint Handler filters or penalizes infeasible actions.
4. The RL Core selects an action maximizing expected task + social utility.
5. The environment executes the action and emits observable outcomes.
6. The ToM module updates beliefs using Bayesian inference.
7. SIQ is computed offline from logged interaction traces.

This closed belief–action–observation loop enables rational social adaptation rather than imitation.

## 5. Design Rationale

The architecture is intentionally designed to satisfy the following principles:

- **Explicitness:** Social reasoning is represented, not hidden in weights.
- **Interpretability:** Beliefs and decisions can be inspected and explained.
- **Modularity:** Components can be ablated or replaced independently.
- **Robustness:** Bayesian inference and priors mitigate noise and deception.
- **Scientific Testability:** Each module corresponds to a testable hypothesis.

This distinguishes MToM from purely neural, end-to-end, or reward-shaping approaches.

## 6. Scope and Limitations

The architecture assumes:

- finite or low-dimensional mental-state spaces,
- short to medium interaction horizons,
- partial but informative social feedback.

It is not intended as:

- a model of full human psychology,
- a clinical diagnostic system,
- or a replacement for human judgment.

These constraints are appropriate for a proof-of-concept framework.

## 7. Relation to the Paper

This architecture corresponds directly to:

- Figure 1 in the paper,
- the formal model in the Theory section,
- and the experimental analyses of belief updates, robustness, and SIQ.

Implementation details are documented separately and do not affect the conceptual structure described here.

---

## Summary

The Bayesian MToM architecture integrates belief inference, normative reasoning, and task optimization into a single, interpretable system. By modeling how humans form beliefs—rather than merely imitating social behavior—the framework enables principled social intelligence, empirical evaluation, and a foundation for future human-centered AI and computational psychiatry research.
