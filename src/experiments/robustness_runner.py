"""Robustness experiment suite covering noisy channels, domain shifts, and mixed opponents."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List, Optional
import numpy as np

from src.utils.config import load_config
from src.envs.negotiation_v1 import NegotiationEnv
from src.observers.simple_observer import SimpleObserver
from src.observers.adversarial_observer import AdversarialObserver
from src.social.social_score import SocialScoreFactory
from src.agents.agent_factory import AgentFactory
from src.experiments.run_week4 import OpponentPolicy


class MixedOpponentPolicy:
    """Opponent that samples from multiple scripted strategies within an episode."""

    def __init__(self, pool: List[str], total_resources: int, seed: Optional[int] = None):
        if not pool:
            raise ValueError("MixedOpponentPolicy requires at least one policy in the pool")
        self.pool = pool
        self.total_resources = total_resources
        self._rng = np.random.default_rng(seed)
        self._policies = [OpponentPolicy(policy_type=p, total_resources=total_resources) for p in pool]

    def reset(self):
        for policy in self._policies:
            policy.reset()

    def propose(self, state) -> tuple:
        policy = self._rng.choice(self._policies)
        return policy.propose(state)

    def observe_opponent_action(self, action: tuple, opponent_id: int):
        for policy in self._policies:
            policy.observe_opponent_action(action, opponent_id)


class RobustnessExperimentRunner:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.agent_factory = AgentFactory()
        self.output_dir = Path(config["output"]["directory"])
        self.environment = config["environment"]
        self.channels = config["channels"]
        self.domain_shifts = config["domain_shifts"]
        self.opponent_cfg = config["opponents"]
        self.agent_cfg = config["agents"]
        self.exp_cfg = config["experiment"]
        self.social_cfg = config["social_config"]

    def _build_env(self, variant: Dict[str, Any]) -> NegotiationEnv:
        total = variant.get("total_resources", self.environment["total_resources"])
        max_turns = variant.get("max_turns", self.environment["max_turns"])
        return NegotiationEnv(total_resources=total, max_turns=max_turns)

    def _build_observer(self, channel_profile: Dict[str, Any]):
        params = channel_profile.get("params", {})
        if channel_profile["type"] == "adversarial":
            return AdversarialObserver(
                warmth_weight=self.social_cfg["warmth_weight"],
                competence_weight=self.social_cfg["competence_weight"],
                **params,
            )
        return SimpleObserver(
            warmth_weight=self.social_cfg["warmth_weight"],
            competence_weight=self.social_cfg["competence_weight"],
        )

    def _build_social_score(self, observer: SimpleObserver):
        return SocialScoreFactory.create(
            self.social_cfg["score_type"],
            warmth_weight=observer.warmth_weight,
            competence_weight=observer.competence_weight,
        )

    def _build_opponent(self, profile: Dict[str, Any], env: NegotiationEnv):
        mode = profile["mode"]
        if mode == "mixed":
            return MixedOpponentPolicy(profile["pool"], env.total_resources)
        return OpponentPolicy(policy_type=profile["policy"], total_resources=env.total_resources)

    def _iter_opponent_profiles(self) -> List[Dict[str, Any]]:
        profiles: List[Dict[str, Any]] = []
        for pure in self.opponent_cfg.get("pure_types", []):
            profiles.append({"mode": "pure", "name": pure, "policy": pure})
        for mix in self.opponent_cfg.get("mixes", []):
            profiles.append({"mode": "mixed", "name": mix["name"], "pool": mix["pool"]})
        return profiles

    def _accept_prob(self, action: tuple, env: NegotiationEnv) -> float:
        share_for_receiver = action[1]
        ratio = share_for_receiver / env.total_resources
        return 0.2 + 0.8 * ratio

    def run_episode(
        self,
        agent_type: str,
        lambda_social: float,
        env_variant: Dict[str, Any],
        channel_profile: Dict[str, Any],
        opponent_profile: Dict[str, Any],
        seed: int,
        prior_strength: Optional[float] = None,
    ) -> Dict[str, Any]:
        np.random.seed(seed)
        env = self._build_env(env_variant)
        observer = self._build_observer(channel_profile)
        social_score = self._build_social_score(observer)
        channel_meta = observer.describe_channel()
        channel_meta.setdefault("type", channel_profile["type"])
        channel_meta["profile"] = channel_profile["name"]

        agent_kwargs: Dict[str, Any] = {}
        if agent_type == "bayesian_mtom":
            if prior_strength is not None:
                agent_kwargs["prior_strength"] = prior_strength
            if "cultural_template" in self.agent_cfg:
                agent_kwargs["cultural_template"] = self.agent_cfg["cultural_template"]
        agent = self.agent_factory.create(
            agent_type,
            agent_id=0,
            lambda_social=lambda_social,
            **agent_kwargs,
        )

        opponent = self._build_opponent(opponent_profile, env)
        opponent.reset()

        state = env.reset()

        while not state.is_terminal() and state.current_turn < env.max_turns:
            if state.current_proposer == 0:
                action = agent.choose_action(state)
                feedback = observer.observe_action(state, action, agent_id=0)
                state = env.step(state, action)

                if np.random.random() < self._accept_prob((action[1], action[0]), env):
                    state = env.accept_offer(state)
                else:
                    state = env.reject_offer(state)

                agent.update_beliefs(
                    state,
                    action,
                    True,
                    observer_feedback=feedback,
                    feedback_reliability=getattr(observer, "reliability", 1.0),
                )
                opponent.observe_opponent_action(action, opponent_id=1)
            else:
                action = opponent.propose(state)
                state = env.step(state, action)

                if np.random.random() < self._accept_prob(action, env):
                    state = env.accept_offer(state)
                else:
                    state = env.reject_offer(state)

                opponent.observe_opponent_action(action, opponent_id=0)
                agent.update_beliefs(state, action, True)

        task_reward = env.get_agent_reward(state, 0)
        mental_state = agent.get_mental_state()
        if mental_state is not None:
            warmth = float(mental_state.warmth)
            competence = float(mental_state.competence)
            social_val = float(social_score.compute(mental_state))
        else:
            warmth = competence = social_val = 0.0

        return {
            "agent_type": agent_type,
            "lambda_social": lambda_social,
            "prior_strength": prior_strength,
            "channel": channel_meta,
            "domain": env_variant["name"],
            "opponent": opponent_profile["name"],
            "task_reward": task_reward,
            "warmth": warmth,
            "competence": competence,
            "social_score": social_val,
            "total_utility": task_reward + lambda_social * social_val,
            "final_agreement": state.final_agreement,
            "num_turns": state.current_turn,
        }

    def run(self) -> List[Dict[str, Any]]:
        results: List[Dict[str, Any]] = []
        lambda_values = self.agent_cfg["lambda_social"]
        prior_strengths = self.agent_cfg.get("bayesian_prior_strengths", [None])
        seeds = self.exp_cfg["num_seeds"]
        runs_per_seed = self.exp_cfg["runs_per_config"]

        for channel in self.channels:
            for domain in self.domain_shifts:
                env_variant = {**self.environment, **domain}
                opponent_profiles = self._iter_opponent_profiles()
                for opponent_profile in opponent_profiles:
                    for agent_type in self.agent_cfg["types"]:
                        priors = prior_strengths if agent_type == "bayesian_mtom" else [None]
                        for lambda_val in lambda_values:
                            for prior_strength in priors:
                                for seed_idx in range(seeds):
                                    base_seed = 100 * seed_idx + 42
                                    for run_idx in range(runs_per_seed):
                                        result = self.run_episode(
                                            agent_type=agent_type,
                                            lambda_social=lambda_val,
                                            env_variant=env_variant,
                                            channel_profile=channel,
                                            opponent_profile=opponent_profile,
                                            seed=base_seed + run_idx,
                                            prior_strength=prior_strength,
                                        )
                                        result["seed"] = base_seed + run_idx
                                        result["run_idx"] = run_idx
                                        results.append(result)
        return results

    def save_results(self, results: List[Dict[str, Any]]):
        self.output_dir.mkdir(parents=True, exist_ok=True)
        out_path = self.output_dir / "robustness_results.jsonl"
        with open(out_path, "w") as fh:
            for record in results:
                fh.write(json.dumps(record) + "\n")
        print(f"✅ Robustness results written to {out_path}")


def main():
    parser = argparse.ArgumentParser(description="Run noisy-channel/domain-shift robustness experiments")
    parser.add_argument("--config", required=True, help="Path to robustness suite YAML config")
    args = parser.parse_args()

    config = load_config(args.config)
    runner = RobustnessExperimentRunner(config)
    results = runner.run()
    runner.save_results(results)


if __name__ == "__main__":
    main()
