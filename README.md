# Machine Theory of Mind (MToM)

**Belief-Based Social Reasoning for Interpretable Human–AI Interaction**

---

## Overview

Machine Theory of Mind (MToM) is a computational framework for developing artificial agents capable of explicit reasoning about how their actions are perceived by human observers. This framework integrates such social cognition into decision-making processes through probabilistic inference and multi-objective optimization.

Unlike conventional approaches that encode social behavior implicitly through reward shaping or heuristic functions, MToM models social cognition as a process of belief formation and inference, grounded in Bayesian reasoning principles. The architecture enables agents to maintain explicit mental state representations and update these representations through structured belief revision.

This repository presents a methodological proof-of-concept system emphasizing interpretability, diagnostic evaluation, and human-centered behavioral alignment.

---

## Motivation and Significance

Traditional artificial intelligence systems primarily optimize task-oriented objectives, whereas MToM explicitly addresses how actions are socially interpreted by human observers.

This approach provides several methodological advantages:

- **Explicit social reasoning**: Mental state representations are directly accessible for inspection and analysis
- **Transparent utility trade-offs**: Task performance and social alignment objectives are balanced through explicit parameterization
- **Distributional robustness**: System exhibits stable behavior under conditions of uncertainty, cultural norm variation, and noisy observational feedback
- **Diagnosable social intelligence**: Social reasoning mechanisms are structurally separable from task-oriented planning, enabling component-level analysis

---

## Theoretical Framework

The MToM agent architecture implements a sequential decision-making process wherein, at each timestep, the agent:

1. **Maintains probabilistic belief distributions** over latent social attributes (e.g., perceived warmth, competence) as evaluated by external observers
2. **Predicts social consequences** of candidate actions through forward modeling of observer perception
3. **Optimizes a multi-objective utility function** that explicitly balances task reward and social alignment via a tunable parameter λ ∈ ℝ⁺
4. **Adapts behavioral policy** through Bayesian belief updates rather than policy gradient learning

**Architectural properties:**

- The system does not employ learned policy networks
- Social metrics are not directly optimized; rather, they emerge from belief-conditioned decision rules
- Behavioral adaptation derives from belief state inference, reducing susceptibility to reward function exploitation

---

## Evaluation Methodology

Social reasoning capabilities are quantified using the **Social Intelligence Quotient (SIQ)**, a diagnostic post-hoc metric that decomposes system performance into four orthogonal components:

1. **Social alignment**: Proximity to normative social targets
2. **Theory-of-Mind accuracy**: Prediction fidelity for observer mental states
3. **Cross-context generalization**: Performance stability across varied interaction contexts
4. **Ethical consistency**: Adherence to fairness and equity constraints

**Critically, SIQ is not an optimization target and does not influence agent decisions.**

The evaluation protocol comprises:

- **Controlled simulation experiments**: Systematic variation of environmental parameters, opponent strategies, and observer types
- **Robustness and ablation studies**: Component-level sensitivity analysis and stress testing
- **Human evaluation study**: Pilot investigation (N = 25 participants) assessing perceived warmth, competence, and trustworthiness through within-subjects design

---

## Repository map (start here)
Documentation Structure

Comprehensive documentation is organized as follows:

- **System Architecture**: [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) — Technical implementation details and component specifications
- **Theoretical Foundations**: [`docs/theory.md`](docs/theory.md) — Formal framework and mathematical foundations
- **Experimental Design**: [`docs/EXPERIMENTS.md`](docs/EXPERIMENTS.md) — Methodology and experimental protocols
- **Empirical Results**: [`docs/Results.md`](docs/Results.md) — Quantitative findings and statistical analyses
- **Ethical Considerations**: [`ETHICS.md`](ETHICS.md) — Responsible use guidelines and limitations
- **Reproducibility Protocol**: [`docs/REPRODUIBILITY.md`](docs/REPRODUIBILITY.md) — Step-by-step reproduction instructions

For a comprehensive research narrative, refer to:  
[`docs/README.md`](docs/README.md)

---

## Scope of Application

This repository is designed to support:

- Academic research in socially intelligent and human-centered artificial intelligence
- Methodological investigations of belief-based decision architectures
- Reproducible computational experimentation and comparative analysis

**Important limitation**: This system represents a research prototype intended for scientific investigation. It is not validated for deployment in real-world applications or clinical decision-making contexts involving human subjects.

---

## Citation

Researchers utilizing this framework should reference the work according to the metadata provided in [`CITATION.cff`](CITATION.cff).

---

## Note on Documentation Design

This README provides a high-level overview of the research framework. Detailed technical specifications, theoretical derivations, and experimental protocols are documented in the linked resources above
