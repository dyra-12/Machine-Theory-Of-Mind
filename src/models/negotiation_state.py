from dataclasses import dataclass

@dataclass
class NegotiationState:
    """Represents the state of a simple resource negotiation."""
    total_resources: int  # e.g., 10 chocolates to split
    our_offer: int  # Our proposed share for ourselves
    their_offer: int  # Their proposed share for themselves
    round: int = 0  # Current negotiation round
    
    def get_offer_for_other(self, our_offer: int) -> int:
        """Calculate what the other party gets given our offer."""
        return self.total_resources - our_offer