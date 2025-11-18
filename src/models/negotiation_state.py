from dataclasses import dataclass, field
from typing import List, Optional, Tuple

@dataclass
class NegotiationState:
    """Represents the state of a negotiation compatible with the
    `NegotiationEnv` used in the tests.

    Fields mirror the expected API used by `src/envs/negotiation_v1.py`:
    - total_resources, current_turn, max_turns, current_proposer
    - offers: list of (int,int) tuples
    - responses: list of bools
    - final_agreement: Optional[(int,int)]
    """
    total_resources: int
    current_turn: int = 0
    max_turns: int = 3
    current_proposer: int = 0
    offers: List[Tuple[int, int]] = field(default_factory=list)
    responses: List[bool] = field(default_factory=list)
    final_agreement: Optional[Tuple[int, int]] = None

    def is_terminal(self) -> bool:
        """Return True when negotiation has reached a terminal state.

        Terminal when a final agreement exists or max turns reached.
        """
        if self.final_agreement is not None:
            return True
        return self.current_turn >= self.max_turns

    def get_latest_offer(self) -> Optional[Tuple[int, int]]:
        return self.offers[-1] if self.offers else None

    def get_available_actions(self) -> List[Tuple[int, int]]:
        """Return all possible splits of `total_resources` between two agents.

        Actions are represented as tuples `(agent0_share, agent1_share)` and
        must sum to `total_resources`.
        """
        actions: List[Tuple[int, int]] = []
        # Require at least 1 resource for each agent to avoid degenerate offers
        # (tests expect agents to offer between 1 and total_resources-1)
        for a0 in range(1, self.total_resources):
            a1 = self.total_resources - a0
            actions.append((a0, a1))
        return actions

    def __repr__(self) -> str:  # Helpful for debugging/tests
        return (
            f"NegotiationState(total_resources={self.total_resources}, "
            f"current_turn={self.current_turn}, max_turns={self.max_turns}, "
            f"current_proposer={self.current_proposer}, offers={self.offers}, "
            f"responses={self.responses}, final_agreement={self.final_agreement})"
        )