"""
Factory for creating all agent types - integrates existing advanced agents
"""
from typing import Dict, Any
import numpy as np

class AgentFactory:
    """Creates agents of all types with proper configuration"""
    
    @staticmethod
    def create(agent_type: str, agent_id: int = 0, **kwargs) -> object:
        """
        Create an agent of specified type
        
        Args:
            agent_type: Type of agent to create
            agent_id: ID of the agent (0 or 1)
            **kwargs: Agent-specific parameters
        """
        if agent_type == "greedy_baseline":
            from .baseline_greedy import GreedyBaseline
            return GreedyBaseline(agent_id=agent_id)
        
        elif agent_type == "social_baseline":
            from .baseline_social import SocialBaseline
            return SocialBaseline(agent_id=agent_id)
        
        elif agent_type == "random_baseline":
            from .baseline_random import RandomBaseline
            seed = kwargs.get('seed', 42)
            return RandomBaseline(agent_id=agent_id, seed=seed)
        
        elif agent_type == "simple_mtom":
            from .mtom_negotiation_agent import MToM_NegotiationAgent
            lambda_social = kwargs.get('lambda_social', 0.5)
            return MToM_NegotiationAgent(lambda_social=lambda_social, agent_id=agent_id)
        
        elif agent_type == "bayesian_mtom":
            from .bayesian_mtom_agent import BayesianMToMAgent
            lambda_social = kwargs.get('lambda_social', 0.5)
            prior_strength = kwargs.get('prior_strength', 6.0)
            adaptive_prior_offset = kwargs.get('adaptive_prior_offset')
            risk_weight = kwargs.get('risk_weight')
            lambda_schedule = kwargs.get('lambda_schedule')
            cultural_template = kwargs.get('cultural_template')
            cultural_overrides = kwargs.get('cultural_overrides')
            agent_config = {
                'lambda_social': lambda_social,
                'agent_id': agent_id,
                'prior_strength': prior_strength,
            }
            if adaptive_prior_offset is not None:
                agent_config['adaptive_prior_offset'] = adaptive_prior_offset
            if risk_weight is not None:
                agent_config['risk_weight'] = risk_weight
            if lambda_schedule is not None:
                agent_config['lambda_schedule'] = lambda_schedule
            if cultural_template is not None:
                agent_config['cultural_template'] = cultural_template
            if cultural_overrides is not None:
                agent_config['cultural_overrides'] = cultural_overrides
            return BayesianMToMAgent(**agent_config)
        
        elif agent_type == "learned_tom":
            from .enhanced_learned_agent import EnhancedLearnedAgent
            lambda_social = kwargs.get('lambda_social', 0.5)
            model_path = kwargs.get('model_path', 'best_neural_tom.pth')
            return EnhancedLearnedAgent(lambda_social=lambda_social, agent_id=agent_id, model_path=model_path)
        
        else:
            raise ValueError(f"Unknown agent type: {agent_type}")
    
    @staticmethod
    def get_available_agents() -> list:
        """Get list of available agent types"""
        return [
            "greedy_baseline",
            "social_baseline", 
            "random_baseline",
            "simple_mtom",
            "bayesian_mtom",
            "learned_tom"
        ]