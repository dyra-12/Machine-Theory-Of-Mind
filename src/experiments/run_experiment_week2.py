"""
Week 2 Experiment Runner - Tests all agent types
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
from src.agents.agent_factory import AgentFactory

class Week2ExperimentRunner:
    """Runs Week 2 experiments comparing all agent types"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.set_seed()
        
        # Initialize components
        self.env = NegotiationEnv(
            total_resources=config['environment']['total_resources'],
            max_turns=config['environment']['max_turns']
        )
        
        social_config = config['social_config']
        self.observer = SimpleObserver(
            warmth_weight=social_config['warmth_weight'],
            competence_weight=social_config['competence_weight']
        )
        
        self.social_score = SocialScoreFactory.create(
            social_config['score_type'],
            warmth_weight=social_config['warmth_weight'],
            competence_weight=social_config['competence_weight']
        )
        
        self.agent_factory = AgentFactory()
    
    def set_seed(self):
        """Set random seed for reproducibility"""
        seed = self.config['experiment']['seed']
        np.random.seed(seed)
    
    def run_single_episode(self, agent0_type: str, lambda_social: float = 0.5) -> Dict[str, float]:
        """
        Run a single negotiation episode with specified agents
        """
        state = self.env.reset()
        
        # Create agents
        agent0 = self.agent_factory.create(
            agent0_type, 
            agent_id=0,
            lambda_social=lambda_social
        )
        
        agent1_type = self.config['agents']['agent1_type']
        agent1_lambda = self.config['agents'].get('agent1_lambda', 0.5)
        agent1 = self.agent_factory.create(
            agent1_type,
            agent_id=1, 
            lambda_social=agent1_lambda
        )
        
        # Run negotiation
        while not state.is_terminal() and state.current_turn < state.max_turns:
            if state.current_proposer == 0:
                action = agent0.choose_action(state)
                state = self.env.step(state, action)
                
                # Agent1 responds (simple accept/reject logic)
                if np.random.random() < 0.7:  # 70% chance of acceptance
                    state = self.env.accept_offer(state)
                else:
                    state = self.env.reject_offer(state)
                    
                agent0.update_beliefs(state, action, True)
                
            else:  # Agent1's turn to propose
                action = agent1.choose_action(state)
                state = self.env.step(state, action)
                
                # Agent0 responds
                if np.random.random() < 0.7:
                    state = self.env.accept_offer(state)
                else:
                    state = self.env.reject_offer(state)
                    
                agent1.update_beliefs(state, action, True)
        
        # Calculate metrics for agent0
        task_reward = self.env.get_agent_reward(state, 0)
        
        # Get social metrics from agent0's mental state if available
        mental_state = agent0.get_mental_state()
        if mental_state:
            warmth = mental_state.warmth
            competence = mental_state.competence
            social_score_val = self.social_score.compute(mental_state)
        else:
            # Estimate social score from final agreement
            if state.final_agreement:
                w_delta, c_delta = self.observer.observe_action(state, state.final_agreement, 0)
                warmth = 0.5 + 0.3 * w_delta
                competence = 0.5 + 0.3 * c_delta
                temp_mental_state = type('obj', (object,), {'warmth': warmth, 'competence': competence})
                social_score_val = self.social_score.compute(temp_mental_state)
            else:
                warmth = competence = social_score_val = 0.0
        
        total_utility = task_reward + lambda_social * social_score_val
        
        return {
            "task_reward": float(task_reward),
            "warmth": float(warmth),
            "competence": float(competence),
            "social_score": float(social_score_val),
            "total_utility": float(total_utility),
            "lambda_social": float(lambda_social),
            "agent0_type": agent0_type,
            "final_agreement": state.final_agreement,
            "num_turns": state.current_turn
        }
    
    def run_comparison_experiment(self) -> List[Dict[str, Any]]:
        """Run comparison across all agent types and lambda values"""
        results = []
        agent_types = self.config['agents']['agent0_types']
        lambda_values = self.config['lambda_sweep']['values']
        num_runs = self.config['experiment']['num_runs']
        
        print(f"🚀 Running Week 2 Agent Comparison")
        print(f"Agent types: {agent_types}")
        print(f"Lambda values: {lambda_values}")
        print(f"Runs per config: {num_runs}")
        print("=" * 60)
        
        for agent_type in agent_types:
            for lambda_val in lambda_values:
                # Skip lambda for non-MToM agents
                if "baseline" in agent_type or "random" in agent_type:
                    actual_lambda = 0.0
                else:
                    actual_lambda = lambda_val
                
                for run in range(num_runs):
                    metrics = self.run_single_episode(agent_type, actual_lambda)
                    metrics['run_id'] = run
                    results.append(metrics)
                    
                    print(f"Agent: {agent_type:15} λ={actual_lambda:.1f} Run {run+1}: "
                          f"Reward={metrics['task_reward']:.2f} "
                          f"Warmth={metrics['warmth']:.2f} "
                          f"Comp={metrics['competence']:.2f}")
        
        return results
    
    def save_results(self, results: List[Dict[str, Any]], output_path: Path):
        """Save results to JSON file"""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        experiment_data = {
            "config": self.config,
            "results": results
        }
        
        with open(output_path, 'w') as f:
            json.dump(experiment_data, f, indent=2)
        
        print(f"✅ Week 2 results saved to: {output_path}")

def main():
    parser = argparse.ArgumentParser(description='Run Week 2 agent comparison')
    parser.add_argument('--config', type=str, required=True,
                       help='Path to config YAML file')
    parser.add_argument('--out', type=str, 
                       default='results/week2/agent_comparison.json',
                       help='Output path for results')
    
    args = parser.parse_args()
    
    # Load config
    config = load_config(args.config)
    
    # Run experiment
    runner = Week2ExperimentRunner(config)
    results = runner.run_comparison_experiment()
    
    # Save results
    output_path = Path(args.out)
    runner.save_results(results, output_path)

if __name__ == "__main__":
    main()