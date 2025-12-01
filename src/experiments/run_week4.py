"""Week 4 Negotiation Generalization Runner

Runs negotiation experiments across:
- Multiple observer types (lenient, harsh, competence-biased, warmth-biased, simple)
- Environment variants (resources, rounds, stakes tags)
- Opponent strategies (fair, tit-for-tat, concession, unpredictable)

Outputs a flat list of episode-level results with tags for
observer/env/opponent so downstream analysis scripts can compute
Week 4 metrics (generalization, adaptation speed, robustness).
"""
import argparse
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
import numpy as np

from src.utils.config import load_config
from src.envs.negotiation_v1 import NegotiationEnv
from src.observers.simple_observer import SimpleObserver
from src.social.social_score import SocialScoreFactory
from src.agents.agent_factory import AgentFactory


# --- Helper factories for Week 4 conditions ---


def create_observer(observer_type: str, warmth_weight: float, competence_weight: float) -> SimpleObserver:
    """Create different observer variants.

    For now we implement the variants as different weightings and
    sensitivity scalings on top of `SimpleObserver`.
    """
    # Base observer
    base = SimpleObserver(warmth_weight=warmth_weight, competence_weight=competence_weight)

    # Wrap with simple behavioral tweaks via attributes
    if observer_type == "simple":
        return base
    elif observer_type == "lenient":
        # Forgiving: downscale negative deltas, upscale positives
        class LenientObserver(SimpleObserver):
            def observe_action(self, state, action, agent_id):
                w, c = super().observe_action(state, action, agent_id)
                w = 1.2 * max(w, 0) + 0.5 * min(w, 0)
                c = 1.2 * max(c, 0) + 0.5 * min(c, 0)
                return w, c
        return LenientObserver(warmth_weight=warmth_weight, competence_weight=competence_weight)
    elif observer_type == "harsh":
        # Harsh: amplify penalties for selfishness
        class HarshObserver(SimpleObserver):
            def observe_action(self, state, action, agent_id):
                w, c = super().observe_action(state, action, agent_id)
                w = 1.5 * min(w, 0) + 0.8 * max(w, 0)
                c = 1.5 * min(c, 0) + 0.8 * max(c, 0)
                return w, c
        return HarshObserver(warmth_weight=warmth_weight, competence_weight=competence_weight)
    elif observer_type == "competence_biased":
        return SimpleObserver(warmth_weight=0.3, competence_weight=0.7)
    elif observer_type == "warmth_biased":
        return SimpleObserver(warmth_weight=0.8, competence_weight=0.2)
    else:
        raise ValueError(f"Unknown observer_type: {observer_type}")


class OpponentPolicy:
    """Stateless helper implementing different opponent strategies."""

    def __init__(self, policy_type: str, total_resources: int):
        self.policy_type = policy_type
        self.total_resources = total_resources
        self.last_offer_to_opponent = None
        self.round_index = 0

    def reset(self):
        self.last_offer_to_opponent = None
        self.round_index = 0

    def propose(self, state) -> tuple:
        total = state.total_resources
        self.round_index = state.current_turn

        if self.policy_type == "fair":
            offer_self = total // 2
        elif self.policy_type == "tit_for_tat":
            if self.last_offer_to_opponent is None:
                offer_self = total // 2
            else:
                # Mirror what the opponent gave us last time
                offer_self = total - self.last_offer_to_opponent
        elif self.policy_type == "concession":
            # Start greedy, move toward fairness over time
            fraction = max(0, min(1, self.round_index / max(1, state.max_turns - 1)))
            greedy_share = int(0.8 * total)
            fair_share = total // 2
            offer_self = int(greedy_share * (1 - fraction) + fair_share * fraction)
        elif self.policy_type == "unpredictable":
            # Randomly switch between greedy/fair/generous
            mode = np.random.choice(["greedy", "fair", "generous"])
            if mode == "fair":
                offer_self = total // 2
            elif mode == "generous":
                offer_self = int(0.3 * total)
            else:  # greedy
                offer_self = int(0.8 * total)
        else:
            raise ValueError(f"Unknown opponent policy: {self.policy_type}")

        offer_self = max(1, min(total - 1, offer_self))
        return (offer_self, total - offer_self)

    def observe_opponent_action(self, action: tuple, opponent_id: int):
        # Record what the opponent gave us to mirror in tit-for-tat
        self.last_offer_to_opponent = action[1 - opponent_id]


