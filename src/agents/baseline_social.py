"""
Social baseline agent - maximizes only social perception
"""
import numpy as np
from typing import List, Tuple, Optional
from src.models.negotiation_state import NegotiationState
from src.observers.simple_observer import SimpleObserver
from src.models.mental_states import MentalState

class SocialBaseline:
    """Pure social perception maximizer - ignores task reward"""
    
    def __init__(self, agent_id: int = 0):
        self.agent_id = agent_id
        self.name = "social_baseline"
        self.observer = SimpleObserver()
        self.mental_state = MentalState(warmth=0.5, competence=0.5)
    
    def choose_action(self, state: NegotiationState) -> Tuple[int, int]:
        """Choose action that maximizes social score"""
        available_actions = state.get_available_actions()
        
        best_action = None
        best_social_score = -float('inf')
        
        for action in available_actions:
            # Predict social impact
            w_delta, c_delta = self.observer.observe_action(state, action, self.agent_id)
            predicted_warmth = np.clip(self.mental_state.warmth + 0.3 * w_delta, 0.0, 1.0)
            predicted_competence = np.clip(self.mental_state.competence + 0.3 * c_delta, 0.0, 1.0)
            
            temp_mental_state = MentalState(warmth=predicted_warmth, competence=predicted_competence)
            social_score = self.observer.compute_social_score(temp_mental_state)
            
            if social_score > best_social_score:
                best_social_score = social_score
                best_action = action
        
        return best_action
    
    def update_beliefs(
        self,
        state: NegotiationState,
        action: Tuple[int, int],
        response: bool,
        opponent_action: Tuple[int, int] = None,
        observer_feedback=None,
        feedback_reliability: Optional[float] = None,
    ):
        """Update mental state based on chosen action"""
        if observer_feedback is not None:
            w_delta, c_delta = observer_feedback
        else:
            w_delta, c_delta = self.observer.observe_action(state, action, self.agent_id)
        gain = 0.3 * (0.5 + 0.5 * (feedback_reliability if feedback_reliability is not None else 1.0))
        self.mental_state.warmth = np.clip(self.mental_state.warmth + gain * w_delta, 0.0, 1.0)
        self.mental_state.competence = np.clip(self.mental_state.competence + gain * c_delta, 0.0, 1.0)
    
    def get_mental_state(self):
        return self.mental_state