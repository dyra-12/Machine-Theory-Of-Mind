# Week 5 — Executive Summary (2 pages)

## TL;DR
- Sweep completed over λ ∈ {0.985, 0.99, 0.995, 1.0}, prior ∈ {4.1–4.3}, risk ∈ {0.50–0.60}, static/burst schedules.
- Best combo: **λ=0.995, prior=4.3, risk=0.55, static**, mean utility **1.2006** (n=1920) vs simple baseline **1.1439** (n=1920).
- Mean improvement: **+0.0567** (95% CI [0.0476, 0.0658], Cohen's d=0.39, power≈1.00).

## Key Figures
- Pareto — Utility vs Adaptation: `results/week5/plots/pareto_utility_vs_adaptation.png`
- Pareto — Utility vs Robustness: `results/week5/plots/pareto_utility_vs_robustness.png`
- Heatmap (λ × prior × risk): `results/week5/plots/utility_heatmap.png`

(Place these three figures across the top/bottom of page 1 and 2.)

## Short Table — Top Configurations

| Rank | λ | Prior | Risk | Schedule | Mean Utility | SD | n |
|------|----:|-----:|-----:|:--------:|-------------:|---:|--:|
| 1 | 0.995 | 4.3 | 0.55 | static | 1.2006 | 0.144 | 1920 |
| 2 | 0.995 | 4.3 | 0.50 | static | 1.2006 | 0.144 | 1920 |
| 3 | 0.990 | 4.3 | 0.55 | static | 1.1976 | 0.153 | 1920 |
| 4 | 0.995 | 4.3 | 0.60 | static | 1.1968 | 0.151 | 1920 |
| 5 | 0.990 | 4.3 | 0.50 | static | 1.1967 | 0.151 | 1920 |

(Expand to 8–10 rows for the final PDF layout.)

## Conclusions & Recommendations
- The Bayesian MToM now consistently outperforms the simple baseline on mean utility across top parameterizations; focus future tuning around prior ∈ [4.2–4.4] and λ∈[0.99–1.0].
- Keep `static` λ-schedule for stability; consider a confirmatory sweep with denser λ grid around 0.99–1.0.
- Publish figures and summary as `week5_summary.pdf` and add a short note in the repo `README` about the winning config.


---

*Saved: `results/week5/summary_2page.md`*
