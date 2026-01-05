# Machine Theory of Mind

## Socially-Aligned AI via Bayesian Mental-State Reasoning

---

*A research framework for endowing artificial agents with computational Theory of Mind through explicit, belief-based social reasoning.*

---

## Abstract

Human social intelligence relies on Theory of Mind (ToM)—the capacity to reason about others' mental states, intentions, and beliefs. This repository presents Machine Theory of Mind (MToM), a methodological framework for modeling social cognition in artificial agents using Bayesian inference over latent social perceptions.

MToM agents maintain probabilistic beliefs over perceived warmth and competence, predict how candidate actions will be socially interpreted, and select actions by trading off task performance and social alignment via an explicit, interpretable control parameter. Social intelligence is evaluated post hoc using a diagnostic metric, the Social Intelligence Quotient (SIQ).

The framework is evaluated through controlled simulations, robustness analyses, and a small human-in-the-loop pilot study (N=25), demonstrating that explicit belief-based social reasoning yields more interpretable and human-perceived socially intelligent behavior than reward-only baselines.

This project is intended as a proof-of-concept research contribution at the intersection of probabilistic AI, cognitive modeling, and human-centered AI.

---

## How to Read This Repository

**Start here for a conceptual overview**, then explore:

- [`ARCHITECTURE.md`](ARCHITECTURE.md) — System design and data flow
- [`theory.md`](theory.md) — Formal assumptions, idealized results, and theoretical motivation
- [`EXPERIMENTS.md`](EXPERIMENTS.md) — Experimental protocols and evaluation setup
- [`Results.md`](Results.md) — Figure-by-figure interpretation of empirical findings
- [`../ETHICS.md`](../ETHICS.md) — Research ethics, responsible use, and scope

---

## Core Idea

**Most AI systems optimize *what to do*.**  
**MToM explicitly models *how actions are perceived*.**

At each decision step, an MToM agent:

1. **Maintains probabilistic beliefs** over perceived social attributes (e.g., warmth, competence)
2. **Predicts the social impact** of candidate actions
3. **Trades off task utility and social alignment** using an explicit parameter λ
4. **Adapts behavior** through belief updates, not policy learning

This separation makes social reasoning:

- **Inspectable**
- **Adjustable**
- **Diagnosable**
- **Resistant to reward hacking**

---

## System Architecture

The MToM agent is a belief-conditioned decision system composed of:

### 1. Bayesian Theory-of-Mind Module
Tracks probabilistic beliefs over perceived warmth and competence under uncertainty.

### 2. Task Utility Evaluator
Computes instrumental task reward independently of social considerations.

### 3. Social Scoring Module
Estimates predicted social perception changes for candidate actions.

### 4. Risk-Adjusted Action Selection
Combines task and social utilities via an explicit trade-off parameter λ, with uncertainty penalties.

**Key properties:**
- No parametric policy is learned
- No social metric is optimized directly
- Behavioral adaptation arises solely from belief updates

See [`ARCHITECTURE.md`](ARCHITECTURE.md) for details.

---

## Social Intelligence Quotient (SIQ)

To evaluate social intelligence without optimizing it, we introduce the **Social Intelligence Quotient (SIQ)** — a diagnostic evaluation metric computed post hoc from interaction traces.

SIQ decomposes social intelligence into:

- **Social alignment**
- **Theory-of-Mind accuracy**
- **Cross-context generalization**
- **Ethical consistency**

**SIQ is not part of the decision loop and is used strictly for analysis and comparison.**

See [`theory.md`](theory.md) for formal definitions.

---

## Experiments and Evaluation

MToM is evaluated through:

### Simulation Studies

- Two-agent negotiation environments
- Explicit sweeps over the task–social trade-off parameter λ
- Robustness tests under noisy, adversarial, and norm-shifted observers
- Ablations isolating belief modeling and uncertainty

### Human-in-the-Loop Pilot

- N = 25 adult participants
- Short, text-based negotiation dialogues
- 7-point Likert ratings for Warmth, Competence, and Trust
- **Finding**: MToM agents rated higher than reward-only baselines across all dimensions

Experimental protocols are described in [`EXPERIMENTS.md`](EXPERIMENTS.md), with results summarized in [`Results.md`](Results.md).

---

## Theoretical Foundations

The framework is grounded in:

- Bayesian inference for latent social belief tracking
- Multi-objective optimization and Pareto analysis
- First-order analysis of social weighting effects
- Explicit separation between theory and implementation

**Important**: All theoretical results apply to idealized abstractions and are used to motivate design choices and empirical trends, not as guarantees of deployed behavior.

See [`theory.md`](theory.md) for formal treatment.

---

## Ethics, Responsibility, and Scope

This repository presents **non-clinical, minimal-risk research**.

- Human evaluation concerns perceptions of artificial agents, not participants
- No personally identifiable or sensitive data are collected
- No clinical, diagnostic, or deployment claims are made
- Ethical consistency is evaluated diagnostically, not enforced

See [`../ETHICS.md`](../ETHICS.md) for detailed discussion.

---

## Repository Structure

```
├── README.md
├── docs/
│   ├── ARCHITECTURE.md
│   ├── theory.md
│   ├── EXPERIMENTS.md
│   ├── Results.md
│   ├── REPRODUIBILITY.md
│   └── figures/
├── ETHICS.md
├── CODE_OF_CONDUCT.md
├── CONTRIBUTING.md
├── CITATION.cff
├── src/
├── experiments/
├── results/
└── tests/
```

---

## Reproducibility

- YAML-based experiment configurations
- Controlled random seeds
- Offline computation of SIQ
- Logged interaction traces for auditability

See [`REPRODUIBILITY.md`](REPRODUIBILITY.md) for step-by-step instructions.

---

## Intended Use

**Intended for:**

- Research in human-centered and socially aligned AI
- Methodological exploration of belief-based decision systems
- Reproducible experimentation and analysis

**Not intended for:**

- Real-world deployment without extensive validation
- Manipulative or deceptive applications
- High-stakes negotiation or decision-making

---

## Citation

If you use or build on this work, please cite it as described in [`../CITATION.cff`](../CITATION.cff).

---

## Summary

Machine Theory of Mind (MToM) demonstrates that explicit, probabilistic modeling of social perception enables artificial agents to behave in ways that are more socially aligned, interpretable, and meaningful to human observers.

Rather than treating social behavior as an implicit side effect of optimization, MToM reframes it as belief-conditioned decision-making, providing a transparent foundation for future research in socially intelligent AI systems.

---

**Last Updated**: December 2025  
**Repository Status**: Active research development | Preparing for preprint submission
