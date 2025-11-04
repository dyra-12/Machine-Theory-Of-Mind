from dataclasses import dataclass
from typing import Dict, List, Optional
import numpy as np

@dataclass
class MentalState:
    """Represents the AI's belief about the human's mental state"""
    warmth: float  # 0.0 to 1.0 probability of high warmth attribution
    competence: float  # 0.0 to 1.0 probability of high competence attribution
    goals: List[str]  # Inferred human goals
    beliefs: Dict[str, float]  # Inferred human beliefs with confidence
    
    @classmethod
    def default(cls):
        """Start with neutral priors"""
        return cls(warmth=0.5, competence=0.5, goals=[], beliefs={})

@dataclass 
class SocialAction:
    """An action with predicted social consequences"""
    name: str
    task_utility: float  # -1.0 to 1.0
    predicted_warmth_impact: float  # -1.0 to 1.0  
    predicted_competence_impact: float  # -1.0 to 1.0
    
    def total_value(self, warmth_weight: float = 0.5, competence_weight: float = 0.5) -> float:
        """Calculate combined value of this action"""
        social_value = (warmth_weight * self.predicted_warmth_impact + 
                       competence_weight * self.predicted_competence_impact)
        return self.task_utility + social_value