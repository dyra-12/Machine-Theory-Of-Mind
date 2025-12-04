"""
Simple observer that maps actions → warmth & competence scores
Uses your existing MentalState model
"""
from typing import Tuple
import numpy as np

from src.models.negotiation_state import NegotiationState
from src.models.mental_states import MentalState

class SimpleObserver:
    """
    Observes agent actions and infers warmth/competence perceptions
    Compatible with your existing social scoring
    """
    
    def __init__(self, warmth_weight: float = 0.6, competence_weight: float = 0.4):
        self.warmth_weight = warmth_weight
        self.competence_weight = competence_weight
        
    def observe_action(self, state: NegotiationState, action: Tuple[int, int], 
                      agent_id: int) -> Tuple[float, float]:
        """
        Observe an action and return (warmth_delta, competence_delta)
        Uses your existing perception mapping logic
        """
        offer_self, offer_other = action
        total = state.total_resources
        ratio_self = offer_self / total
        
        # Use your existing perception mapping
        if ratio_self <= 0.3:  # Very generous
            warmth_delta = 1.2
            competence_delta = -0.8
        elif ratio_self <= 0.45:  # Generous
            warmth_delta = 0.6
            competence_delta = -0.2
        elif ratio_self <= 0.55:  # Fair
            warmth_delta = 0.2
            competence_delta = 0.3
        elif ratio_self <= 0.7:  # Selfish
            warmth_delta = -0.6
            competence_delta = 0.5
        else:  # Very selfish
            warmth_delta = -1.2
            competence_delta = 0.8
            
        return warmth_delta, competence_delta
    
    def compute_social_score(self, mental_state: MentalState) -> float:
        """Compute social score using your existing mental state"""
        return (self.warmth_weight * mental_state.warmth + 
                self.competence_weight * mental_state.competence)
    
    def create_initial_mental_state(self) -> MentalState:
        """Create initial mental state using your existing model"""
        return MentalState(warmth=0.5, competence=0.5)

    @property
    def reliability(self) -> float:
        """Channel reliability score used to scale observation confidence."""
        return 1.0

    def describe_channel(self) -> dict:
        return {
            'noise_std': 0.0,
            'deception_prob': 0.0,
            'dropout_prob': 0.0,
            'reliability': self.reliability,
            'type': 'simple'
        }