class Week4GeneralizationRunner:
    """Runs Week 4 generalization experiments in negotiation.

    This is intentionally simpler than the Week 3 `AdvancedExperimentRunner`:
    it focuses on tagging conditions cleanly for downstream analysis.
    """

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.agent_factory = AgentFactory()
        self.base_env_cfg = config["environment"]
        self.sweep = config["sweep_parameters"]
        self.bayesian_lambda_values = self.sweep.get("bayesian_lambda_values")
        self.bayesian_prior_strengths = self.sweep.get("bayesian_prior_strengths")
        self.bayesian_prior_adjustments = self.sweep.get("bayesian_prior_adjustments")
        self.bayesian_risk_weights = self.sweep.get("bayesian_risk_weights")
        self.bayesian_lambda_schedules = self.sweep.get("bayesian_lambda_schedules")
        self.social_cfg = config["social_config"]
        self.output_dir = Path(config["output"]["directory"])

    def set_seed(self, seed: int):
        np.random.seed(seed)

    def _build_env(self, variant: Dict[str, Any]) -> NegotiationEnv:
        total = variant.get("total_resources", self.base_env_cfg["total_resources"])
        max_turns = variant.get("max_turns", self.base_env_cfg["max_turns"])
        return NegotiationEnv(total_resources=total, max_turns=max_turns)

    def _build_social_components(self, observer_type: str):
        observer = create_observer(
            observer_type,
            warmth_weight=self.social_cfg["warmth_weight"],
            competence_weight=self.social_cfg["competence_weight"],
        )
        social_score = SocialScoreFactory.create(
            self.social_cfg["score_type"],
            warmth_weight=observer.warmth_weight,
            competence_weight=observer.competence_weight,
        )
        return observer, social_score

    def run_single_episode(
        self,
        agent_type: str,
        lambda_social: float,
        env_variant: Dict[str, Any],
        observer_type: str,
        opponent_type: str,
        seed: int,
        prior_strength: Optional[float] = None,
        prior_adjustment: Optional[float] = None,
        risk_weight: Optional[float] = None,
        lambda_schedule: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        self.set_seed(seed)
        env = self._build_env(env_variant)
        observer, social_score = self._build_social_components(observer_type)

        state = env.reset()

        # Agent0 (our evaluated agent) vs scripted opponent policy
        agent_kwargs: Dict[str, Any] = {}
        if agent_type == "bayesian_mtom":
            if prior_strength is not None:
                agent_kwargs["prior_strength"] = prior_strength
            if prior_adjustment is not None:
                agent_kwargs["adaptive_prior_offset"] = prior_adjustment
            if risk_weight is not None:
                agent_kwargs["risk_weight"] = risk_weight
            if lambda_schedule is not None:
                agent_kwargs["lambda_schedule"] = lambda_schedule
            agent_kwargs["prior_strength"] = prior_strength

        agent0 = self.agent_factory.create(
            agent_type,
            agent_id=0,
            lambda_social=lambda_social,
            **agent_kwargs,
        )

        opponent_policy = OpponentPolicy(policy_type=opponent_type, total_resources=env.total_resources)
        opponent_policy.reset()

        # Simple fixed acceptance behavior for both sides
        def accept_prob(action):
            # More generous offers are more likely to be accepted
            share_for_receiver = action[1]
            ratio = share_for_receiver / env.total_resources
            return 0.2 + 0.8 * ratio

        # Negotiation loop
        while not state.is_terminal() and state.current_turn < state.max_turns:
            if state.current_proposer == 0:
                action = agent0.choose_action(state)
                state = env.step(state, action)

                # Opponent (policy) decides to accept/reject based on what it receives
                if np.random.random() < accept_prob((action[1], action[0])):
                    state = env.accept_offer(state)
                else:
                    state = env.reject_offer(state)

                # Update beliefs for our agent from its own action
                agent0.update_beliefs(state, action, True)
                opponent_policy.observe_opponent_action(action, opponent_id=1)
            else:
                # Opponent proposes according to its policy
                action = opponent_policy.propose(state)
                state = env.step(state, action)

                # Our agent decides to accept or reject
                if np.random.random() < accept_prob(action):
                    state = env.accept_offer(state)
                else:
                    state = env.reject_offer(state)

                opponent_policy.observe_opponent_action(action, opponent_id=0)
                # Our agent updates beliefs based on opponent action
                agent0.update_beliefs(state, action, True)

        # Metrics for agent0
        task_reward = env.get_agent_reward(state, 0)

        # Social perception from agent0's mental state if available
        mental_state = agent0.get_mental_state()
        if mental_state is not None:
            warmth = float(mental_state.warmth)
            competence = float(mental_state.competence)
            social_score_val = float(social_score.compute(mental_state))
        else:
            if state.final_agreement:
                w_delta, c_delta = observer.observe_action(state, state.final_agreement, 0)
                warmth = float(0.5 + 0.3 * w_delta)
                competence = float(0.5 + 0.3 * c_delta)
                temp_ms = type("MS", (object,), {"warmth": warmth, "competence": competence})
                social_score_val = float(social_score.compute(temp_ms))
            else:
                warmth = competence = social_score_val = 0.0

        total_utility = float(task_reward + lambda_social * social_score_val)

        result = {
            "agent_type": agent_type,
            "lambda_social": float(lambda_social),
            "prior_strength": float(prior_strength) if prior_strength is not None else None,
            "prior_adjustment": float(prior_adjustment) if prior_adjustment is not None else None,
            "risk_weight": float(risk_weight) if risk_weight is not None else None,
            "lambda_schedule_label": lambda_schedule.get("label") if lambda_schedule else None,
            "lambda_schedule_start_factor": float(lambda_schedule["start_factor"]) if lambda_schedule else None,
            "lambda_schedule_end_factor": float(lambda_schedule["end_factor"]) if lambda_schedule else None,
            "lambda_schedule_decay_turns": int(lambda_schedule["decay_turns"]) if lambda_schedule else None,
            "observer_type": observer_type,
            "env_name": env_variant.get("name", "base"),
            "env_total_resources": env.total_resources,
            "env_max_turns": env.max_turns,
            "stakes_tag": env_variant.get("stakes", self.base_env_cfg.get("stakes", "unknown")),
            "opponent_type": opponent_type,
            "seed": int(seed),
            "task_reward": float(task_reward),
            "warmth": warmth,
            "competence": competence,
            "social_score": social_score_val,
            "total_utility": total_utility,
            "final_agreement": state.final_agreement,
            "num_turns": state.current_turn,
        }
        return result

    def run(self) -> List[Dict[str, Any]]:
        seeds_per_config = self.config["experiment"]["num_seeds"]
        runs_per_config = self.config["experiment"]["runs_per_config"]

        agent_types = self.sweep["agent_types"]
        lambda_values = self.sweep["lambda_values"]
        observer_types = self.sweep["observer_types"]
        env_variants = self.sweep["env_variants"]
        opponent_types = self.sweep["opponent_types"]

        all_results: List[Dict[str, Any]] = []

        print("🚀 Week 4 Negotiation Generalization")
        print("Agents:", agent_types)
        print("Lambdas:", lambda_values)
        if self.bayesian_lambda_values:
            print("Bayesian lambdas:", self.bayesian_lambda_values)
        if self.bayesian_prior_strengths:
            print("Bayesian priors:", self.bayesian_prior_strengths)
        print("Observers:", observer_types)
        print("Env variants:", [v["name"] for v in env_variants])
        print("Opponents:", opponent_types)
        print("Seeds per config:", seeds_per_config, "Runs per seed:", runs_per_config)
        print("=" * 60)

        for agent_type in agent_types:
            if agent_type == "bayesian_mtom" and self.bayesian_lambda_values:
                lambda_list = self.bayesian_lambda_values
            else:
                lambda_list = lambda_values

            if agent_type == "bayesian_mtom" and self.bayesian_prior_strengths:
                prior_strengths = self.bayesian_prior_strengths
            else:
                prior_strengths = [None]

            if agent_type == "bayesian_mtom" and self.bayesian_prior_adjustments:
                prior_adjustments = self.bayesian_prior_adjustments
            else:
                prior_adjustments = [None]

            if agent_type == "bayesian_mtom" and self.bayesian_risk_weights:
                risk_weights = self.bayesian_risk_weights
            else:
                risk_weights = [None]

            if agent_type == "bayesian_mtom" and self.bayesian_lambda_schedules:
                lambda_schedules = self.bayesian_lambda_schedules
            else:
                lambda_schedules = [None]

            for lambda_val in lambda_list:
                # Only MToM agents should sweep lambda; baselines get lambda=0
                if "baseline" in agent_type or "random" in agent_type:
                    effective_lambda = 0.0
                else:
                    effective_lambda = lambda_val

                for prior_strength in prior_strengths:
                    for prior_adjustment in prior_adjustments:
                        for risk_weight in risk_weights:
                            for lambda_schedule in lambda_schedules:
                                for observer_type in observer_types:
                                    for env_variant in env_variants:
                                        for opponent_type in opponent_types:
                                            for seed_idx in range(seeds_per_config):
                                                seed = 1000 * seed_idx + 7
                                                for run_idx in range(runs_per_config):
                                                    res = self.run_single_episode(
                                                        agent_type=agent_type,
                                                        lambda_social=effective_lambda,
                                                        env_variant=env_variant,
                                                        observer_type=observer_type,
                                                        opponent_type=opponent_type,
                                                        seed=seed + run_idx,
                                                        prior_strength=prior_strength,
                                                        prior_adjustment=prior_adjustment,
                                                        risk_weight=risk_weight,
                                                        lambda_schedule=lambda_schedule,
                                                    )
                                                    all_results.append(res)
        return all_results

    def save_results(self, results: List[Dict[str, Any]]):
        self.output_dir.mkdir(parents=True, exist_ok=True)
        out_path = self.output_dir / "results.jsonl"
        with open(out_path, "w") as f:
            for r in results:
                f.write(json.dumps(r) + "\n")
        print(f"✅ Week 4 generalization results saved to: {out_path}")


def main():
    parser = argparse.ArgumentParser(description="Run Week 4 negotiation generalization experiments")
    parser.add_argument("--config", type=str, required=True, help="Path to config YAML file")
    args = parser.parse_args()

    config = load_config(args.config)
    runner = Week4GeneralizationRunner(config)
    results = runner.run()
    runner.save_results(results)


if __name__ == "__main__":
    main()
