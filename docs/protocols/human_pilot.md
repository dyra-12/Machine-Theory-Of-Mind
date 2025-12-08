# Human Pilot Protocol — Reproducibility & Ethics

This document describes the human-pilot study used to validate perceptual
effects of Machine Theory of Mind (MToM) agents and provides the information
needed for reproducibility and ethical transparency.

## Study goal

The goal of this pilot is to evaluate whether agents endowed with a Machine
Theory of Mind (MToM) are perceived differently than non-MToM baseline
agents on social attributes. Primary outcomes are participant ratings of
Warmth, Competence, and Trust for short negotiation dialogue snippets produced
by different agent types.

## Design

- Stimuli: 12 short negotiation dialogue snippets (6 produced by MToM agents,
  6 produced by baseline agents). Dialogue text is stored in
  `data/human_pilot/dialogues.json` and randomized per participant session.
- Rating scales: For each dialogue, participants rated the agent on three
  7-point Likert scales (1 = lowest, 7 = highest):
  - Warmth
  - Competence
  - Trust
- Randomization: Dialogue order is randomized per participant to control for
  order effects. Agent assignment within dialogues is predetermined in the
  stimulus file and counterbalanced across the set of stimuli.

## Participants

- Target sample size: **N = 25** participants for the initial pilot snapshot. The protocol is written to support additional recruitment in follow-up studies if needed.
- Recruitment channel: Prolific (or equivalent crowdsourcing platform).
- Inclusion criteria:
  - Age 18 or older.
  - Fluent English reading comprehension.
  - No prior participation in the study (first-time participants only).
  - Located in countries approved by the institution's human-subjects
    guidelines (where applicable).

## Procedure

1. Participants arrive at the Gradio web interface (`demo/human_pilot_app.py`).
2. They are presented with the consent text (exact wording below) and must
   acknowledge consent to proceed.
3. The session presents 12 dialogues in a randomized order; for each dialogue
   the participant slides three sliders (Warmth, Competence, Trust) and then
   advances to the next item.
4. Average completion time is approximately 7 minutes (monitored during data
   collection). Participants may stop at any time; only completed sessions are
   appended to `data/human_pilot/pilot_ratings.csv`.

## Consent text (exact wording)

Please read the following carefully. Participation is voluntary.

"You are invited to take part in a short research study about how people
perceive conversational agents. Participation involves reading 12 short
dialogues and rating each on three short scales (Warmth, Competence, Trust).
You will not be asked for your name, email, or any other personally
identifying information. Your responses are anonymous and stored with a
random completion code and a UTC timestamp. The task takes about 7 minutes.
Participation is voluntary and you may withdraw at any time before
submitting your responses. By clicking 'I consent' you confirm that you are
at least 18 years old, you consent to anonymous use of your ratings for
research and publication purposes, and you understand that no identifying
information will be collected or published."

Participants must click an explicit **I consent** button to continue.

## Data handling

- Storage: Only anonymized responses (slider values, dialogue id, agent type,
  completion code, UTC timestamp) are stored in `data/human_pilot/pilot_ratings.csv`.
- No personally identifying information (names, e-mails, IP addresses) are
  collected or stored in the published dataset.
- No free-text responses that could contain identifying information are
  retained in the published dataset.
- Access: Raw live-collection files are treated as internal artifacts. Public
  snapshots and aggregated summaries are stored in `results/week10/` and are
  published under **CC-BY-NC 4.0** (see `data/human_pilot/README.md`).

## IRB statement

This pilot is classified as **Exempt** under our internal guidance, because it
collects only anonymized perceptual ratings and does not solicit or record
clinical, sensitive, or identifying personal data. No clinical interventions
or medically sensitive questions are included. If the study is extended to
clinical populations or to collect identifiable personal data, we commit to
obtaining Institutional Review Board (IRB) / Research Ethics Committee
approval prior to data collection.

---

If you have questions about the protocol, please open an issue on the project
GitHub or contact the maintainers listed in the repository metadata.
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
