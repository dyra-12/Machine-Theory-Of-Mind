# Machine Theory of Mind (MToM)

**Bayesian Social Reasoning for Interpretable and Aligned Human–AI Interaction**

This repository presents a proof-of-concept Machine Theory of Mind (MToM) framework that equips artificial agents with explicit models of how humans infer intentions, evaluate behavior, and update social beliefs. Rather than training agents to merely act socially, this work focuses on reasoning about social cognition itself.

## Motivation

Modern AI systems increasingly interact with humans in social settings, yet most optimize behavior without modeling how actions are perceived. This limits interpretability, robustness, and trust. Inspired by human Theory of Mind and computational psychiatry, this project asks:

> Can agents explicitly reason about human belief formation—and does this improve social alignment without sacrificing task performance?

## Core Contributions

- **Bayesian Machine Theory of Mind (MToM):**  
  An agent architecture that maintains probabilistic beliefs over latent human mental states (e.g., warmth, competence) and updates them through interaction.

- **Multi-Objective Decision Framework:**  
  Formalization of social decision-making as joint optimization of task reward and social intelligence, controlled by a social-weight parameter (λ).

- **Social Intelligence Quotient (SIQ):**  
  A composite, interpretable metric capturing social alignment, Theory-of-Mind accuracy, cross-context generalization, and ethical consistency.

- **Theoretical Guarantees:**  
  Proof sketches for Bayesian posterior concentration, Pareto-optimal scalarization, and first-order social improvement under small λ.

- **Empirical Validation:**  
  Extensive simulation studies (parameter sweeps, ablations, robustness, generalization) and a human-in-the-loop pilot study (N = 25).

## Key Results (Highlights)

- Bayesian MToM achieves the highest SIQ (0.73) among all agents tested.
- Perfect ethical consistency (100%) under fairness constraints.
- Robust performance under noisy, biased, and adversarial observers.
- **Human evaluation:**  
  MToM agents rated significantly higher in warmth, competence, and trust than baselines (Cohen's d = 0.99–1.83).

## Why This Matters

This work demonstrates that explicit belief modeling—not imitation—can yield socially aligned, interpretable AI behavior. Beyond human–AI interaction, the framework naturally connects to computational psychiatry, where deviations in belief updating and social inference are central to conditions such as psychosis.

## Status

- **Scope:** Proof of concept
- **Focus:** Interpretability, theory–experiment alignment, reproducibility
- **Not a clinical system** (no diagnostic claims)

## Documentation & Reproducibility

- 📄 **Paper:** included in this repository
- 📘 **Full documentation:** see [docs/README.md](docs/README.md)
- 🔁 **Reproducible experiments:** configuration-driven, deterministic seeds

## Intended Audience

Researchers in:

- Human–AI Interaction (HCI)
- Social and Multi-Agent AI
- Bayesian Cognitive Modeling
- Computational Psychiatry (methodological foundations)

---

For full theoretical details, experimental protocols, and reproducibility instructions, see [docs/README.md](docs/README.md).
