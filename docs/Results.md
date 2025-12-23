# Results (Reviewer-Safe): Empirical Evidence for Machine Theory of Mind (MToM)

## 1. Scope and Reporting Policy

This repository is a **proof-of-concept** evaluation of Machine Theory of Mind (MToM) agents. This document is intentionally **reviewer-safe**:

- We only state numbers that are directly supported by artifacts in `results/` or by executable configs in `experiments/config/`.
- We avoid claiming analyses that are not implemented (e.g., Tukey HSD, ICC/Cronbach’s α) and avoid inflated sample-size language.
- Where results vary by week/config, we report them **by artifact** (Week 3 / Week 5 / Week 7 / Week 10).

## 2. Experimental Setup (Simulation)

### 2.1 Negotiation Environment

The core environment is the discrete negotiation task implemented in `src/envs/negotiation_v1.py`.

- **Total resources:** `total_resources = 10` (default)
- **Horizon:** `max_turns = 3` (default)
- **Action space:** integer splits encoded as `(agent0_share, agent1_share)` with `agent0_share ∈ {1, …, total_resources-1}` (i.e., 1…9 when `total_resources=10`) and the remainder given to the other agent.

These defaults are also used in Week 2 configs (see `experiments/config/negotiation_week2.yaml`).

### 2.2 Run Counts / Replicates (No Inflation)

Run counts differ by experiment suite and are defined in config files:

- **Week 2 agent comparison:** `experiment.num_runs = 10` (per (agent, λ) configuration), `seed = 42` (see `experiments/config/negotiation_week2.yaml`).
- **Week 7 robustness suite:** `num_seeds = 1`, `runs_per_config = 3` (see `experiments/config/robustness_suite.yaml`).

We do **not** claim uniform “50 seeds per config” or similarly large-N designs unless an artifact explicitly records such counts.

### 2.3 Metrics and Logged Outputs

Across the simulation runners, the following fields are logged per episode (names vary slightly across weeks):

- `task_reward` (normalized by `total_resources`)
- `warmth`, `competence`, and `social_score`
- `total_utility` (typically `task_reward + λ * social_score` in the runners)
- `num_turns`, `final_agreement`

Composite SIQ summaries appear in week-specific artifacts (e.g., `results/week3/siq_summary.json`, `results/week5/analysis_summary.json`).

## 3. Simulation Results (What the Repo Actually Supports)

### 3.1 SIQ Snapshot (Week 3)

`results/week3/siq_summary.json` provides aggregated SIQ and component values by agent. Example values from that artifact:

- `bayesian_mtom`: SIQ ≈ 0.796, ethical_consistency ≈ 0.622
- `greedy_baseline`: SIQ ≈ 0.524, ethical_consistency ≈ 0.067
- `simple_mtom`: SIQ ≈ 0.539, ethical_consistency ≈ 0.067

Important: **ethical consistency is not uniformly 1.0** across settings; it depends on the scenario and the SIQ component definitions.

### 3.2 Sweep / Best-Combo Summary (Week 5)

Week 5 provides two useful “paper-ready” artifacts:

- `results/week5/analysis_summary.json` (includes SIQ components for many Bayesian combinations)
- `results/week5/stats_summary.json` (reports a “best combo” vs baseline summary with a 95% CI and Cohen’s d)

From `results/week5/stats_summary.json`:

- Baseline referenced: `simple_mtom`
- Reported difference in means: `difference_mean ≈ 0.0567`
- Reported 95% CI: `[0.0476, 0.0658]`
- Reported Cohen’s d: `≈ 0.394`

This is the **correct** place to cite an effect size/CI for the Week 5 sweep, instead of inventing ANOVA/Tukey outputs.

### 3.3 Robustness Suite (Week 7)

Robustness experiments are configured in `experiments/config/robustness_suite.yaml` and logged in `results/week7/robustness_suite/robustness_results.jsonl`.

Key facts that are safe to claim:

- The suite includes multiple **noisy-channel** profiles (e.g., `noise_std`, `deception_prob`, `dropout_prob`, `bias`).
- It includes several **domain shifts** that explicitly change `total_resources` and `max_turns` (e.g., scarce_resources uses 6 resources, abundant_long uses 18 resources and 8 turns).
- The run budget is small and explicit: `num_seeds = 1`, `runs_per_config = 3`.

This supports qualitative and descriptive robustness claims (e.g., “evaluated under adversarial feedback channels”), but does **not** justify high-powered inferential statements unless you compute them from the JSONL.

### 3.4 Small-λ Validation (Week 7)

`results/week7/lambda_validation_summary.json` is the artifact to cite for the micro-sweep. In the currently committed summary, the mean social score is identical for λ ∈ {0.0, 0.1, 0.2} (delta reported as 0.0). This means we should **not** claim a clearly observed linear improvement regime from that artifact alone.

## 4. Human Pilot Results (Week 10, As Logged)

### 4.1 What We Can Safely Claim

The pilot data is stored in `data/human_pilot/pilot_ratings.csv` and exported/aggregated into Week 10 artifacts.

Two key points for reviewer safety:

1. The repository includes both a paired-analysis pipeline and an unpaired one; the paired summary currently reports `n_pairs = 0` in `results/week10/human_pilot_stats_summary.csv`, indicating that within-subject pairing was not available in the aggregated pivot (see `results/week10/human_pilot_participant_means.csv`).
2. The unpaired (between-group) stats are available and should be cited.

### 4.2 Unpaired (Between-Group) Tests

`results/week10/human_pilot_unpaired_stats.csv` reports unpaired group sizes and Welch-style statistics (as stored in the artifact) for each metric:

- Warmth: `n1=11`, `n2=14`, `d≈0.99`, `p≈0.0186`
- Competence: `n1=11`, `n2=14`, `d≈1.83`, `p≈1.38e-4`
- Trust: `n1=11`, `n2=14`, `d≈1.62`, `p≈3.30e-4`

This supports the directionally correct claim that MToM is rated higher on warmth/competence/trust in the pilot **as collected**, while keeping the inferential framing consistent with the repo.

### 4.3 What We Do *Not* Claim

The repo does not (currently) provide artifacts that justify:

- Paired t-tests with large degrees of freedom (e.g., `df=149`)
- Inter-rater reliability metrics (ICC) or Cronbach’s α
- Tukey HSD post-hoc testing
- “Large-N simulation power” language (unless an artifact logs that study design)

## 5. Ethical Consistency (No “Perfect” Claims)

Ethical consistency appears as a component in SIQ summaries (e.g., `results/week3/siq_summary.json`, `results/week5/analysis_summary.json`). The numbers vary by week/config, and are not a mathematical guarantee of **0% violations** in all settings.

Reviewer-safe phrasing is:

- “Ethical consistency is high in several sweeps/configurations,” and
- “We do not claim universal zero-violation guarantees.”

## 6. Summary (Evidence-Backed)

Supported, reviewer-safe claims from the current repo state:

- The negotiation environment uses `total_resources=10`, `max_turns=3`, and an offer space of integer splits (1…9 for self-share).
- Week 2 comparisons run 10 replicates per configuration (as configured).
- Week 7 robustness uses small, explicit run counts and includes adversarial/noisy feedback channels and domain shifts.
- Week 10 human pilot supports unpaired comparisons with large effect sizes (Cohen’s d ≈ 1.0–1.8), but does not support paired inference from the stored data.

If you want, I can also add a short “How to regenerate” appendix that points to the exact commands/scripts that produce each artifact (still reviewer-safe, no new claims).
