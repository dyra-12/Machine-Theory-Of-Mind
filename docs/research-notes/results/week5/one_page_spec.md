# One-Page Spec — SIQ Prototype & Formal Objective

Objective
- Maximize expected negotiated utility subject to robustness and adaptation constraints.

Notation
- u(·): total utility for the agent in an episode.
- π_B(·|s): Bayesian MToM policy with parameters θ = {λ_social, prior_strength, risk_weight, schedule}.
- D: distribution over negotiation contexts (opponent types, observers, environment variants).

Formal objective (single-run expected utility):

E_{c∼D}[ u( π_B(·|c; θ) ) ]

Constrained optimization view (SIQ prototype):

maximize_θ  E_{c∼D}[ u(π_B(·|c; θ)) ]
subject to
  Robustness(θ) ≥ ρ_min
  AdaptationSpeed(θ) ≥ α_min

Where:
- Robustness(θ) := 1 − Var_{c∼D}[ u(π_B(·|c; θ)) ] / (1 + E_{c∼D}[ u(π_B(·|c; θ)) ])
- AdaptationSpeed(θ) := −E_{episode t=1..T}[ Δ_t ] where Δ_t is rolling short-term drop after context shift (higher is better)

Prototype SIQ scalarization (single metric used in experiments):

SIQ(θ) = w_u * E[ u ] + w_r * Robustness(θ) + w_a * AdaptationSpeed(θ)

With weights used for Week 5 reporting (example): w_u=1.0, w_r=0.25, w_a=0.5.

Evaluation Protocol
- For each candidate θ, evaluate on N episodes (N=1,920) sampled from held-out context grid.
- Report: mean utility, sd, 95% CI, robustness index, adaptation speed.

Deliverables (implementation note)
- `analyze_week5.py` should export per-θ rows with the above stats and plot Pareto frontiers in utility vs robustness and utility vs adaptation.

*Saved: `results/week5/one_page_spec.md`*
