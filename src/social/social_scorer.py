import numpy as np
from typing import Tuple
from ..models.mental_states import MentalState

class SocialScorer:
    """
    Computes SocialScore based on the Stereotype Content Model.
    Fixed to be more sensitive to different offers.
    """
    
    def __init__(self, warmth_weight: float = 0.6, competence_weight: float = 0.4):
        self.warmth_weight = warmth_weight
        self.competence_weight = competence_weight
        
    def predict_perception_change(self, offer_self: int, total_resources: int) -> Tuple[float, float]:
        """
        More nuanced perception model with stronger differentiation.
        """
        ratio = offer_self / total_resources
        
        # More pronounced differences between strategies
        if ratio <= 0.3:  # Very generous
            delta_warmth = 1.2
            delta_competence = -0.8
        elif ratio <= 0.45:  # Generous
            delta_warmth = 0.6
            delta_competence = -0.2
        elif ratio <= 0.55:  # Fair
            delta_warmth = 0.2
            delta_competence = 0.3
        elif ratio <= 0.7:  # Selfish
            delta_warmth = -0.6
            delta_competence = 0.5
        else:  # Very selfish
            delta_warmth = -1.2
            delta_competence = 0.8
            
        return delta_warmth, delta_competence

    def observe_action(self, state, action: Tuple[int, int], agent_id: int) -> Tuple[float, float]:
        """Observe an action and return (warmth_delta, competence_delta).

        This mirrors the interface used by `SimpleObserver.observe_action` so
        agents can use `SocialScorer` interchangeably.
        """
        offer_self = action[agent_id]
        return self.predict_perception_change(offer_self, state.total_resources)
    
    def compute_social_score(self, delta_warmth, delta_competence=None) -> float:
        """
        Compute social score from perception changes.
        """
        # Support two calling conventions:
        # - compute_social_score(mental_state) -> compute from MentalState attributes
        # - compute_social_score(delta_warmth, delta_competence) -> compute from deltas
        # If called with a single object (mental state-like), compute from attributes
        if delta_competence is None:
            ms = delta_warmth
            return (self.warmth_weight * ms.warmth +
                    self.competence_weight * ms.competence)

        # Otherwise treat as two numeric deltas
        social_score = (self.warmth_weight * delta_warmth +
                       self.competence_weight * delta_competence)
        return social_score