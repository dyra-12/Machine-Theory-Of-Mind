"""Week 7 traceable negotiation episode runner.

This helper runs a single negotiation episode between the agent under test
(agent 0) and a scripted opponent policy while capturing detailed traces of
how the agent's beliefs evolve after every action. Each trace entry also
includes the social score computed from the agent's current mental state.
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional, Sequence, Tuple

import numpy as np

from src.agents.agent_factory import AgentFactory
from src.envs.negotiation_v1 import NegotiationEnv
from src.models.mental_states import MentalState
from src.observers.simple_observer import SimpleObserver
from src.social.social_score import SocialScoreFactory
from src.utils import TraceLogger

TRACE_OUTPUT_DIR = Path("results/week7/traces")


@dataclass
class TraceConfig:
    agent_type: str = "bayesian_mtom"
    opponent_type: str = "fair"
    lambda_social: float = 0.9
    total_resources: int = 10
    max_turns: int = 4
    seed: int = 7
    observer_warmth_weight: float = 0.6
    observer_competence_weight: float = 0.4
    social_score_type: str = "linear"


class OpponentPolicy:
    """Stateless helper implementing a few scripted opponent behaviors."""

    def __init__(self, policy_type: str, total_resources: int):
        self.policy_type = policy_type
        self.total_resources = total_resources
        self.last_offer_to_opponent = None
        self.round_index = 0

    def reset(self) -> None:
        self.last_offer_to_opponent = None
        self.round_index = 0

    def propose(self, state) -> Tuple[int, int]:
        total = state.total_resources
        self.round_index = state.current_turn

        if self.policy_type == "fair":
            offer_self = total // 2
        elif self.policy_type == "tit_for_tat":
            if self.last_offer_to_opponent is None:
                offer_self = total // 2
            else:
                offer_self = total - self.last_offer_to_opponent
        elif self.policy_type == "concession":
            fraction = max(0.0, min(1.0, self.round_index / max(1, state.max_turns - 1)))
            greedy_share = int(0.8 * total)
            fair_share = total // 2
            offer_self = int(greedy_share * (1 - fraction) + fair_share * fraction)
        elif self.policy_type == "greedy":
            offer_self = int(0.8 * total)
        elif self.policy_type == "generous":
            offer_self = int(0.3 * total)
        else:
            raise ValueError(f"Unknown opponent policy: {self.policy_type}")

        offer_self = max(1, min(total - 1, offer_self))
        return (total - offer_self, offer_self)

    def observe_opponent_action(self, action: Tuple[int, int], opponent_id: int) -> None:
        self.last_offer_to_opponent = action[1 - opponent_id]


def run_traceable_episode(
    *,
    seed: int = 7,
    config: Optional[TraceConfig] = None,
    agent_kwargs: Optional[Dict[str, Any]] = None,
    opponent_kwargs: Optional[Dict[str, Any]] = None,
    output_dir: Path = TRACE_OUTPUT_DIR,
) -> Dict[str, Any]:
    """Run a single negotiation episode and persist the full trace.

    Args:
        seed: Random seed for stochastic acceptance decisions.
        config: Optional high-level configuration; falls back to defaults.
        agent_kwargs: Extra parameters forwarded to the agent factory.
        opponent_kwargs: Extra overrides for the scripted opponent.
        output_dir: Directory where trace files will be written.

    Returns:
        Dict containing the episode ID, output path, and final metrics.
    """

    cfg = config or TraceConfig()
    agent_kwargs = agent_kwargs.copy() if agent_kwargs else {}
    opponent_kwargs = opponent_kwargs.copy() if opponent_kwargs else {}

    rng = np.random.default_rng(seed)
    env = NegotiationEnv(total_resources=cfg.total_resources, max_turns=cfg.max_turns)
    state = env.reset()

    agent_factory = AgentFactory()
    agent = agent_factory.create(
        cfg.agent_type,
        agent_id=0,
        lambda_social=cfg.lambda_social,
        **agent_kwargs,
    )

    opponent_policy_name = cfg.opponent_type
    scripted_opponent = OpponentPolicy(opponent_policy_name, env.total_resources)
    scripted_opponent.reset()

    observer = SimpleObserver(
        warmth_weight=cfg.observer_warmth_weight,
        competence_weight=cfg.observer_competence_weight,
    )
    social_score = SocialScoreFactory.create(
        cfg.social_score_type,
        warmth_weight=observer.warmth_weight,
        competence_weight=observer.competence_weight,
    )

    episode_id = _generate_episode_id()
    logger = TraceLogger(
        episode_id=episode_id,
        output_dir=output_dir,
        metadata={
            "seed": seed,
            "agent_type": cfg.agent_type,
            "lambda_social": cfg.lambda_social,
            "opponent_policy": opponent_policy_name,
            "total_resources": cfg.total_resources,
            "max_turns": cfg.max_turns,
        },
    )

    step_count = 0
    while not state.is_terminal() and state.current_turn < cfg.max_turns:
        if state.current_proposer == 0:
            action = _ensure_action(agent.choose_action(state))
            pre_turn = state.current_turn
            state = env.step(state, action)
            accept_prob = _accept_probability(action, receiver_id=1, total=env.total_resources)
            accepted = bool(rng.random() < accept_prob)
            state = env.accept_offer(state) if accepted else env.reject_offer(state)

            if hasattr(agent, "update_beliefs"):
                agent.update_beliefs(state, action, accepted)

            social_score_val, belief_source = _social_score_for_agent(
                agent,
                social_score,
                observer,
                state,
                action,
                acting_agent_id=0,
            )
            beliefs_snapshot = _safe_get_beliefs(agent)

            logger.log_step(
                turn_index=pre_turn,
                proposer_id=0,
                action=action,
                accepted=accepted,
                mental_state=beliefs_snapshot,
                social_score=social_score_val,
                notes={
                    "accept_prob": accept_prob,
                    "belief_source": belief_source,
                    "phase": "agent_action",
                },
            )
            step_count += 1
            scripted_opponent.observe_opponent_action(action, opponent_id=1)
        else:
            action = scripted_opponent.propose(state)
            pre_turn = state.current_turn
            state = env.step(state, action)
            accept_prob = _accept_probability(action, receiver_id=0, total=env.total_resources)
            accepted = bool(rng.random() < accept_prob)
            state = env.accept_offer(state) if accepted else env.reject_offer(state)

            if hasattr(agent, "update_beliefs"):
                agent.update_beliefs(state, action, accepted)

            social_score_val, belief_source = _social_score_for_agent(
                agent,
                social_score,
                observer,
                state,
                action,
                acting_agent_id=1,
            )
            beliefs_snapshot = _safe_get_beliefs(agent)

            logger.log_step(
                turn_index=pre_turn,
                proposer_id=1,
                action=action,
                accepted=accepted,
                mental_state=beliefs_snapshot,
                social_score=social_score_val,
                notes={
                    "accept_prob": accept_prob,
                    "belief_source": belief_source,
                    "phase": "opponent_action",
                },
            )
            step_count += 1
            scripted_opponent.observe_opponent_action(action, opponent_id=0)

        if state.final_agreement is not None:
            break

    task_reward = env.get_agent_reward(state, agent_id=0)
    final_beliefs = _safe_get_beliefs(agent)
    final_social_score, belief_source = _social_score_for_agent(
        agent,
        social_score,
        observer,
        state,
        state.final_agreement if state.final_agreement else state.get_latest_offer(),
        acting_agent_id=state.current_proposer,
    )
    total_utility = (
        float(task_reward)
        + float(cfg.lambda_social) * final_social_score
        if final_social_score is not None
        else float(task_reward)
    )

    outcome = {
        "final_agreement": state.final_agreement,
        "num_turns": state.current_turn,
        "task_reward": task_reward,
        "final_social_score": final_social_score,
        "total_utility": total_utility,
        "belief_source": belief_source,
        "steps_recorded": step_count,
    }
    logger.set_outcome(outcome)
    trace_path = logger.close()

    return {
        "episode_id": episode_id,
        "trace_path": str(trace_path),
        "final_agreement": state.final_agreement,
        "task_reward": task_reward,
        "final_social_score": final_social_score,
        "total_utility": total_utility,
        "steps_recorded": step_count,
        "final_beliefs": final_beliefs,
    }


def _generate_episode_id() -> str:
    token = uuid.uuid4().hex[:6]
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    return f"trace_{timestamp}_{token}"


def _ensure_action(action: Sequence[int]) -> Tuple[int, int]:
    if len(action) != 2:
        raise ValueError("Negotiation action must be a length-2 sequence")
    return (int(action[0]), int(action[1]))


def _accept_probability(action: Tuple[int, int], receiver_id: int, total: int) -> float:
    ratio = action[receiver_id] / total
    base = 0.2 + 0.75 * ratio
    return float(np.clip(base, 0.05, 0.98))


def _safe_get_beliefs(agent: Any) -> Optional[Any]:
    getter = getattr(agent, "get_mental_state", None)
    if callable(getter):
        return getter()
    return None


def _social_score_for_agent(
    agent: Any,
    scorer,
    observer: SimpleObserver,
    state,
    action: Optional[Tuple[int, int]],
    *,
    acting_agent_id: int,
) -> Tuple[Optional[float], str]:
    beliefs = _safe_get_beliefs(agent)
    ms = _to_mental_state(beliefs)
    if ms is not None:
        try:
            return float(scorer.compute(ms)), "agent"
        except Exception:
            pass

    fallback_ms = _project_from_action(observer, state, action, acting_agent_id)
    if fallback_ms is not None:
        return float(scorer.compute(fallback_ms)), "fallback"
    return None, "missing"


def _to_mental_state(beliefs: Optional[Any]) -> Optional[MentalState]:
    if beliefs is None:
        return None
    if isinstance(beliefs, MentalState):
        return beliefs
    warmth = _maybe_get_attr(beliefs, "warmth")
    competence = _maybe_get_attr(beliefs, "competence")
    if warmth is None or competence is None:
        return None
    return MentalState(warmth=float(warmth), competence=float(competence))


def _maybe_get_attr(obj: Any, key: str) -> Optional[float]:
    if isinstance(obj, dict):
        value = obj.get(key)
    else:
        value = getattr(obj, key, None)
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _project_from_action(
    observer: SimpleObserver,
    state,
    action: Optional[Tuple[int, int]],
    agent_id: int,
) -> Optional[MentalState]:
    if action is None:
        return None
    try:
        w_delta, c_delta = observer.observe_action(state, action, agent_id)
    except Exception:
        return None
    warmth = float(np.clip(0.5 + 0.3 * w_delta, 0.0, 1.0))
    competence = float(np.clip(0.5 + 0.3 * c_delta, 0.0, 1.0))
    return MentalState(warmth=warmth, competence=competence)