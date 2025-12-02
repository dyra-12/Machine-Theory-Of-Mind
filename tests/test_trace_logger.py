import json
import sys
from pathlib import Path

# Ensure project root is on sys.path for pytest runs
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.experiments.week7_trace_runner import run_traceable_episode


def test_trace_logger_writes_beliefs_and_social_score(tmp_path):
    # Run a single episode with output directed to a temp dir
    outdir = tmp_path / "traces"
    info = run_traceable_episode(seed=123, output_dir=outdir)
    trace_path = Path(info["trace_path"])
    assert trace_path.exists(), "Trace file should be created"

    data = json.load(trace_path.open())
    assert "steps" in data and isinstance(data["steps"], list)
    assert len(data["steps"]) >= 1

    for step in data["steps"]:
        # Each step must include beliefs with warmth/competence and a social_score
        beliefs = step.get("beliefs")
        assert beliefs is not None, "Beliefs snapshot missing for a step"
        assert "warmth" in beliefs and "competence" in beliefs
        assert step.get("social_score") is not None

    # outcome should contain final_social_score
    outcome = data.get("outcome")
    assert outcome is not None
    assert "final_social_score" in outcome
