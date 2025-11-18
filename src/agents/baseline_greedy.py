"""
Greedy baseline agent - maximizes only task reward
"""
import numpy as np
from typing import List, Tuple
from src.models.negotiation_state import NegotiationState

class GreedyBaseline:
    """Pure task-reward maximizer - ignores social perceptions"""
    
    def __init__(self, agent_id: int = 0):
        self.agent_id = agent_id
        self.name = "greedy_baseline"
    
    def choose_action(self, state: NegotiationState) -> Tuple[int, int]:
        """Choose action that maximizes immediate self-reward"""
        available_actions = state.get_available_actions()
        
        # Simply choose the action that gives us the most resources
        best_action = max(available_actions, key=lambda a: a[self.agent_id])
        return best_action
    
    def update_beliefs(self, state: NegotiationState, action: Tuple[int, int], 
                      response: bool, opponent_action: Tuple[int, int] = None):
        """Greedy agent doesn't update beliefs about others"""
        pass
    
    def get_mental_state(self):
        """Greedy agent doesn't track mental states"""
        return None