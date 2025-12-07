# Experiment Manifest

This document maps experiment configuration files (YAML) to the figures and
analyses they reproduce. Use the `reproduce` Makefile target for the primary
reproduction workflow (Week 5 sweep). Each entry also includes a short note of
what the corresponding "Week" refers to in our development schedule.

## How to run

From the repository root (after `make install`):

```bash
# reproduce the Week 5 sweep and analysis (Pareto plots, SIQ heatmaps)
make reproduce
```

Or run an individual config directly:

```bash
python experiments/run_experiment.py --config experiments/config/week5_bayesian_sweep.yaml
python src/experiments/analyze_week5.py
```

## Configurations

- `experiments/config/negotiation_base.yaml`
  - Purpose: Basic negotiation environment defaults used as a starting point for other sweeps.
  - Produces: baseline statistics and sanity-check plots.
  - Week: foundational / Week 2

- `experiments/config/negotiation_week2.yaml`
  - Purpose: Early negotiation rule-set and opponent validations.
  - Produces: simple utility and fairness plots.
  - Week: Week 2

- `experiments/config/week3_comprehensive.yaml`
  - Purpose: Systematic agent validation across hyperparameters.
  - Produces: generalization curves and easy-vs-hard analyses.
  - Week: Week 3

- `experiments/config/week5_bayesian_sweep.yaml`
  - Purpose: Main Bayesian MToM parameter sweep used in the paper.
  - Produces: Pareto frontiers, `siq_heatmap.png`, `siq_task_tradeoff.png`, `week5_siq_components.png` in `results/week5/plots/`.
  - Week: Week 5 (main results)

- `experiments/config/week6_siq.yaml`
  - Purpose: SIQ validation and sensitivity analyses (weights, components).
  - Produces: SIQ component breakdowns and trend plots.
  - Week: Week 6

- `experiments/config/robustness_suite.yaml`
  - Purpose: Cross-context robustness across opponent types and cultural templates.
  - Produces: generalization plots and aggregated stats in `results/robustness_suite/`.
  - Week: Week 7

- `experiments/config/negotiation_generalization.yaml`
  - Purpose: Hold-out environment tests for generalization metrics.
  - Produces: held-out performance curves and cross-context SIQ values.
  - Week: Week 7

If you add new experiments, please update this manifest with the config filename,
the expected output files, and the Week the experiment belongs to.
