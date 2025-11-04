from dataclasses import dataclass, field
from typing import Dict


@dataclass
class MentalState:
    """Tracks the agent's belief about the human's perceptions."""
    warmth: float  # Probability of high warmth attribution (0.0 to 1.0)
    competence: float  # Probability of high competence attribution (0.0 to 1.0)
    goals: Dict = field(default_factory=dict)
    beliefs: Dict = field(default_factory=dict)

    @classmethod
    def neutral_prior(cls):
        """Start with neutral priors about what the human thinks of us."""
        return cls(warmth=0.5, competence=0.5)

    # Convenience alias used by some agents/tests
    @classmethod
    def default(cls):
        return cls.neutral_prior()

    def __str__(self):
        return f"MentalState(warmth={self.warmth:.2f}, competence={self.competence:.2f})"


@dataclass
class SocialAction:
    """Simple representation of a social action and its predicted effects.

    Fields:
    - name: identifier
    - predicted_warmth_impact: expected change to perceived warmth (can be negative)
    - predicted_competence_impact: expected change to perceived competence
    - task_value: a numeric estimate of how much the action advances task goals
    """
    name: str
    predicted_warmth_impact: float
    predicted_competence_impact: float
    task_value: float = 0.0

    def total_value(self, warmth_weight: float, competence_weight: float) -> float:
        """Compute a simple combined value used by the agent's chooser.

        This is intentionally simple: a weighted sum of predicted social impacts
        plus the task value.
        """
        return (warmth_weight * self.predicted_warmth_impact
                + competence_weight * self.predicted_competence_impact
                + self.task_value)