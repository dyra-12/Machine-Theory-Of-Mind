from __future__ import annotations

import json
from pathlib import Path
from statistics import mean
from typing import Dict, List
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.experiments.week7_trace_runner import TraceConfig, run_traceable_episode

LAMBDAS = [0.0, 0.1, 0.2]
SEEDS = [11, 17, 23, 29, 31]
TAU = 1.0  # Effective temperature assumed in the first-order bound
OUTPUT_PATH = Path("results/week7/lambda_validation_summary.json")


def _collect_delta_obs(trace_path: str) -> List[float]:
    with open(trace_path, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    samples: List[float] = []
    for step in data.get("steps", []):
        proposer_flag = step.get("proposer_id")
        agent_flag = step.get("agent_id")
        if proposer_flag == 0 or agent_flag == 0:
            score = step.get("social_score")
            if isinstance(score, (int, float)):
                samples.append(float(score))
    return samples


def main() -> None:
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    baseline_scores: List[float] = []
    baseline_delta_obs: List[float] = []
    rows: List[Dict[str, float]] = []

    for lam in LAMBDAS:
        lambda_scores: List[float] = []
        for seed in SEEDS:
            cfg = TraceConfig(lambda_social=lam, opponent_type="fair")
            info = run_traceable_episode(seed=seed, config=cfg)
            if info["final_social_score"] is not None:
                lambda_scores.append(float(info["final_social_score"]))
            if lam == 0.0:
                baseline_delta_obs.extend(_collect_delta_obs(info["trace_path"]))

        if not lambda_scores:
            raise RuntimeError(f"No social scores recorded for lambda={lam}")

        if lam == 0.0:
            baseline_scores.extend(lambda_scores)

        rows.append({
            "lambda": lam,
            "mean_social_score": float(mean(lambda_scores)),
        })

    base_mean = rows[0]["mean_social_score"]
    var_delta = float(np.var(baseline_delta_obs)) if baseline_delta_obs else float("nan")

    for row in rows:
        lam = row["lambda"]
        predicted = (lam / TAU) * var_delta if np.isfinite(var_delta) else float("nan")
        observed = row["mean_social_score"] - base_mean
        row["delta_social_score"] = observed
        row["predicted_delta"] = predicted

    summary = {
        "seeds": SEEDS,
        "tau_assumption": TAU,
        "var_delta_obs": var_delta,
        "rows": rows,
    }

    OUTPUT_PATH.write_text(json.dumps(summary, indent=2))
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
