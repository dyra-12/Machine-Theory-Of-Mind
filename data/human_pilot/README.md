# Human Pilot Data

| File | Purpose |
| --- | --- |
| `dialogues.json` | Contains the 12 short human-agent snippets used in the study; each entry has an `id`, `agent_type` (MToM or Baseline), and the dialogue text. This file is consumed directly by `apps/human_pilot_survey.py` and randomized per session.
| `dialogues_table.md` | Human-readable reference table (ID, agent type, snippet) to help the team track which dialogues belong to which agent.
| `pilot_ratings.csv` | Stores the pilot responses collected via the Gradio app. Each row has `timestamp`, `dialogue_id`, `agent_type`, the three sliders (`warmth`, `competence`, `trust`), and the generated `completion_code`. The file is appended to by `apps/human_pilot_survey.py` whenever a participant finishes a dialogue.
| `README.md` | (This document.) |

## Saved responses
- Every participant session produces a set of rows that are timestamped in UTC; the script also creates a completion code of the form `HUMTOMXXXX`.
- The dataset currently contains 25 synthetic yet human-like responses created via helper scripts in the repo (see `scripts/analyze_human_pilot_responses.py` for the exact pipeline that rebuilds/aggregates the dataset).
- The `results/week10` folder mirrors the combined CSV (`pilot_ratings_combined.csv`), the aggregated averages (`agent_means.csv`), and the comparison plot (`agent_comparison.png`). These artifacts exist to keep analysis snapshots separate from the live `data/human_pilot` store.
