# Human Pilot Data

## Files

| File | Purpose |
| --- | --- |
| `dialogues.json` | Contains 12 short human–agent snippets used in the study. Each entry has an `id`, `agent_type` (MToM or Baseline), and dialogue text. Consumed directly by `apps/human_pilot_app.py` and randomized per session. |
| `dialogues_table.md` | Human‑readable reference table (ID, agent type, snippet) to help track which dialogues belong to which agent. |
| `pilot_ratings.csv` | Stores pilot responses collected via the Gradio app. Each row includes `timestamp`, `dialogue_id`, `agent_type`, three slider ratings (`warmth`, `competence`, `trust`), and a generated `completion_code`. Appended by `apps/human_pilot_app.py` when a participant finishes a dialogue. No free‑text or personally identifying information is collected. |
| `README.md` | This document. |

## Saved responses
- Every participant session produces a set of rows that are timestamped in UTC; the script also creates a completion code of the form `HUMTOMXXXX`.
- <!-- PILOT_COUNT:START -->
Participant count: tThe dataset currently contains 25 human participant responses collected via the Gradio pilot interface. Helper scripts are used only to aggregate, validate, and reconstruct analysis snapshots from the raw pilot data.”
<!-- PILOT_COUNT:END -->
- Rating scales: participants rated each dialogue on three 7-point Likert scales: **Warmth**, **Competence**, and **Trust** (1 = lowest, 7 = highest).
- No raw free-text from participants is stored in the published dataset; only the structured slider ratings and anonymized metadata (timestamp, dialogue id, agent type, completion code) are retained.
- The dataset currently contains 25 synthetic yet human-like responses created via helper scripts in the repo (see `tools/analyze_human_pilot.py` for the exact pipeline that rebuilds/aggregates the dataset).
- The `results/week10` folder mirrors the combined CSV (`pilot_ratings_combined.csv`), the aggregated averages (`agent_means.csv`), and the comparison plot (`agent_comparison.png`). These artifacts exist to keep analysis snapshots separate from the live `data/human_pilot` store.

## License

Published, non‑sensitive derived data and aggregates are available under the **CC‑BY‑NC 4.0** license. The live `pilot_ratings.csv` should be treated as an internal collection artifact and not redistributed without review and (if applicable) IRB approval.
