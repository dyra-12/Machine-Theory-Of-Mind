# Reproducibility Guide

> **For Reviewers**: This document provides complete, step-by-step instructions to reproduce all experimental results from the paper. Estimated total time: 4–6 hours for core experiments (parallelizable to ~2 hours with appropriate hardware).

---

## Quick Start (5 minutes)

For reviewers who want to verify the setup and run a minimal sanity check:

```bash
# Clone and setup
git clone https://github.com/dyra-12/Machine-Theory-Of-Mind.git
cd Machine-Theory-Of-Mind
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt

# Run tests to verify installation
python -m pytest tests/ -q

# Quick validation: single negotiation episode (~30 seconds)
python src/main.py --agent bayesian --opponent fair --lambda-social 0.3 --seed 42
```

**Expected output**: Console logs showing negotiation turns, final utilities, and social scores. If this completes without errors, your environment is correctly configured.

---

## Table of Contents

1. [Purpose and Scope](#1-purpose-and-scope)
2. [Repository Structure](#2-repository-structure-overview)
3. [Installation and Environment Setup](#3-installation-and-environment-setup)
4. [Running Core Experiments](#4-running-core-experiments)
5. [Mapping to Paper Results](#5-mapping-experiments-to-paper-results)
6. [SIQ Computation](#6-siq-computation-reproducibility)
7. [Statistical Analysis](#7-statistical-analysis)
8. [Human Pilot Study](#8-human-pilot-reproducibility)
9. [Determinism and Variance](#9-determinism-and-variance-reporting)
10. [Known Limitations](#10-known-limitations-of-reproducibility)
11. [Troubleshooting](#11-troubleshooting)
12. [Citation and Contact](#12-citation-and-versioning)

---

## 1. Purpose and Scope

This document describes how to reproduce **all experimental results reported in the paper** associated with this repository.

**In scope**

- **Simulation experiments (Weeks 2–7)**
- **SIQ computation** (Social Intelligence Quotient)
- **Robustness, ablations, and generalization** studies
- **Human pilot analysis** using *aggregated, anonymized* artifacts

**Important notes**

- This repository is a **proof-of-concept research system** intended for scientific evaluation.
- **No clinical claims** are made, and nothing here should be interpreted as clinical guidance or a medical device.

### 1.1 Claims Covered by Reproducibility

This reproducibility guide supports verification of the following claims **made in the paper**:

✅ **SIQ (Social Intelligence Quotient) improvement**: MToM agents achieve 15-20% higher SIQ than baselines  
✅ **Task performance maintenance**: MToM maintains ≥95% of baseline task rewards while improving social metrics  
✅ **Robustness and generalization**: Cross-context SIQ degradation <8% across novel opponent strategies  
✅ **Human preference validation**: Pilot study (N=25) shows significant improvements in warmth (+0.78), competence (+1.89), and trust (+1.75)  
✅ **Pareto optimality**: Multi-objective trade-offs between task utility and social perception  
✅ **Ablation studies**: Effects of λ, prior strength, and SIQ component weights  
✅ **Statistical significance**: All reported p-values, effect sizes, and confidence intervals  

**Explicitly excluded from reproducibility scope**:

❌ **Clinical applicability**: No claims about therapeutic use, medical efficacy, or patient outcomes  
❌ **Real-world deployment**: Results are from controlled simulation environments only  
❌ **Long-term effects**: Study covers short negotiation episodes, not longitudinal outcomes  
❌ **Population generalization**: Human pilot is a convenience sample, not representative of general population  

**Academic and legal protection**: Reviewers reproducing this work are validating **computational and statistical claims only**, not endorsing any clinical, therapeutic, or deployment-readiness assertions.

---

## 2. Repository Structure Overview

The following folders are the ones that matter most for reproduction:

- `src/` — core implementation (agents, environments, metrics, analysis utilities)
- `experiments/` — experiment runners (entrypoints for sweeps and trace generation)
- `experiments/config/` — YAML experiment definitions (the “source of truth” for sweeps)
- `results/` — reference outputs used in the paper (plots + summary JSON/CSV)
- `scripts/` — analysis/aggregation helpers (when applicable)
- `data/` — human pilot and synthetic data used by the demos/analysis

**Paper mapping rule of thumb**: figures and tables in the paper map directly to files under `results/` (typically `results/week*/plots/` for figures and `results/week*/` for JSON/CSV summaries).

---

## 3. Installation and Environment Setup

### 3.1 System Requirements

**Operating Systems**
- Linux (Ubuntu 20.04+, tested)
- macOS (11.0+, tested)
- Windows (via WSL2, not extensively tested but should work)

**Python Version**
- Python 3.9, 3.10, or 3.11 (3.10 recommended)
- Verify: `python --version` or `python3 --version`

**Hardware**
- **CPU**: Any modern multi-core processor (experiments are CPU-bound)
- **RAM**: Minimum 8GB, recommended 16GB for parallel sweeps
- **Disk**: ~2GB for repository + dependencies + results
- **GPU**: Not required (PyTorch components default to CPU)

**Estimated Runtime**
- Full Week 5 sweep (main results): ~90 minutes on 4-core CPU
- Week 3-7 complete suite: ~4-6 hours total
- Human pilot analysis (pre-collected data): <5 minutes

### 3.2 Installation Steps

#### Option A: Standard Python Environment (Recommended)

```bash
# 1. Clone repository
git clone https://github.com/dyra-12/Machine-Theory-Of-Mind.git
cd Machine-Theory-Of-Mind

# 2. Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# 4. Verify installation
python -m pytest tests/ -v
```

**Key dependencies** (see `requirements.txt` for full list):
- `numpy>=1.21.0` — numerical computing
- `pandas>=1.3.0` — data manipulation
- `pymc>=5.0.0` — Bayesian modeling
- `torch>=1.9.0` — neural components (CPU-only is fine)
- `matplotlib>=3.5.0`, `seaborn>=0.11.0` — visualization
- `gradio>=3.50.0` — human study interface
- `statsmodels>=0.14.0` — statistical tests

#### Option B: Docker Container

```bash
# Build image
docker build -t mtom:latest .

# Run container with mounted workspace
docker run -it --rm -v $(pwd):/app mtom:latest bash

# Inside container: run experiments as normal
python -m pytest tests/ -q
```

### 3.3 Verification Checklist

After installation, verify the following:

```bash
# ✓ Test suite passes
python -m pytest tests/ -q  # Should show all tests passing

# ✓ Import core modules
python -c "from src.agents.bayesian_mtom_agent import BayesianMToMAgent; print('✓ Core imports OK')"

# ✓ SIQ metric loads
python -c "from src.metrics.siq import compute_siq; print('✓ SIQ metric OK')"

# ✓ Config files parse
python -c "import yaml; yaml.safe_load(open('experiments/config/week5_bayesian_sweep.yaml')); print('✓ Config files OK')"
```

**Expected result**: All checks should print "✓" without errors.

---

## 4. Running Core Experiments

### 4.0 Experiment Overview

**Summary Table**

| Experiment | Config File | Runtime | Key Outputs | Paper Figures |
|------------|-------------|---------|-------------|---------------|
| **Week 5 Bayesian Sweep** | `week5_bayesian_sweep.yaml` | ~90 min | SIQ heatmaps, Pareto plots | Fig 2-4, Table 1-3 |
| **Week 3 Validation** | `week3_comprehensive.yaml` | ~45 min | λ sensitivity, generalization | Fig 5-6, Table 4 |
| **Week 6 SIQ Validation** | `week6_siq.yaml` | ~30 min | Component ablations | Table 5, Supp. Fig S2 |
| **Week 7 Robustness** | `robustness_suite.yaml` | ~90 min | Cross-context tests | Fig 7, Table 6 |
| **Trace Generation** | (via scripts) | ~20 min | Belief trajectories | Supp. Materials |
| **Human Pilot Analysis** | (pre-collected data) | <5 min | Statistical summaries | Fig 8, Table 7-8 |

**Total estimated time**: 4-6 hours (parallelizable to ~2 hours with multi-core processing)

### 4.0.1 Determinism Configuration

All experiments use **fixed random seeds** for reproducibility:
- Primary seeds: `11, 17, 23, 29, 31` (5-seed average for main results)
- λ (social weight) sweep: `[0.1, 0.3, 0.5, 0.7]` (Week 3-4) or `[0.985, 0.99, 0.995, 1.0]` (Week 5 fine-grained)
- Bayesian prior strengths: `[4.1, 4.2, 4.3]` (Week 5 sweep)

Set seeds are embedded in YAML configs; reproducibility claims are based on these configurations.

### 4.1 Main Results: Week 5 Bayesian Sweep

**What it reproduces**: Figures 2-4 and Tables 1-3 in the paper (Pareto frontiers, SIQ heatmaps, component breakdowns).

**Command**:
```bash
# Run the full sweep (estimated time: ~90 minutes)
python experiments/run_experiment.py --config experiments/config/week5_bayesian_sweep.yaml

# Generate analysis plots and summaries
python src/experiments/analyze_week5.py
```

**Alternative (Makefile)**:
```bash
make reproduce  # Runs both commands above
```

**Expected outputs** (check these files were created):
```
results/week5/
├── analysis_summary.json          # Aggregate statistics
├── bayesian_combo_summary.csv     # Agent × outcome table
├── stats_summary.json             # Detailed SIQ/utility stats
└── plots/
    ├── siq_heatmap.png           # Figure 2
    ├── pareto_utility_vs_adaptation.png  # Figure 3
    ├── week5_siq_components.png  # Figure 4
    └── ... (7 plots total)
```

**Verification**:
```bash
# Check plot generation
ls -lh results/week5/plots/*.png | wc -l  # Should output: 7

# Inspect summary statistics
python -c "import json; print(json.dumps(json.load(open('results/week5/stats_summary.json')), indent=2)[:500])"
```

### 4.2 Week 3: Comprehensive Validation

**What it reproduces**: Agent generalization curves, λ sensitivity analysis (Figures 5-6, Table 4).

**Command**:
```bash
python experiments/run_experiment.py --config experiments/config/week3_comprehensive.yaml
python src/experiments/analyze_week3.py
```

**Runtime**: ~45 minutes

**Expected outputs**:
```
results/week3/
├── siq_summary.json
└── plots/
    ├── pareto_frontiers.png
    ├── lambda_sensitivity.png
    └── performance_comparison.png
```

### 4.3 Week 6: SIQ Validation

**What it reproduces**: SIQ component sensitivity, weight ablations (Table 5, Supplementary Figure S2).

**Command**:
```bash
python experiments/run_experiment.py --config experiments/config/week6_siq.yaml
python src/experiments/siq_visualizations.py
```

**Runtime**: ~30 minutes

**Note**: This experiment validates that SIQ's weighted components correlate with human ratings and remain stable under weight perturbations.

### 4.4 Week 7: Robustness Suite

**What it reproduces**: Cross-context generalization, opponent-type robustness (Figure 7, Table 6).

**Command**:
```bash
python experiments/run_experiment.py --config experiments/config/robustness_suite.yaml
python experiments/run_experiment.py --config experiments/config/negotiation_generalization.yaml
python src/experiments/analyze_robustness.py
```

**Runtime**: ~90 minutes (runs across 4 opponent types × 3 cultural templates)

**Expected outputs**:
```
results/week7/
├── lambda_validation_summary.json
├── robustness_summary_bar.png
├── robustness_suite/robustness_results.jsonl
└── plots/
    ├── social_score_vs_turn.png
    └── social_score_vs_turn_extended.png
```

### 4.5 Trace Generation and Belief Visualization

**What it reproduces**: Belief trajectory plots, dashboard data (Supplementary Materials).

**Command**:
```bash
# Generate trace logs
python experiments/run_trace_sweep.py
python experiments/run_trace_sweep_extended.py

# Launch interactive dashboard (optional)
streamlit run demo/trace_dashboard.py
```

**Runtime**: ~20 minutes for trace generation

**Dashboard**: Opens at `http://localhost:8501` — allows interactive exploration of belief dynamics.

### 4.6 Human Pilot Analysis

**What it reproduces**: Human evaluation results (Figure 8, Tables 7-8).

**Command**:
```bash
# Re-run statistical analysis on pre-collected data
python tools/analyze_human_pilot.py
python tools/analyze_human_pilot_stats.py
```

**Runtime**: <5 minutes

**Expected outputs**:
```
results/week10/
├── agent_means.csv                # Table 7
├── human_pilot_stats_summary.csv  # Table 8
├── agent_comparison.png           # Figure 8
└── human_pilot_paired_*.png       # Supplementary plots
```

**Important**: This analyzes the **pre-collected** data in `data/human_pilot/pilot_ratings.csv`. The live collection interface (`demo/human_pilot_app.py`) is provided for transparency but not required for reproduction.

### 4.7 Running All Experiments (Complete Reproduction)

To reproduce everything in sequence:

```bash
# Set up environment (if not already done)
source .venv/bin/activate

# Run all experiments (estimated total: 4-6 hours)
python experiments/run_experiment.py --config experiments/config/week3_comprehensive.yaml
python src/experiments/analyze_week3.py

python experiments/run_experiment.py --config experiments/config/week5_bayesian_sweep.yaml
python src/experiments/analyze_week5.py

python experiments/run_experiment.py --config experiments/config/week6_siq.yaml
python src/experiments/siq_visualizations.py

python experiments/run_experiment.py --config experiments/config/robustness_suite.yaml
python experiments/run_experiment.py --config experiments/config/negotiation_generalization.yaml
python src/experiments/analyze_robustness.py

python experiments/run_trace_sweep_extended.py

python tools/analyze_human_pilot.py
python tools/analyze_human_pilot_stats.py

# Verify all expected outputs exist
python tools/verify_reproduction_artifacts.py  # (if available)
```

### 4.8 Partial Reproduction (Time-Constrained Reviewers)

If you have limited time, prioritize **Week 5** (main results) + **Week 10** (human validation):

```bash
# Core results only (~2 hours)
make reproduce  # Week 5 sweep
python tools/analyze_human_pilot_stats.py  # Human pilot stats
```

This reproduces the paper's headline claims (Pareto optimality, SIQ gains, human preference).

---

## 5. Mapping Experiments to Paper Results

This section is intended for reviewers: it maps paper artifacts to exact repository files.

If the final camera-ready paper has different figure/table numbering, replace the “Figure/Table ID” in the left column while keeping the file paths unchanged.

| Paper Figure / Table (describe) | Output artifact in repo |
| --- | --- |
| Figure/Table (Week 5) — SIQ heatmap | `results/week5/plots/siq_heatmap.png` |
| Figure/Table (Week 5) — Utility heatmap | `results/week5/plots/utility_heatmap.png` |
| Figure/Table (Week 5) — SIQ task tradeoff | `results/week5/plots/siq_task_tradeoff.png` |
| Figure/Table (Week 5) — SIQ component breakdown | `results/week5/plots/week5_siq_components.png` |
| Figure/Table (Week 5) — Pareto (utility vs adaptation) | `results/week5/plots/pareto_utility_vs_adaptation.png` |
| Figure/Table (Week 5) — Pareto (utility vs robustness) | `results/week5/plots/pareto_utility_vs_robustness.png` |
| Figure/Table (Week 5) — Aggregate stats summary | `results/week5/analysis_summary.json` |
| Table (Week 5) — Detailed statistics | `results/week5/stats_summary.json` |
| Table (Week 5) — Prior×λ merged outcomes | `results/week5/bayesian_combo_summary.csv` |
| Figure/Table (Week 4) — Generalization curves | `results/week4/plots/generalization_env_curves.png` |
| Figure/Table (Week 4) — Easy vs hard bar plot | `results/week4/plots/easy_vs_hard_bar.png` |
| Figure/Table (Week 4) — Observer×opponent heatmap | `results/week4/plots/bayesian_observer_opponent_heatmap.png` |
| Table (Week 4) — Analysis summary | `results/week4/analysis_summary.json` |
| Figure/Table (Week 3) — Pareto frontiers | `results/week3/plots/pareto_frontiers.png` |
| Figure/Table (Week 3) — λ sensitivity | `results/week3/plots/lambda_sensitivity.png` |
| Figure/Table (Week 3) — Performance comparison | `results/week3/plots/performance_comparison.png` |
| Table (Week 3) — SIQ summary | `results/week3/siq_summary.json` |
| Figure/Table (Week 7) — Social score vs turn | `results/week7/plots/social_score_vs_turn.png` |
| Figure/Table (Week 7) — Social score vs turn (extended) | `results/week7/plots/social_score_vs_turn_extended.png` |
| Table (Week 7) — λ validation summary | `results/week7/lambda_validation_summary.json` |
| Table (Week 7) — Robustness results (JSONL) | `results/week7/robustness_suite/robustness_results.jsonl` |
| Figure/Table (Week 7) — Robustness summary bar | `results/week7/robustness_summary_bar.png` |
| Figure/Table (Week 7) — Posterior trace example | `results/week7/posterior_trace_example.png` |
| Table (Week 7) — Trace-derived score summary | `results/week7/summaries/social_score_summary_extended.csv` |
| Figure/Table (Week 10) — Human pilot agent comparison | `results/week10/agent_comparison.png` |
| Figure/Table (Week 10) — Paired warmth | `results/week10/human_pilot_paired_warmth.png` |
| Figure/Table (Week 10) — Paired competence | `results/week10/human_pilot_paired_competence.png` |
| Figure/Table (Week 10) — Paired trust | `results/week10/human_pilot_paired_trust.png` |
| Table (Week 10) — Aggregated means | `results/week10/agent_means.csv` |
| Table (Week 10) — Participant means | `results/week10/human_pilot_participant_means.csv` |
| Table (Week 10) — Statistical summary | `results/week10/human_pilot_stats_summary.csv` |
| Table (Week 10) — Unpaired stats | `results/week10/human_pilot_unpaired_stats.csv` |
| Table (Week 10) — Combined cleaned ratings snapshot | `results/week10/pilot_ratings_combined.csv` |

Notes:

- The experiment-to-config mapping is also summarized in `EXPERIMENTS.md`.
- Some extended write-ups are stored under `docs/internal/results/` and are not required to reproduce the paper’s headline results.

---

## 6. SIQ Computation Reproducibility

### 6.1 Implementation Details

**Location**: `src/metrics/siq.py`

**Formula**: SIQ is computed as a weighted combination of four normalized components:

```
SIQ = w₁·(Social Alignment) + w₂·(ToM Accuracy) + w₃·(Cross-Context) + w₄·(Ethical)
```

where:
- **Social Alignment**: Proximity to normative warmth/competence targets (0-1 scale)
- **ToM Accuracy**: Inverse prediction error on observer ratings (0-1 scale)
- **Cross-Context**: Robustness across opponent types and cultural templates (0-1 scale)
- **Ethical Consistency**: Fairness constraint satisfaction (0-1 scale)

**Default weights** (from `week6_siq.yaml`):
```yaml
siq_weights:
  social_alignment: 0.35
  tom_accuracy: 0.30
  cross_context: 0.20
  ethical: 0.15
```

### 6.2 Key Properties

- **Normalization**: All components normalized to [0, 1] before weighting
- **Missing data handling**: Uses weighted average over available components
- **Configurability**: Component weights modifiable in YAML for sensitivity analyses

### 6.3 Verification

To verify SIQ computation:

```bash
# Test SIQ function
python -c "from src.metrics.siq import compute_siq; print('✓ SIQ module loads')"

# Expected SIQ ranges: 0.6-0.9 (MToM), 0.3-0.6 (baselines)
```

### 6.4 Provenance Guarantee

**All SIQ values in the paper are derived from logged traces**, not hand-computed. To audit:

```bash
# Check trace files exist
ls -lh results/week7/traces/*.json | head -3

# View SIQ in summaries
cat results/week5/stats_summary.json | grep -A 5 '"siq'
```

---

## 7. Statistical Analysis

**Tests and reporting**

- Welch’s t-test (unequal variance) for pairwise comparisons
- Effect sizes via Cohen’s d
- ANOVA across λ where applicable (e.g., multi-level comparisons)

**Statistical conventions**

- Significance level: α = 0.05
- Two-tailed tests

**Multiple comparisons**

- The codebase includes support for multiple-comparison correction (e.g., FDR / Bonferroni) where appropriate to the analysis.

**Code references**

- `src/experiments/rigorous_week3.py` (rigorous Week 3 analysis pipeline)
- `src/metrics/statistical_tests_fixed.py` (statistical test utilities)

---

## 8. Human Pilot Reproducibility

### 8.1 Data Collection Protocol

**Collection interface**: Gradio app (`demo/human_pilot_app.py`)

**Stimuli**: 12 negotiation dialogue snippets
- 6 from MToM agent
- 6 from Baseline agent
- Stored in `data/human_pilot/dialogues.json`

**Randomization**: Dialogue order randomized per participant session

**Rating scales**: Three 7-point Likert scales (1=lowest, 7=highest)
- **Warmth**: "How warm/friendly does the agent seem?"
- **Competence**: "How capable/intelligent does the agent seem?"
- **Trust**: "How much would you trust this agent?"

**Sample size**: N=25 participants (as reported in paper)

### 8.2 Data Schema

**File**: `data/human_pilot/pilot_ratings.csv`

**Columns**:
```
timestamp         | ISO 8601 UTC timestamp
dialogue_id       | Integer 1-12
agent_type        | "MToM" or "Baseline"
warmth            | Integer 1-7
competence        | Integer 1-7
trust             | Integer 1-7
completion_code   | String "HUMTOMXXXX"
```

**Privacy**: No PII collected; only structured ratings + anonymized metadata

### 8.3 Reproducibility Scope

**What IS reproduced**:
- Statistical analysis on pre-collected data
- Plot generation from aggregated data
- Effect size and significance calculations

**What is NOT reproduced**:
- Live data collection (requires human participants)
- Original Prolific recruitment process

### 8.4 Running the Analysis

```bash
# Re-run complete human pilot statistical analysis
python tools/analyze_human_pilot.py
python tools/analyze_human_pilot_stats.py

# Expected outputs created:
# - results/week10/agent_means.csv
# - results/week10/human_pilot_stats_summary.csv
# - results/week10/agent_comparison.png
```

**Verification**:
```bash
# Check data snapshot has correct N
wc -l data/human_pilot/pilot_ratings.csv  # Should show 26 (25 + header)

# View aggregated means
cat results/week10/agent_means.csv
```

### 8.5 Expected Results

| Metric     | Baseline | MToM | Δ (MToM − Baseline) | Cohen's d | p-value |
|------------|----------|------|---------------------|-----------|----------|
| Warmth     | 4.86     | 5.64 | **+0.78**           | 0.52      | 0.014   |
| Competence | 3.93     | 5.82 | **+1.89**           | 1.23      | <0.001  |
| Trust      | 4.43     | 6.18 | **+1.75**           | 1.15      | <0.001  |

All differences statistically significant at α=0.05 (two-tailed Welch's t-test).

---

## 9. Determinism and Variance Reporting

Exact numeric replication may vary slightly across machines and runs because:

- Some components (notably learning and Bayesian sampling) can introduce small stochasticity.
- Floating point arithmetic and library versions can cause minor drift.

Variance is handled via:

- **Multiple seeds** rather than single-run reporting
- **Mean ± std** reporting in summaries

The intended claim is that **qualitative conclusions are robust** to seed changes (e.g., trade-off shapes and relative rankings remain stable under re-runs).

---

## 10. Known Limitations of Reproducibility

---

## 11. Troubleshooting

### Common Issues and Solutions

#### Issue: `ModuleNotFoundError: No module named 'src'`

**Cause**: Python not finding the repository modules.

**Solution**:
```bash
# Ensure you're in the repository root
cd /path/to/Machine-Theory-Of-Mind

# Make sure virtual environment is activated
source .venv/bin/activate

# Add repo to Python path (temporary)
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# OR: Install as editable package
pip install -e .
```

#### Issue: `yaml.scanner.ScannerError` when loading configs

**Cause**: YAML syntax error or file not found.

**Solution**:
```bash
# Verify config exists and is valid
python -c "import yaml; yaml.safe_load(open('experiments/config/week5_bayesian_sweep.yaml'))"

# Check for tabs (YAML requires spaces)
grep -P '\t' experiments/config/*.yaml
```

#### Issue: Experiments run but no plots generated

**Cause**: Analysis scripts not run after experiment, or matplotlib backend issue.

**Solution**:
```bash
# Explicitly run analysis after experiment
python src/experiments/analyze_week5.py

# If matplotlib errors, try different backend
export MPLBACKEND=Agg
python src/experiments/analyze_week5.py
```

#### Issue: `RuntimeError: Bayesian inference failed`

**Cause**: PyMC sampling convergence issues (rare but possible).

**Solution**:
```bash
# Check PyMC version
pip show pymc | grep Version

# Try with increased sampling iterations (edit YAML or script)
# Or skip Bayesian-heavy components temporarily
```

#### Issue: Human pilot analysis shows different N than paper

**Cause**: You may be using a different snapshot of the data.

**Solution**:
```bash
# Verify you have the correct data snapshot
wc -l data/human_pilot/pilot_ratings.csv  # Should show 26 lines (25 + header)

# Check last commit date
git log -1 --format=%cd data/human_pilot/pilot_ratings.csv
```

#### Issue: Docker container can't access X display for plots

**Cause**: Docker doesn't have display forwarding configured.

**Solution**:
```bash
# Save plots to files instead of showing
# Plots are automatically saved to results/*/plots/ anyway

# Or: enable X forwarding (Linux/macOS)
xhost +local:docker
docker run -it --rm -e DISPLAY=$DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix -v $(pwd):/app mtom:latest
```

#### Issue: Results differ slightly from paper

**Expected**: Minor numerical differences (<1%) due to:
- Floating point precision across machines
- Library version differences
- OS-level RNG implementation differences

**Verify qualitative agreement**:
```bash
# Check that rankings/orderings match
python -c "
import pandas as pd
df = pd.read_csv('results/week5/bayesian_combo_summary.csv')
print('Top 5 configs by SIQ:')
print(df.nlargest(5, 'siq_mean')[['agent_type', 'lambda', 'siq_mean']])
"
```

If orderings and effect directions match, reproduction is successful.

### Getting Help

If issues persist:

1. **Check existing issues**: [GitHub Issues](https://github.com/dyra-12/Machine-Theory-Of-Mind/issues)
2. **Provide diagnostic info**:
   ```bash
   python --version
   pip list | grep -E "numpy|pandas|pymc|torch"
   uname -a  # or "ver" on Windows
   git rev-parse HEAD  # current commit
   ```
3. **Open a new issue** with:
   - Command you ran
   - Full error traceback
   - Diagnostic info from above
   - Expected vs. actual behavior

---

## 12. Citation and Versioning

### Recommended Citation

Cite this repository using the metadata in `CITATION.cff`:

```bibtex
@software{mtom2025,
  author = {[Author Names from CITATION.cff]},
  title = {Machine Theory of Mind: Socially-Aligned AI via Bayesian Mental-State Reasoning},
  year = {2025},
  url = {https://github.com/dyra-12/Machine-Theory-Of-Mind},
  version = {1.0.0},
  doi = {DOI_PLACEHOLDER}
}
```

### Version Control and Archival

**Paper commit hash**: `INSERT_COMMIT_HASH_HERE`

To reproduce the exact version used in the paper:
```bash
git checkout INSERT_COMMIT_HASH_HERE
```

**Tagged releases**: We recommend citing a tagged release (e.g., `v1.0.0`) for long-term archival stability:
```bash
git checkout tags/v1.0.0
```

**DOI**: A DOI-minted archive (Zenodo/Figshare) will be created upon paper acceptance. Check the repository README for the latest DOI badge.

### Contact and Reporting Issues

**For reproducibility issues specifically**:
- Open a GitHub Issue with the "reproducibility" label
- Include: OS, Python version, commit hash, exact command, error log

**For general questions**:
- See `CONTRIBUTING.md` for collaboration guidelines
- See `CODE_OF_CONDUCT.md` for community standards

**Primary contact**: [Insert contact from CITATION.cff or README]

---

## Appendix: File Verification Checklist

After running all experiments, verify these key files exist:

```bash
# Week 5 (main results)
[ -f results/week5/plots/siq_heatmap.png ] && echo "✓ W5 SIQ heatmap"
[ -f results/week5/plots/pareto_utility_vs_adaptation.png ] && echo "✓ W5 Pareto"
[ -f results/week5/stats_summary.json ] && echo "✓ W5 stats"

# Week 3
[ -f results/week3/plots/lambda_sensitivity.png ] && echo "✓ W3 λ sensitivity"

# Week 7
[ -f results/week7/robustness_summary_bar.png ] && echo "✓ W7 robustness"

# Week 10 (human pilot)
[ -f results/week10/agent_comparison.png ] && echo "✓ W10 human pilot"
[ -f results/week10/agent_means.csv ] && echo "✓ W10 stats table"

echo "Verification complete. All ✓ marks indicate successful reproduction."
```

Expected output: 7 ✓ marks (one for each check).

---

**Document version**: 1.0 (December 2025)  
**Last updated**: 23 December 2025  
**Maintainer**: See `CITATION.cff`
