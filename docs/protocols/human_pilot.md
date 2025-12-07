# Human Pilot Survey Protocol

## Overview
This pilot invites participants to read short dialogues between a human and two versions of an agent (MToM vs baseline) and rate each in terms of warmth, competence, and trust. The interface is served by `demo/human_pilot_app.py`, which randomizes dialogue order per participant, collects the three sliders, and records each response with a completion code for Prolific verification.

## Consent text
Participants see this text before the survey begins:

> **Welcome!**
>
> You’ll read short dialogues with AI assistants and rate them on warmth, competence, and trust.
> The study is anonymous, takes under 7 minutes, and stores no personal data.
> By clicking **Start**, you agree to participate voluntarily.

## Procedure
1. **Start screen** – Participants land on the consent/instructions page above and confirm understanding by clicking **Start the Study**.
2. **Dialogue experience** – Dialogues are loaded one at a time. Every dialogue is small (2-3 turns) and is displayed inside a bordered text box with human (`👤`) and agent (`🤖`) labels. The rating section displays three sliders, each ranging 1–7, with explicit labels describing what high/low values mean.
3. **Rating questions** – For each dialogue, participants answer:
   - Warmth – “How friendly or empathetic does this agent seem?”
   - Competence – “How capable or intelligent does this agent seem?”
   - Trust – “How much would you trust this agent in a future interaction?”
4. **Progress tracking** – A badge at the top shows the current dialogue number (e.g., “Dialogue 5 of 12”). Clicking **Next Dialogue ➡️** saves the scores and loads the next snippet until all dialogues are rated.
5. **Completion code** – After the final dialogue everyone sees a thank-you banner plus a completion code such as `HUMTOM4821` that participants can paste into Prolific to prove they finished the study.

## Data handling
Responses are appended to `data/human_pilot/pilot_ratings.csv` with the following columns:
- `timestamp` – UTC timestamp of submission
- `dialogue_id` – identifier for the dialogue (e.g., `MTOM-01`)
- `agent_type` – either `MToM` or `Baseline`
- `warmth`, `competence`, `trust` – slider values (1–7)
- `completion_code` – generated code used for participant verification

A copy of the dataset is written to `results/week10/pilot_ratings_combined.csv` and the averages by agent type are stored in `results/week10/agent_means.csv`. `tools/analyze_human_pilot.py` reloads the saved CSV, recomputes averages, and produces a bar chart (`results/week10/agent_comparison.png`).

## Ethical considerations
- The study logs no personal identifiers. Only timestamps, dialogue IDs, and generated completion codes are stored.
- Warmth/competence/trust sliders are anchored with explicit high/low text so participants know how to interpret the scale.
- Participants may stop at any time; partial responses are not captured because each screen transition saves only after the sliders are submitted and the **Next** button is clicked.
