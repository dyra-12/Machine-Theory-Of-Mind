"""Streamlit dashboard for Week 7 negotiation traces.

The app loads saved trace JSON files (results/week7/traces) and provides:
- Episode selection and metadata display
- Step-by-step playback controls
- Belief trajectory visualization
- Social score timeline and action table

Run with: `streamlit run demo/trace_dashboard.py`
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List

import pandas as pd
import streamlit as st
import altair as alt

TRACE_DIR = Path("results/week7/traces")


@st.cache_data(show_spinner=False)
def list_traces() -> List[Path]:
    TRACE_DIR.mkdir(parents=True, exist_ok=True)
    return sorted(TRACE_DIR.glob("*.json"))


@st.cache_data(show_spinner=False)
def load_trace(trace_path: str) -> Dict:
    path = Path(trace_path)
    if not path.exists():
        raise FileNotFoundError(f"Trace file not found: {trace_path}")
    with path.open() as fh:
        return json.load(fh)


def to_dataframe(trace: Dict) -> pd.DataFrame:
    steps = trace.get("steps", [])
    if not steps:
        return pd.DataFrame()
    df = pd.json_normalize(steps)
    # Rename useful columns for clarity
    rename_map = {
        "beliefs.warmth": "warmth",
        "beliefs.competence": "competence",
        "beliefs.warmth_uncertainty": "warmth_uncertainty",
        "beliefs.competence_uncertainty": "competence_uncertainty",
        "action.0": "agent0_share",
        "action.1": "agent1_share",
    }
    df = df.rename(columns=rename_map)
    # Ensure numeric types where possible
    numeric_cols = [
        "turn",
        "agent_id",
        "warmth",
        "competence",
        "warmth_uncertainty",
        "competence_uncertainty",
        "social_score",
        "agent0_share",
        "agent1_share",
    ]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


def render_episode_metadata(trace: Dict):
    meta = trace.get("metadata", {})
    outcome = trace.get("outcome", {})
    cols = st.columns(2)
    with cols[0]:
        st.subheader("Metadata")
        st.json(meta)
    with cols[1]:
        st.subheader("Outcome")
        st.json(outcome)


def render_belief_chart(df: pd.DataFrame):
    if df.empty or not {"turn", "warmth", "competence"}.issubset(df.columns):
        st.info("No belief data available for this trace.")
        return
    melted = df.melt(
        id_vars=["turn"],
        value_vars=["warmth", "competence"],
        var_name="belief",
        value_name="value",
    )
    chart = (
        alt.Chart(melted)
        .mark_line(point=True)
        .encode(
            x="turn:Q",
            y=alt.Y("value:Q", scale=alt.Scale(domain=[0, 1])),
            color="belief:N",
            tooltip=["turn", "belief", "value"],
        )
        .properties(height=300)
    )
    st.altair_chart(chart, width="stretch")


def render_social_score_chart(df: pd.DataFrame):
    if df.empty or "social_score" not in df.columns:
        return
    chart = (
        alt.Chart(df)
        .mark_line(point=True, color="orange")
        .encode(
            x="turn:Q",
            y="social_score:Q",
            tooltip=["turn", "social_score"],
        )
        .properties(height=200)
    )
    st.altair_chart(chart, width="stretch")


def render_step_details(df: pd.DataFrame, idx: int):
    if df.empty:
        st.warning("No steps in this trace.")
        return
    step = df.iloc[idx].fillna("—")
    st.markdown(f"### Step {idx} — Turn {int(step['turn'])} (Agent {int(step['agent_id'])})")
    cols = st.columns(2)
    with cols[0]:
        st.write({
            "Action": [step.get("agent0_share", "?"), step.get("agent1_share", "?")],
            "Accepted": step.get("accepted"),
            "Social Score": step.get("social_score"),
        })
    with cols[1]:
        st.write({
            "Warmth": step.get("warmth"),
            "Competence": step.get("competence"),
            "Warmth σ": step.get("warmth_uncertainty"),
            "Competence σ": step.get("competence_uncertainty"),
        })
    notes = step.get("notes")
    if notes:
        st.caption(f"Notes: {notes}")


def main():
    st.set_page_config(page_title="Week 7 Negotiation Dashboard", layout="wide")
    st.title("🧠 Week 7 Negotiation Playback")
    st.markdown("Navigate recorded negotiation traces and inspect belief dynamics.")

    trace_files = list_traces()
    if not trace_files:
        st.error("No trace files found. Run `python experiments/run_trace_sweep.py` first.")
        return

    with st.sidebar:
        st.header("Trace Selection")
        options = {p.name: p for p in trace_files}
        selected = st.selectbox("Choose an episode", options=list(options.keys()))
        if st.button("Refresh traces"):
            list_traces.clear()
            load_trace.clear()
            st.experimental_rerun()

    trace = load_trace(str(options[selected]))
    df = to_dataframe(trace)

    render_episode_metadata(trace)

    if not df.empty:
        max_step = len(df) - 1
        step_idx = st.slider("Step index", 0, max_step, value=0)
        render_step_details(df, step_idx)
    else:
        st.warning("Trace has no steps to display.")

    st.subheader("Belief Trajectory")
    render_belief_chart(df)

    st.subheader("Social Score Timeline")
    render_social_score_chart(df)

    st.subheader("All Steps")
    st.dataframe(
        df[[
            "turn",
            "agent_id",
            "agent0_share",
            "agent1_share",
            "accepted",
            "warmth",
            "competence",
            "social_score",
        ]]
        if not df.empty
        else df
    )

    with st.expander("Raw trace JSON"):
        st.json(trace)


if __name__ == "__main__":
    main()
