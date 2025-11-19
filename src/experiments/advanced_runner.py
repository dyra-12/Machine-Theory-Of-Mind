"""
Advanced experiment runner with systematic sweeps and comprehensive metrics
"""
import json
import time
from pathlib import Path
from typing import Dict, List, Any
import numpy as np
from concurrent.futures import ProcessPoolExecutor
import itertools

from src.utils.logging import ExperimentLogger
from src.utils.reproducibility import set_global_seeds
from src.envs.negotiation_v1 import NegotiationEnv
from src.agents.agent_factory import AgentFactory

class AdvancedExperimentRunner:
    """
    Runs comprehensive experiments with parameter sweeps and parallel execution
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = ExperimentLogger(config)
        self.agent_factory = AgentFactory()
        
    def run_parameter_sweep(self) -> List[Dict[str, Any]]:
        """Run comprehensive parameter sweep"""
        all_results = []
        
        # Generate all parameter combinations
        sweep_configs = self._generate_sweep_configs()
        
        print(f"🚀 Running {len(sweep_configs)} experiment configurations")
        print(f"📊 Total runs: {len(sweep_configs) * self.config['experiment']['runs_per_config']}")
        
        # Run experiments (parallel or sequential)
        if self.config['experiment'].get('parallel', False):
            all_results = self._run_parallel(sweep_configs)
        else:
            for config in sweep_configs:
                results = self._run_single_configuration(config)
                all_results.extend(results)
        
        return all_results
    
    def _generate_sweep_configs(self) -> List[Dict[str, Any]]:
        """Generate all parameter combinations for sweeping"""
        base_config = self.config
        
        # Define parameter spaces to sweep
        agent_types = base_config['sweep_parameters']['agent_types']
        lambda_values = base_config['sweep_parameters']['lambda_values']
        seeds = list(range(base_config['experiment']['num_seeds']))
        
        # Generate all combinations
        configs = []
        for agent_type, lambda_val, seed in itertools.product(agent_types, lambda_values, seeds):
            config = {
                'agent_type': agent_type,
                'lambda_social': lambda_val,
                'seed': seed,
                'run_id': f"{agent_type}_λ{lambda_val}_s{seed}"
            }
            configs.append(config)
        
        return configs

    def _run_parallel(self, sweep_configs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Run sweep configurations in parallel where possible.

        Note: a safe sequential fallback is used to avoid pickling issues with instance
        methods when using multiprocessing. If true parallelism is desired, this method
        can be expanded to spawn processes and call a module-level worker function.
        """
        all_results: List[Dict[str, Any]] = []
        for cfg in sweep_configs:
            results = self._run_single_configuration(cfg)
            all_results.extend(results)
        return all_results
    
    def _run_single_configuration(self, config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Run multiple episodes for a single configuration"""
        set_global_seeds(config['seed'])
        
        results = []
        for episode in range(self.config['experiment']['runs_per_config']):
            start_time = time.time()
            
            # Run episode
            episode_results = self._run_single_episode(config)
            episode_results.update({
                'episode_id': episode,
                'run_time': time.time() - start_time,
                'config_hash': self.logger.get_config_hash(config)
            })
            
            # Log results
            self.logger.log_episode(episode_results)
            results.append(episode_results)
        
        return results
    
    def _run_single_episode(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Run a single negotiation episode with comprehensive metrics"""
        env = NegotiationEnv(
            total_resources=self.config['environment']['total_resources'],
            max_turns=self.config['environment']['max_turns']
        )
        
        # Create agents
        agent0 = self.agent_factory.create(
            config['agent_type'],
            agent_id=0,
            lambda_social=config['lambda_social']
        )
        
        # Fixed opponent for controlled comparisons
        opponent_type = self.config['experiment']['opponent_type']
        agent1 = self.agent_factory.create(opponent_type, agent_id=1)
        
        # Track episode metrics
        episode_metrics = {
            'agent_type': config['agent_type'],
            'lambda_social': config['lambda_social'],
            'seed': config['seed'],
            'warmth_trajectory': [],
            'competence_trajectory': [],
            'actions_taken': []
        }
        
        # Run negotiation
        state = env.reset()
        while not state.is_terminal() and state.current_turn < state.max_turns:
            if state.current_proposer == 0:
                action = agent0.choose_action(state)
                state = env.step(state, action)
                episode_metrics['actions_taken'].append(action)
                
                # Update mental state tracking
                if hasattr(agent0, 'get_mental_state'):
                    mental_state = agent0.get_mental_state()
                    if mental_state is not None:
                        episode_metrics['warmth_trajectory'].append(mental_state.warmth)
                        episode_metrics['competence_trajectory'].append(mental_state.competence)
            
            # Simplified opponent response
            response = np.random.random() < 0.7  # 70% acceptance rate
            if response:
                state = env.accept_offer(state)
            else:
                state = env.reject_offer(state)
        
        # Calculate final metrics
        final_metrics = self._calculate_episode_metrics(episode_metrics, state, agent0)
        episode_metrics.update(final_metrics)
        
        return episode_metrics
    
    def _calculate_episode_metrics(self, episode_metrics: Dict, state, agent) -> Dict[str, Any]:
        """FIXED: Proper metric calculation without data leakage"""
        # FIX: Calculate task reward properly
        if state.final_agreement:
            task_reward = state.final_agreement[0] / state.total_resources
        else:
            task_reward = 0.0  # No agreement = 0 reward
        
        # FIX: Independent social metric calculation
        if hasattr(agent, 'get_mental_state'):
            mental_state = agent.get_mental_state()
            if mental_state is not None:
                warmth = max(0.0, min(1.0, mental_state.warmth))  # Clamp to valid range
                competence = max(0.0, min(1.0, mental_state.competence))
            else:
                # Fallback when agent exposes method but returns None
                if episode_metrics['actions_taken']:
                    last_action = episode_metrics['actions_taken'][-1]
                    ratio_self = last_action[0] / state.total_resources
                    warmth = 1.0 - ratio_self
                    competence = ratio_self
                else:
                    warmth = competence = 0.5
        else:
            # FIX: Estimate from final action if available
            if episode_metrics['actions_taken']:
                last_action = episode_metrics['actions_taken'][-1]
                ratio_self = last_action[0] / state.total_resources
                warmth = 1.0 - ratio_self  # Simple heuristic
                competence = ratio_self
            else:
                warmth = competence = 0.5
        
        # FIX: Use configured weights, not hard-coded
        social_score = (self.config['social_config']['warmth_weight'] * warmth + 
                    self.config['social_config']['competence_weight'] * competence)
        
        # FIX: Calculate utility with proper bounds
        total_utility = task_reward + episode_metrics['lambda_social'] * social_score
        
        return {
            'task_reward': float(task_reward),
            'warmth_final': float(warmth),
            'competence_final': float(competence),
            'social_score': float(social_score),
            'total_utility': float(total_utility),
            'agreement_reached': state.final_agreement is not None,
            'num_turns': state.current_turn,
            'action_diversity': len(set(episode_metrics['actions_taken'])) / max(1, len(episode_metrics['actions_taken'])),
            'final_agreement': state.final_agreement
        }