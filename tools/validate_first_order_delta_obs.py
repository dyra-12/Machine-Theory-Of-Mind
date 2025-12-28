from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Sequence, Tuple

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.agents.agent_factory import AgentFactory
from src.envs.negotiation_v1 import NegotiationEnv
from src.experiments.week7_trace_runner import OpponentPolicy
from src.models.bayesian_mental_state import BayesianMentalState


@dataclass(frozen=True)
class ValidationConfig:
    agent_type: str = "bayesian_mtom"
    opponent_type: str = "fair"
    total_resources: int = 10
    max_turns: int = 4
    tau: float = 1.0
    epsilon: float = 0.1
    seeds: Tuple[int, ...] = (11, 17, 23, 29, 31)
    delta_samples: int = 400
    belief_update_scale: float = 0.5


def _softmax(logits: np.ndarray) -> np.ndarray:
    logits = np.asarray(logits, dtype=float)
    logits = logits - np.max(logits)
    exps = np.exp(logits)
    z = np.sum(exps)
    if not np.isfinite(z) or z <= 0:
        # Fallback to uniform if degenerate.
        return np.ones_like(exps) / len(exps)
    return exps / z


def _accept_probability(action: Tuple[int, int], receiver_id: int, total: int) -> float:
    ratio = action[receiver_id] / total
    base = 0.2 + 0.75 * ratio
    return float(np.clip(base, 0.05, 0.98))


def _mean(values: Sequence[float]) -> float:
    return float(np.mean(np.asarray(values, dtype=float)))


def _episode_decision_points(
    *,
    seed: int,
    cfg: ValidationConfig,
) -> List[Dict[str, Any]]:
    """Run a single episode at λ=0 to collect decision-point snapshots.

    We only use these snapshots to evaluate action-level Δ_obs(a) and
    construct π_0 and π_ε over actions at the *same* states.

    No episode-averaged social scores or SIQ are used.
    """

    rng_env = np.random.default_rng(seed)
    env = NegotiationEnv(total_resources=cfg.total_resources, max_turns=cfg.max_turns)
    state = env.reset()

    agent = AgentFactory().create(
        cfg.agent_type,
        agent_id=0,
        lambda_social=0.0,
    )

    opponent = OpponentPolicy(cfg.opponent_type, env.total_resources)
    opponent.reset()

    points: List[Dict[str, Any]] = []
    step_index = 0

    while not state.is_terminal() and state.current_turn < cfg.max_turns:
        if state.current_proposer == 0:
            # Snapshot BEFORE taking the action (policy-level quantity).
            ms: BayesianMentalState = agent.mental_state
            points.append(
                {
                    "seed": seed,
                    "turn_index": int(state.current_turn),
                    "step_index": int(step_index),
                    "total_resources": int(state.total_resources),
                    "max_turns": int(state.max_turns),
                    "proposer_id": 0,
                    "warmth_belief": float(ms.warmth_belief),
                    "competence_belief": float(ms.competence_belief),
                    "prior_strength": float(ms.prior_strength),
                    "adaptive_offset": float(getattr(ms, "adaptive_offset", 0.0)),
                }
            )

            # Step environment using the existing agent implementation.
            action = agent.choose_action(state)
            action = (int(action[0]), int(action[1]))
            state = env.step(state, action)
            accept_prob = _accept_probability(action, receiver_id=1, total=env.total_resources)
            accepted = bool(rng_env.random() < accept_prob)
            state = env.accept_offer(state) if accepted else env.reject_offer(state)

            if hasattr(agent, "update_beliefs"):
                agent.update_beliefs(state, action, accepted)

            opponent.observe_opponent_action(action, opponent_id=1)
            step_index += 1
        else:
            action = opponent.propose(state)
            pre_turn = state.current_turn
            state = env.step(state, action)
            accept_prob = _accept_probability(action, receiver_id=0, total=env.total_resources)
            accepted = bool(rng_env.random() < accept_prob)
            state = env.accept_offer(state) if accepted else env.reject_offer(state)

            if hasattr(agent, "update_beliefs"):
                agent.update_beliefs(state, action, accepted)

            opponent.observe_opponent_action(action, opponent_id=0)
            step_index += 1

        if state.final_agreement is not None:
            break

    return points


def _compute_decision_stats(
    *,
    point: Dict[str, Any],
    cfg: ValidationConfig,
    rng: np.random.Generator,
) -> Dict[str, Any]:
    total = int(point["total_resources"])

    # Reconstruct a Bayesian belief state snapshot.
    ms = BayesianMentalState(
        prior_strength=float(point["prior_strength"]),
        adaptive_offset=float(point.get("adaptive_offset", 0.0)),
    )
    ms.warmth_belief = float(point["warmth_belief"])
    ms.competence_belief = float(point["competence_belief"])

    # Enumerate all offers to self (1..total-1). This matches the env's action space.
    offers_self = list(range(1, total))

    # Action-level Δ_obs(a): expected social response for each action.
    # IMPORTANT: expected_delta_obs performs *no clipping/normalization* of Δ_obs.
    scorer = AgentFactory().create(cfg.agent_type, agent_id=0, lambda_social=0.0).social_scorer
    delta_obs = np.array(
        [
            scorer.expected_delta_obs(
                offer,
                ms,
                total_resources=total,
                update_scale=cfg.belief_update_scale,
                n_samples=cfg.delta_samples,
                rng=rng,
            )
            for offer in offers_self
        ],
        dtype=float,
    )

    # Base reward R(a): self share fraction.
    task_reward = np.array([offer / total for offer in offers_self], dtype=float)

    # Policies π_0 and π_ε.
    logits0 = (task_reward + 0.0 * delta_obs) / float(cfg.tau)
    logits_eps = (task_reward + float(cfg.epsilon) * delta_obs) / float(cfg.tau)

    pi0 = _softmax(logits0)
    pieps = _softmax(logits_eps)

    mean_pi0 = float(np.sum(pi0 * delta_obs))
    second_pi0 = float(np.sum(pi0 * (delta_obs**2)))
    var_pi0 = float(max(0.0, second_pi0 - mean_pi0**2))

    mean_pieps = float(np.sum(pieps * delta_obs))

    return {
        **point,
        "mean_pi0": mean_pi0,
        "second_pi0": second_pi0,
        "var_pi0": var_pi0,
        "mean_pieps": mean_pieps,
    }


