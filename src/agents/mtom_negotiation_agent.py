import numpy as np
from ..models.mental_states import MentalState
from ..models.negotiation_state import NegotiationState
from ..social.social_scorer import SocialScorer

class MToM_NegotiationAgent:
    """
    Fixed agent with better optimization and lambda sensitivity.
    """
    
    def __init__(self, lambda_social: float = 0.5, agent_type: str = "balanced"):
        self.lambda_social = lambda_social
        self.agent_type = agent_type
        self.mental_state = MentalState.neutral_prior()
        self.social_scorer = SocialScorer()
        
    def evaluate_offer(self, offer_self: int, negotiation_state: NegotiationState) -> float:
        """
        Evaluate a specific offer using the dual objective.
        """
        # More balanced task reward (less aggressive)
        task_reward = (offer_self / negotiation_state.total_resources) ** 0.8  # Reduced exponent
        
        # Social score
        delta_w, delta_c = self.social_scorer.predict_perception_change(
            offer_self, negotiation_state.total_resources)
        social_score = self.social_scorer.compute_social_score(delta_w, delta_c)
        
        # Combined utility with lambda weighting
        total_utility = task_reward + self.lambda_social * social_score
        
        return total_utility

    def make_offer(self, negotiation_state: NegotiationState) -> int:
        """
        Choose offer by evaluating all possible options.
        """
        best_offer = 1
        best_utility = -float('inf')
        
        # Evaluate all possible offers
        for offer in range(1, negotiation_state.total_resources):
            utility = self.evaluate_offer(offer, negotiation_state)
            if utility > best_utility:
                best_utility = utility
                best_offer = offer
        
        # Update mental state based on chosen offer
        self._update_mental_state(best_offer, negotiation_state)
        
        return best_offer
    
    def _update_mental_state(self, chosen_offer: int, negotiation_state: NegotiationState):
        """Update mental state based on chosen action."""
        delta_w, delta_c = self.social_scorer.predict_perception_change(
            chosen_offer, negotiation_state.total_resources)
        
        # More substantial updates
        self.mental_state.warmth = np.clip(
            self.mental_state.warmth + 0.3 * delta_w, 0.05, 0.95
        )
        self.mental_state.competence = np.clip(
            self.mental_state.competence + 0.3 * delta_c, 0.05, 0.95
        )
    
    def get_mental_state(self) -> MentalState:
        return self.mental_state
    
    def __str__(self):
        return f"{self.agent_type}(λ={self.lambda_social})"