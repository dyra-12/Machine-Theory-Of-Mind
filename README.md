# Machine Theory of Mind (MToM)

Bayesian social reasoning for explicit, interpretable, and aligned human–AI interaction

This repository presents a proof‑of‑concept Machine Theory of Mind (MToM) framework that equips artificial agents with explicit probabilistic models of how humans infer intentions, evaluate behavior, and update social beliefs. Rather than training agents to merely act socially, this work focuses on reasoning about social cognition itself.

## Motivation

Modern AI systems increasingly interact with humans in social settings, yet most optimize behavior without modeling how actions are perceived. This limits interpretability, robustness, and trust. Inspired by human Theory of Mind and Bayesian cognitive modeling, this project asks:

> Can agents explicitly reason about human belief formation—and does this improve social alignment without sacrificing task performance?

## Core Contributions

- **Bayesian MToM:** An agent architecture that maintains probabilistic beliefs over latent human mental states (e.g., warmth, competence) and updates them through interaction.
- **Multi‑Objective Decision Framework:** Formalizes social decision‑making as joint optimization of task reward and social intelligence, controlled by a social‑weight parameter (λ).
- **Social Intelligence Quotient (SIQ):** A composite, interpretable metric capturing social alignment, Theory‑of‑Mind accuracy, cross‑context generalization, and ethical consistency.
- **Theoretical Guarantees:** Proof sketches for Bayesian posterior concentration, Pareto‑optimal scalarization, and first‑order social improvement under small λ.
- **Empirical Validation:** Simulation studies (parameter sweeps, robustness suites) and a human‑in‑the‑loop pilot study (N = 25 total; unpaired groups n=11 vs n=14 in the stored Week 10 stats artifacts).

## Key Results (Highlights)

- **SIQ (artifact-backed):** Week-specific SIQ summaries are stored under `results/` (e.g., Week 3 reports `bayesian_mtom` SIQ ≈ 0.796; see `results/week3/siq_summary.json`).
- **Ethical consistency (no “perfect” claim):** Ethical consistency varies by suite/configuration and is not universally 1.0 in the committed artifacts.
- **Robustness (explicit, small-budget suite):** Evaluated under noisy/adversarial observer channels and domain shifts with an explicit run budget (`num_seeds=1`, `runs_per_config=3`) in the Week 7 robustness suite.

### Human Evaluation

- **Perceived qualities:** In the Week 10 pilot artifacts, unpaired comparisons show higher warmth, competence, and trust for MToM than baseline dialogues.
- **Effect sizes:** Large effects (Cohen’s d = 0.99–1.83).

## Why This Matters

This work demonstrates that explicit belief modeling—not imitation or reward shaping—can yield socially aligned and interpretable AI behavior. Beyond human–AI interaction, the framework is methodologically aligned with computational psychiatry, where deviations in belief updating and social inference are central to conditions such as psychosis.

## Status

- **Scope:** Proof of concept.
- **Focus:** Interpretability, theory–experiment alignment, reproducibility.
- **Not a clinical system:** No diagnostic claims.

## Repository Structure

```
├── data/              Human pilot study data (dialogues, ratings, metadata)
├── apps/              Interactive Gradio apps for human evaluation and trace visualization
├── docs/              Full documentation (architecture, theory, experiments, reproducibility)
├── experiments/       Experiment runners and YAML configurations for parameter sweeps
├── results/           Experimental outputs organized by week (plots, summaries, raw data)
├── scripts/           Setup and configuration scripts (GitHub topics, environment setup)
├── src/               Core framework implementation
│   ├── agents/        Agent implementations (Bayesian MToM, baselines, factory)
│   ├── data/          Data loading and processing utilities
│   ├── envs/          Negotiation and interaction environments
│   ├── experiments/   Experiment orchestration and logging
│   ├── metrics/       SIQ and performance evaluation metrics
│   ├── models/        Bayesian belief models and social reasoning
│   ├── observers/     Human perception models (noisy, biased, adversarial)
│   ├── social/        Social inference and Theory‑of‑Mind computations
│   └── utils/         Helper functions and configuration
├── tests/             Unit and integration tests for all components
└── tools/             Analysis and validation tools (human pilot stats, figures, PDF generation)
```

## Documentation & Reproducibility

- **Paper:** Included in this repository.
- **Full documentation:** See [docs/README.md](docs/README.md).
- **Reproducible experiments:** Configuration‑driven with seeds specified per config/artifact.

## Intended Audience

- Human–AI Interaction (HCI)
- Social and Multi‑Agent AI
- Bayesian Cognitive Modeling
- Computational Psychiatry (methodological foundations)
- Theoretical approaches to social alignment in AI

---

For reviewer-safe, artifact-backed results, see [docs/Results.md](docs/Results.md). For full theoretical details, experimental protocols, and reproducibility instructions, see [docs/README.md](docs/README.md).
