import numpy as np
from typing import List, Dict
from src.models.mental_states import MentalState, SocialAction

class SimpleMToMAgent:
    """Minimal MToM agent that reasons about warmth/competence"""
    
    def __init__(self, warmth_weight: float = 0.5, competence_weight: float = 0.5):
        self.warmth_weight = warmth_weight
        self.competence_weight = competence_weight
        self.mental_state = MentalState.default()
        
        # Simple action library - we'll expand this later
        self.actions = {
            'task_focus': SocialAction('task_focus', 0.8, -0.3, 0.4),
            'social_help': SocialAction('social_help', 0.2, 0.7, -0.2), 
            'balanced_approach': SocialAction('balanced_approach', 0.5, 0.3, 0.3)
        }
    
    def update_mental_state(self, observation: Dict):
        """Very simple mental state update based on observation"""
        # Placeholder - we'll make this probabilistic later
        if 'positive_social_cue' in observation:
            self.mental_state.warmth = min(1.0, self.mental_state.warmth + 0.1)
        if 'efficiency_demonstrated' in observation:
            self.mental_state.competence = min(1.0, self.mental_state.competence + 0.1)
    
    def predict_action_impact(self, action: SocialAction) -> MentalState:
        """Predict how action will change human's mental state"""
        predicted_state = MentalState(
            warmth=max(0.0, min(1.0, self.mental_state.warmth + action.predicted_warmth_impact * 0.3)),
            competence=max(0.0, min(1.0, self.mental_state.competence + action.predicted_competence_impact * 0.3)),
            goals=self.mental_state.goals.copy(),
            beliefs=self.mental_state.beliefs.copy()
        )
        return predicted_state
    
    def choose_action(self) -> str:
        """Choose action that maximizes combined value"""
        best_action_name = None
        best_value = -float('inf')
        
        for action_name, action in self.actions.items():
            value = action.total_value(self.warmth_weight, self.competence_weight)
            if value > best_value:
                best_value = value
                best_action_name = action_name
                
        return best_action_name

    def get_mental_state(self) -> MentalState:
        return self.mental_state