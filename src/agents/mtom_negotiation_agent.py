"""
Enhanced MToM agent with proper lambda integration
"""
import numpy as np
from typing import Tuple, Optional
from src.models.mental_states import MentalState
from src.models.negotiation_state import NegotiationState
from src.social.social_scorer import SocialScorer

class MToM_NegotiationAgent:
    """
    Enhanced MToM agent with configurable lambda weighting
    """
    
    def __init__(self, lambda_social: float = 0.5, agent_id: int = 0, agent_type: str = "simple_mtom"):
        self.lambda_social = lambda_social
        self.agent_id = agent_id
        self.agent_type = agent_type
        self.mental_state = MentalState(warmth=0.5, competence=0.5)
        self.social_scorer = SocialScorer()
    
    def evaluate_offer(self, offer: Tuple[int, int], state: NegotiationState) -> float:
        """Evaluate offer using dual objective with lambda weighting"""
        task_reward = offer[self.agent_id] / state.total_resources
        
        # Predict social impact
        w_delta, c_delta = self.social_scorer.predict_perception_change(
            offer[self.agent_id], state.total_resources)
        predicted_warmth = np.clip(self.mental_state.warmth + 0.3 * w_delta, 0.0, 1.0)
        predicted_competence = np.clip(self.mental_state.competence + 0.3 * c_delta, 0.0, 1.0)
        
        temp_mental_state = MentalState(warmth=predicted_warmth, competence=predicted_competence)
        social_score = self.social_scorer.compute_social_score(temp_mental_state)
        
        # Dual objective with lambda weighting
        total_utility = task_reward + self.lambda_social * social_score
        return total_utility
    
    def choose_action(self, state: NegotiationState) -> Tuple[int, int]:
        """Choose action that maximizes dual objective"""
        available_actions = state.get_available_actions()
        
        best_action = None
        best_utility = -float('inf')
        
        for action in available_actions:
            utility = self.evaluate_offer(action, state)
            if utility > best_utility:
                best_utility = utility
                best_action = action
        
        return best_action

    def make_offer(self, state: NegotiationState) -> int:
        """Compatibility shim: return the integer share for this agent (used in tests)."""
        action = self.choose_action(state)
        return int(action[self.agent_id])
    
    def update_beliefs(
        self,
        state: NegotiationState,
        action: Tuple[int, int],
        response: bool,
        opponent_action: Tuple[int, int] = None,
        observer_feedback=None,
        feedback_reliability: Optional[float] = None,
    ):
        """Update mental state based on interaction"""
        if observer_feedback is not None:
            w_delta, c_delta = observer_feedback
        else:
            w_delta, c_delta = self.social_scorer.observe_action(state, action, self.agent_id)
        gain = 0.3 * (0.5 + 0.5 * (feedback_reliability if feedback_reliability is not None else 1.0))
        self.mental_state.warmth = np.clip(self.mental_state.warmth + gain * w_delta, 0.0, 1.0)
        self.mental_state.competence = np.clip(self.mental_state.competence + gain * c_delta, 0.0, 1.0)
    
    def get_mental_state(self):
        return self.mental_state
    
    def __str__(self):
        return f"{self.agent_type}(λ={self.lambda_social}, id={self.agent_id})"