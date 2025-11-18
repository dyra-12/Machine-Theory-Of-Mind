"""
Negotiation Environment v1.0 - Integrates with existing models
"""
from typing import Dict, List, Tuple, Optional
import numpy as np

# Import your existing models
from src.models.negotiation_state import NegotiationState as ExistingNegotiationState
from src.models.mental_states import MentalState

class NegotiationEnv:
    """
    Simple 2-agent negotiation environment with discrete resource splitting
    Builds on your existing NegotiationState
    """
    
    def __init__(self, total_resources: int = 10, max_turns: int = 3):
        self.total_resources = total_resources
        self.max_turns = max_turns
        
    def reset(self) -> ExistingNegotiationState:
        """Reset environment to initial state using your existing model"""
        return ExistingNegotiationState(
            total_resources=self.total_resources,
            current_turn=0,
            max_turns=self.max_turns,
            current_proposer=0,  # Agent 0 starts
            offers=[],
            responses=[],
            final_agreement=None
        )
    
    def step(self, state: ExistingNegotiationState, action: Tuple[int, int]) -> ExistingNegotiationState:
        """Execute one negotiation step"""
        if state.is_terminal():
            raise ValueError("Cannot step terminal state")
        
        # Validate action
        if sum(action) != self.total_resources:
            raise ValueError(f"Action {action} must sum to {self.total_resources}")
        
        # Create new state using your existing model
        new_state = ExistingNegotiationState(
            total_resources=state.total_resources,
            current_turn=state.current_turn + 1,
            max_turns=state.max_turns,
            current_proposer=1 - state.current_proposer,  # Alternate proposer
            offers=state.offers + [action],
            responses=state.responses + [False],
            final_agreement=None
        )
        
        return new_state
    
    def accept_offer(self, state: ExistingNegotiationState) -> ExistingNegotiationState:
        """Accept the current offer (end negotiation)"""
        if not state.offers:
            raise ValueError("No offer to accept")
        
        new_state = ExistingNegotiationState(
            total_resources=state.total_resources,
            current_turn=state.current_turn,
            max_turns=state.max_turns,
            current_proposer=state.current_proposer,
            offers=state.offers.copy(),
            responses=state.responses + [True],
            final_agreement=state.offers[-1]
        )
        
        return new_state

    def reject_offer(self, state: ExistingNegotiationState) -> ExistingNegotiationState:
        """Reject the current offer (continue negotiation).

        This appends a rejection response to the history and leaves
        `final_agreement` as None. The proposer will alternate on the
        next `step()` call as usual.
        """
        if not state.offers:
            raise ValueError("No offer to reject")

        new_state = ExistingNegotiationState(
            total_resources=state.total_resources,
            current_turn=state.current_turn,
            max_turns=state.max_turns,
            current_proposer=state.current_proposer,
            offers=state.offers.copy(),
            responses=state.responses + [False],
            final_agreement=None
        )

        return new_state
    
    def get_agent_reward(self, state: ExistingNegotiationState, agent_id: int) -> float:
        """Get final reward for agent"""
        if state.final_agreement:
            return state.final_agreement[agent_id] / self.total_resources
        else:  # No agreement
            return 0.0