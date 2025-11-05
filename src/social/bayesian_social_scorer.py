import numpy as np
from scipy import stats
from ..models.bayesian_mental_state import BayesianMentalState
from typing import Dict, Tuple, List

class BayesianSocialScorer:
    """
    Uses Bayesian inference to model how actions affect social perceptions.
    Incorporates uncertainty and probabilistic reasoning about human judgments.
    """
    
    def __init__(self):
        # Psychological priors based on established research
        self.action_impact_priors = {
            'very_generous': {'warmth_mean': 0.8, 'competence_mean': 0.2, 'uncertainty': 0.2},
            'generous': {'warmth_mean': 0.6, 'competence_mean': 0.4, 'uncertainty': 0.15},
            'fair': {'warmth_mean': 0.5, 'competence_mean': 0.6, 'uncertainty': 0.1},
            'selfish': {'warmth_mean': 0.3, 'competence_mean': 0.7, 'uncertainty': 0.15},
            'very_selfish': {'warmth_mean': 0.1, 'competence_mean': 0.9, 'uncertainty': 0.2}
        }
        
        # Individual differences model (people vary in their judgments)
        self.judgment_heterogeneity = 0.1
    
    def predict_perception_distribution(self, offer_self: int, total_resources: int) -> Dict:
        """
        Predicts the distribution of possible human perceptions for a given offer.
        Returns mean and uncertainty for warmth and competence impacts.
        """
        ratio = offer_self / total_resources
        
        # Map offers to psychological categories with probabilistic boundaries
        if ratio <= 0.3:
            category = 'very_generous'
        elif ratio <= 0.45:
            category = 'generous'
        elif ratio <= 0.55:
            category = 'fair' 
        elif ratio <= 0.7:
            category = 'selfish'
        else:
            category = 'very_selfish'
        
        prior = self.action_impact_priors[category]
        
        # Return distribution parameters (could be sampled from)
        return {
            'warmth_mean': prior['warmth_mean'],
            'warmth_std': prior['uncertainty'] + self.judgment_heterogeneity,
            'competence_mean': prior['competence_mean'],
            'competence_std': prior['uncertainty'] + self.judgment_heterogeneity,
            'category': category
        }
    
    def bayesian_utility(self, offer_self: int, mental_state: BayesianMentalState,
                        lambda_social: float, total_resources: int) -> Dict:
        """
        Calculate utility using Bayesian decision theory: consider multiple possible outcomes
        and their probabilities, not just the most likely outcome.
        """
        # Sample possible perception changes
        perception_dist = self.predict_perception_distribution(offer_self, total_resources)
        
        # Sample possible mental state updates
        n_samples = 1000
        warmth_deltas = np.random.normal(
            perception_dist['warmth_mean'], 
            perception_dist['warmth_std'], 
            n_samples
        )
        competence_deltas = np.random.normal(
            perception_dist['competence_mean'],
            perception_dist['competence_std'],
            n_samples
        )
        
        # Current belief samples
        current_warmth, current_competence = mental_state.sample_possible_states(n_samples)
        
        # Projected future beliefs
        future_warmth = np.clip(current_warmth + warmth_deltas * 0.3, 0.01, 0.99)
        future_competence = np.clip(current_competence + competence_deltas * 0.3, 0.01, 0.99)
        
        # Task reward (deterministic)
        task_reward = (offer_self / total_resources) ** 0.8
        
        # Social reward distribution across samples
        social_rewards = (future_warmth + future_competence) / 2
        expected_social_reward = np.mean(social_rewards)
        social_reward_uncertainty = np.std(social_rewards)
        
        # Total utility distribution
        total_utilities = task_reward + lambda_social * social_rewards
        expected_utility = np.mean(total_utilities)
        utility_uncertainty = np.std(total_utilities)
        
        return {
            'expected_utility': expected_utility,
            'utility_uncertainty': utility_uncertainty,
            'task_reward': task_reward,
            'expected_social_reward': expected_social_reward,
            'social_reward_uncertainty': social_reward_uncertainty,
            'risk_ratio': utility_uncertainty / expected_utility if expected_utility > 0 else 0,
            'perception_category': perception_dist['category']
        }