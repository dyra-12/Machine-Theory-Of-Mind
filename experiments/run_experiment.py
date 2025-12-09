"""Unified experiment entrypoint.

This script dispatches to the appropriate experiment runner based on the
provided YAML config. It currently supports:

- Week 4 / Week 5 style negotiation generalization and Bayesian sweeps
  (via ``Week4GeneralizationRunner``)
- Legacy Week 1 lambda sweeps (kept for backwards compatibility)
"""

import argparse
import json
from pathlib import Path
from typing import Dict, Any, List

import numpy as np

from src.utils.config import load_config
from src.envs.negotiation_v1 import NegotiationEnv
from src.observers.simple_observer import SimpleObserver
from src.social.social_score import SocialScoreFactory
from src.experiments.run_week4 import Week4GeneralizationRunner


class Week1ExperimentRunner:
    """Simple Week 1 lambda sweep runner.

    Retained so older configs relying on ``lambda_sweep`` continue to work,
    but new experiments (Week 4/5) use ``Week4GeneralizationRunner`` instead.
    """

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.set_seed()

        self.env = NegotiationEnv(
            total_resources=config["environment"]["total_resources"],
            max_turns=config["environment"]["max_turns"],
        )

        social_config = config["social_config"]
        self.observer = SimpleObserver(
            warmth_weight=social_config["warmth_weight"],
            competence_weight=social_config["competence_weight"],
        )

        self.social_score = SocialScoreFactory.create(
            social_config["score_type"],
            warmth_weight=social_config["warmth_weight"],
            competence_weight=social_config["competence_weight"],
        )

    def set_seed(self) -> None:
        seed = self.config["experiment"].get("seed", 0)
        np.random.seed(seed)

    def run_single_episode(self, lambda_social: float) -> Dict[str, float]:
        state = self.env.reset()
        mental_state = self.observer.create_initial_mental_state()

        while not state.is_terminal():
            if lambda_social > 1.0:
                offer = (3, 7)
            elif lambda_social > 0.5:
                offer = (5, 5)
            else:
                offer = (7, 3)

            state = self.env.step(state, offer)
            w_delta, c_delta = self.observer.observe_action(state, offer, 0)
            mental_state.warmth = np.clip(mental_state.warmth + 0.3 * w_delta, 0.0, 1.0)
            mental_state.competence = np.clip(
                mental_state.competence + 0.3 * c_delta,
                0.0,
                1.0,
            )
            state = self.env.accept_offer(state)

        task_reward = self.env.get_agent_reward(state, 0)
        social_score_val = self.social_score.compute(mental_state)
        total_utility = task_reward + lambda_social * social_score_val

        return {
            "task_reward": float(task_reward),
            "warmth": float(mental_state.warmth),
            "competence": float(mental_state.competence),
            "social_score": float(social_score_val),
            "total_utility": float(total_utility),
            "lambda_social": float(lambda_social),
            "final_agreement": state.final_agreement,
        }

    def run_experiment(self) -> List[Dict[str, Any]]:
        results: List[Dict[str, Any]] = []
        lambda_values = self.config["lambda_sweep"]["values"]
        num_runs = self.config["experiment"]["num_runs"]

        print(f"🚀 Running Week 1 Experiment: {self.config['experiment']['name']}")
        print(f"Lambda values: {lambda_values}")
        print(f"Runs per config: {num_runs}")
        print("=" * 50)

        for lambda_val in lambda_values:
            for run in range(num_runs):
                metrics = self.run_single_episode(lambda_val)
                metrics["run_id"] = run
                results.append(metrics)

                print(
                    f"λ={lambda_val:.1f}, Run {run+1}: "
                    f"Reward={metrics['task_reward']:.2f}, "
                    f"Warmth={metrics['warmth']:.2f}, "
                    f"Comp={metrics['competence']:.2f}"
                )

        return results

    def save_results(self, results: List[Dict[str, Any]], output_path: Path) -> None:
        output_path.parent.mkdir(parents=True, exist_ok=True)

        experiment_data = {"config": self.config, "results": results}

        with open(output_path, "w") as f:
            json.dump(experiment_data, f, indent=2)

        print(f"✅ Week 1 results saved to: {output_path}")

def main():
    parser = argparse.ArgumentParser(description='Run Week 1 negotiation experiment')
    parser.add_argument('--config', type=str, required=True,
                       help='Path to config YAML file')
    parser.add_argument('--out', type=str, 
                       default='results/week1/negotiation_results.json',
                       help='Output path for results')
    
    args = parser.parse_args()
    
    # Load config
    config: Dict[str, Any] = load_config(args.config)

    exp_meta = config.get("experiment", {})
    exp_name = exp_meta.get("name", "")

    # Week 4 / Week 5 style sweeps use the generalization runner, which
    # writes a JSONL file to the directory specified in the YAML.
    if "sweep_parameters" in config or exp_name in {
        "week4_negotiation_generalization",
        "week5_bayesian_sweep",
    }:
        runner = Week4GeneralizationRunner(config)
        results = runner.run()
        runner.save_results(results)
    else:
        # Fallback to legacy Week 1 runner for older configs.
        runner = Week1ExperimentRunner(config)
        results = runner.run_experiment()
        output_path = Path(args.out)
        runner.save_results(results, output_path)

if __name__ == "__main__":
    main()