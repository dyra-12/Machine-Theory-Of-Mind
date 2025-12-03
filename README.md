# Machine Theory of Mind

Utility scripts, experiments, and dashboards for analyzing negotiation agents with Theory-of-Mind reasoning.

## Week 7 Streamlit Dashboard

Visualize negotiation playback and belief traces captured in `results/week7/traces`.

```
pip install -r requirements.txt  # ensure dependencies such as streamlit, pandas, altair
streamlit run apps/week7_trace_dashboard.py
```

The app lets you:

- Choose any recorded trace from Week 7 analyses.
- Scrub through each step to inspect offers, acceptance, and computed social scores.
- Plot belief trajectories (warmth vs. competence) and social-score timelines.
- Inspect the raw JSON trace for deeper debugging.

If no traces exist yet, generate them via `python experiments/run_trace_sweep.py` or `run_trace_sweep_extended.py` first.
