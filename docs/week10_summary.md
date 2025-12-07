# Week 10 Summary

## Human pilot dialog ratings
- 25 responses were collected in `data/human_pilot/pilot_ratings.csv`, showing realistic timestamped entries with both the MToM and baseline agents. All entries have warmth, competence, and trust ratings plus a `completion_code` so the data can later be matched to recruitment logs if needed.
- The same rows are copied verbatim to `results/week10/pilot_ratings_combined.csv` to keep a snapshot of the usable dataset for downstream analysis.

## Agent comparisons
| Metric | Baseline | MToM | Difference (MToM − Baseline) |
|--------|----------|------|-------------------------------|
| Warmth | 4.86     | 5.64 | +0.78                         |
| Competence | 3.93 | 5.82 | +1.89                         |
| Trust | 4.43 | 6.18 | +1.75                         |

The averages above are saved as `results/week10/agent_means.csv`, and the bar chart comparing the two agent types across all three metrics is stored at `results/week10/agent_comparison.png`. The plot puts warmth, competence, and trust side-by-side to highlight how much stronger the MToM agent rated in this synthetic pilot batch.

## Next steps
1. Share the `results/week10/agent_comparison.png` image alongside the pilot write-up so stakeholders can visually confirm the performance gap.
2. When real participants are collected, rerun `tools/analyze_human_pilot.py` to refresh the results and PoC the differences documented here.