def _markdown_summary_table(
    *,
    tau: float,
    var_pi0: float,
    predicted_slope: float,
    observed_slope: float,
    rel_err_pct: float,
) -> str:
    rows = [
        ("τ (temperature)", f"{tau:.6g}"),
        ("Var₍π₀₎(Δ_obs)", f"{var_pi0:.6g}"),
        ("Predicted slope (Var / τ)", f"{predicted_slope:.6g}"),
        ("Observed slope (finite diff)", f"{observed_slope:.6g}"),
        ("Relative error (%)", f"{rel_err_pct:.6g}"),
    ]

    lines = ["| Quantity | Value |", "|---|---:|"]
    lines.extend([f"| {k} | {v} |" for k, v in rows])
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Validate the first-order small-λ result using action-level Δ_obs(a) only. "
            "Prints ONLY a summary table."
        )
    )
    parser.add_argument("--epsilon", type=float, default=0.1)
    parser.add_argument("--tau", type=float, default=1.0)
    parser.add_argument("--seeds", type=int, nargs="*", default=[11, 17, 23, 29, 31])
    parser.add_argument("--total-resources", type=int, default=10)
    parser.add_argument("--max-turns", type=int, default=4)
    parser.add_argument("--delta-samples", type=int, default=400)
    parser.add_argument("--belief-update-scale", type=float, default=0.5)
    parser.add_argument(
        "--output-json",
        type=str,
        default="results/week7/first_order_delta_obs_validation.json",
        help="Optional path to write the full per-decision breakdown JSON.",
    )
    args = parser.parse_args()

    cfg = ValidationConfig(
        total_resources=int(args.total_resources),
        max_turns=int(args.max_turns),
        tau=float(args.tau),
        epsilon=float(args.epsilon),
        seeds=tuple(int(s) for s in args.seeds),
        delta_samples=int(args.delta_samples),
        belief_update_scale=float(args.belief_update_scale),
    )

    rng = np.random.default_rng(12345)

    decision_points: List[Dict[str, Any]] = []
    for seed in cfg.seeds:
        decision_points.extend(_episode_decision_points(seed=seed, cfg=cfg))

    per_decision: List[Dict[str, Any]] = [
        _compute_decision_stats(point=p, cfg=cfg, rng=rng) for p in decision_points
    ]

    var_list = [d["var_pi0"] for d in per_decision]
    obs_slope_list = [
        (d["mean_pieps"] - d["mean_pi0"]) / float(cfg.epsilon) for d in per_decision
    ]

    var_pi0 = _mean(var_list) if var_list else float("nan")
    predicted_slope = var_pi0 / float(cfg.tau) if np.isfinite(var_pi0) else float("nan")
    observed_slope = _mean(obs_slope_list) if obs_slope_list else float("nan")

    rel_err_pct = float("nan")
    if np.isfinite(predicted_slope) and predicted_slope != 0 and np.isfinite(observed_slope):
        rel_err_pct = (observed_slope - predicted_slope) / predicted_slope * 100.0

    payload = {
        "config": {
            "agent_type": cfg.agent_type,
            "opponent_type": cfg.opponent_type,
            "total_resources": cfg.total_resources,
            "max_turns": cfg.max_turns,
            "tau": cfg.tau,
            "epsilon": cfg.epsilon,
            "seeds": list(cfg.seeds),
            "delta_samples": cfg.delta_samples,
            "belief_update_scale": cfg.belief_update_scale,
        },
        "var_pi0_delta_obs": var_pi0,
        "tau": cfg.tau,
        "predicted_slope": predicted_slope,
        "observed_slope": observed_slope,
        "relative_error_percent": rel_err_pct,
        "num_decision_points": len(per_decision),
        "per_decision": [
            {
                "seed": d["seed"],
                "turn_index": d["turn_index"],
                "step_index": d["step_index"],
                "mean_pi0": d["mean_pi0"],
                "second_pi0": d["second_pi0"],
                "mean_pieps": d["mean_pieps"],
            }
            for d in per_decision
        ],
    }

    if args.output_json:
        out_path = Path(args.output_json)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    # Print ONLY the requested table.
    print(
        _markdown_summary_table(
            tau=cfg.tau,
            var_pi0=var_pi0,
            predicted_slope=predicted_slope,
            observed_slope=observed_slope,
            rel_err_pct=rel_err_pct,
        )
    )


if __name__ == "__main__":
    main()
