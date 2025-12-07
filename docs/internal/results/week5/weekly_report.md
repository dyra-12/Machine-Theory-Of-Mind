# Summary — Bayesian MToM Hyperparameter Sweep & SIQ Analysis

🧠 **Objective**
This week’s focus was to systematically tune the Bayesian MToM agent and evaluate its Social Intelligence Quotient (SIQ) performance across prior strengths and social-weight parameters (λ).

The goal:
→ Reduce the aggregate-utility gap vs. the simple MToM baseline,
→ Improve cross-context generalization without losing adaptability.

⚙️ **Experimental Setup**

| Parameter | Values Tested |
|---|---|
| Prior strength | {4.1, 4.2, 4.3} |
| λ (social weighting) | {0.985 – 1.0} |
| Seeds per cell | 10 |
| Evaluation metrics | Task utility, SIQ (α=β=γ=δ=0.25), component scores |

Agent Types: `bayesian_mtom`, `simple_mtom`, and 3 baseline variants (`greedy`, `random`, `social`).

---

## 📊 Results Overview

### 1️⃣ SIQ Heatmap (priors × λ)

![SIQ Heatmap](plots/siq_heatmap.png)

SIQ values remain stable (~0.89–0.90) across the tested grid.

**Best configuration** ≈ (prior 4.2–4.3, λ ≈ 0.99) → max SIQ = 0.906.

Slight decline at λ = 1.0 indicates over-weighting the social term hurts balance.

**Interpretation:** Moderate λ and stronger priors achieve optimal social alignment without sacrificing utility.

---

### 2️⃣ Task Utility vs SIQ (Pareto Frontier)

![Task Utility vs SIQ](plots/siq_task_tradeoff.png)

Smooth positive trend confirms reward–social trade-off.

Higher prior strength (lighter points in the sweep) improves both metrics until plateau.

Bayesian agent occupies Pareto-front dominant region vs. simple MToM.

**Takeaway:** Bayesian ToM tuning moves the agent along the Pareto front toward balanced social intelligence.

---

### 3️⃣ SIQ Component Breakdown (by Agent)

![SIQ Component Breakdown](plots/week5_siq_components.png)

| Component | Bayesian MToM | Simple MToM | Δ |
|---|---:|---:|---:|
| Social Alignment | 0.86 | 0.68 | ↑ +26% |
| Theory-of-Mind Accuracy | 0.74 | 0.78 | – 4% |
| Cross-Context Generalization | 1.00 | 1.00 | ≈ |
| Ethical Consistency | 0.88 | 0.04 | ↑ huge gain |

**Observation:** Bayesian ToM boosts social and ethical dimensions while maintaining generalization.

---

### 4️⃣ SIQ Progression over Weeks (3 → 5)

![SIQ Trend Through Week 5](plots/siq_trend_through_week5.png)

`bayesian_mtom` shows steady growth (~+0.2 SIQ units).

`simple_mtom` plateaus.

`social_baseline` remains stable at a high level.

`random` and `greedy` decline — expected behavior given lack of social adaptation.

**Conclusion:** Learning curves validate that Bayesian MToM continues to adapt socially and ethically over time.

---

## 📈 Aggregate Findings

| Metric | Simple MToM | Bayesian MToM | Improvement |
|---|---:|---:|---:|
| Mean Task Utility | 1.09 | 1.13 | ↑ +3.7 % |
| Mean SIQ | 0.893 | 0.904 | ↑ +1.2 % |
| Generalization Score | 0.88 | 0.90 | ↑ +2.3 % |
| Utility Gap vs Baseline | –0.05 | –0.02 | ↓ 60 % |

**Interpretation:** Parameter tuning successfully narrowed the utility gap and enhanced overall SIQ, confirming the effectiveness of Bayesian prior adaptation.

**Note on Theory-of-Mind Accuracy:** The Simple MToM model achieves marginally higher ToM-Accuracy than the Bayesian MToM. This likely reflects its more rigid, environment-specific mapping of observer responses. The Bayesian MToM maintains a probabilistic representation of beliefs and adapts to new social contexts, trading off a small loss in raw accuracy for improved generalization and social alignment.

---

🧭 **Summary Statement**

The Week 5 hyperparameter sweep confirms that introducing and tuning a Bayesian ToM component meaningfully enhances the agent’s social intelligence (SIQ), narrows the reward gap with baselines, and yields a stable reward–social Pareto frontier.

The findings support using moderate prior strengths and λ ≈ 0.99 for the next stage of multi-week experiments.

🧩 **Optional for Week 6**

To quantify this trade-off further:

Compute Δ ToM Accuracy vs Δ Social Alignment across λ values and plot one versus the other. We expect a small negative correlation showing that a small loss in ToM accuracy buys a big gain in alignment and ethics — a useful figure for a paper (“Social Adaptation Trade-off Curve”).

---

*Generated from: `results/week5/analysis_summary.json` and plots in `results/week5/plots/`.*

*** End of report ***
