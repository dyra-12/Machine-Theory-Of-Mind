"""
Random baseline agent - chooses actions randomly
"""
import numpy as np
from typing import List, Tuple
from src.models.negotiation_state import NegotiationState

class RandomBaseline:
    """Random action selection baseline"""
    
    def __init__(self, agent_id: int = 0, seed: int = 42):
        self.agent_id = agent_id
        self.name = "random_baseline"
        self.rng = np.random.RandomState(seed)
    
    def choose_action(self, state: NegotiationState) -> Tuple[int, int]:
        """Choose random valid action"""
        available_actions = state.get_available_actions()
        # `RandomState.choice` expects a 1-D array-like of scalars; choose by
        # index to support lists of tuple actions reliably.
        idx = self.rng.choice(len(available_actions))
        return available_actions[int(idx)]
    
    def update_beliefs(self, state: NegotiationState, action: Tuple[int, int],
                      response: bool, opponent_action: Tuple[int, int] = None):
        """Random agent doesn't update beliefs"""
        pass
    
    def get_mental_state(self):
        return None