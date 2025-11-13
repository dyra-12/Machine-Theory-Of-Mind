"""
Pluggable SocialScore system that integrates with your existing scorers
"""
from abc import ABC, abstractmethod
from typing import Dict, Any
from src.models.mental_states import MentalState

class SocialScore(ABC):
    """Abstract base class for SocialScore calculators"""
    
    @abstractmethod
    def compute(self, mental_state: MentalState, **kwargs) -> float:
        """Compute social score from mental state"""
        pass
    
    @abstractmethod
    def get_config(self) -> Dict[str, Any]:
        """Get configuration for reproducibility"""
        pass

class LinearSocialScore(SocialScore):
    """Linear combination - uses your existing weights"""
    
    def __init__(self, warmth_weight: float = 0.6, competence_weight: float = 0.4):
        self.warmth_weight = warmth_weight
        self.competence_weight = competence_weight
        
    def compute(self, mental_state: MentalState, **kwargs) -> float:
        return (self.warmth_weight * mental_state.warmth + 
                self.competence_weight * mental_state.competence)
    
    def get_config(self) -> Dict[str, Any]:
        return {
            "type": "linear",
            "warmth_weight": self.warmth_weight,
            "competence_weight": self.competence_weight
        }

# Factory to create social scorers
class SocialScoreFactory:
    """Factory for creating SocialScore instances"""
    
    @staticmethod
    def create(score_type: str, **kwargs) -> SocialScore:
        if score_type == "linear":
            return LinearSocialScore(**kwargs)
        # Add other types as needed
        else:
            raise ValueError(f"Unknown SocialScore type: {score_type}")