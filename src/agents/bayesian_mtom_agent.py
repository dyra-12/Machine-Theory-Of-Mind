import numpy as np
from typing import Dict, List
from ..models.bayesian_mental_state import BayesianMentalState
from ..models.negotiation_state import NegotiationState
from ..social.bayesian_social_scorer import BayesianSocialScorer

class BayesianMToMAgent:
    """
    A Bayesian Theory of Mind agent that maintains probabilistic beliefs about
    human mental states and uses Bayesian decision theory for action selection.
    """
    
    def __init__(self, lambda_social: float = 0.5, agent_id: int = 0, agent_type: str = "bayesian",
                 prior_strength: float = 6.0):
        self.lambda_social = lambda_social
        self.agent_id = agent_id
        self.agent_type = agent_type
        self.prior_strength = prior_strength
        
        # Probabilistic mental state
        self.mental_state = BayesianMentalState(prior_strength=prior_strength)
        
        # Bayesian social reasoning
        self.social_scorer = BayesianSocialScorer()
        
        # Decision history for analysis
        self.decision_history = []
    
    def evaluate_offer_bayesian(self, offer_self: int, negotiation_state: NegotiationState) -> Dict:
        """
        Evaluate an offer using full Bayesian decision theory.
        Returns comprehensive utility analysis with uncertainty quantification.
        """
        utility_analysis = self.social_scorer.bayesian_utility(
            offer_self, self.mental_state, self.lambda_social, negotiation_state.total_resources
        )
        
        return utility_analysis
    
    def make_offer(self, negotiation_state: NegotiationState) -> int:
        """
        Choose offer by evaluating all options using Bayesian decision theory.
        Considers both expected utility and risk.
        """
        best_offer = 1
        best_expected_utility = -float('inf')
        best_utility_analysis = None
        
        evaluations = []
        
        # Evaluate all possible offers
        for offer in range(1, negotiation_state.total_resources):
            analysis = self.evaluate_offer_bayesian(offer, negotiation_state)
            evaluations.append((offer, analysis))
            
            # Prefer higher expected utility, with stronger penalty on very risky
            # options when social preferences are low. When lambda_social is high,
            # allow more exploration of generous actions.
            risk_weight = 0.05 if self.lambda_social >= 0.7 else 0.15
            risk_adjusted_utility = analysis['expected_utility'] * (1 - risk_weight * analysis['risk_ratio'])
            
            if risk_adjusted_utility > best_expected_utility:
                best_expected_utility = risk_adjusted_utility
                best_offer = offer
                best_utility_analysis = analysis
        
        # Update mental state using Bayesian inference
        self._bayesian_mental_update(best_offer, negotiation_state, best_utility_analysis)
        
        # Record decision
        self.decision_history.append({
            'offer': best_offer,
            'mental_state': {
                'warmth': self.mental_state.warmth_belief,
                'competence': self.mental_state.competence_belief,
                'warmth_uncertainty': self.mental_state.warmth_uncertainty,
                'competence_uncertainty': self.mental_state.competence_uncertainty
            },
            'evaluation': best_utility_analysis
        })
        
        return best_offer

    def choose_action(self, negotiation_state: NegotiationState):
        """Adapter to the common agent interface: returns a (agent0_share, agent1_share) tuple."""
        offer_for_self = self.make_offer(negotiation_state)
        total = negotiation_state.total_resources
        if self.agent_id == 0:
            return (offer_for_self, total - offer_for_self)
        else:
            return (total - offer_for_self, offer_for_self)

    def update_beliefs(self, state: NegotiationState, action, response: bool, opponent_action=None):
        """Update Bayesian beliefs after observing an interaction."""
        offer_self = action[self.agent_id]
        perception = self.social_scorer.predict_perception_distribution(offer_self, state.total_resources)

        warmth_obs = perception['warmth_mean']
        competence_obs = perception['competence_mean']
        confidence = 0.65

        # Infer acceptance/rejection from the most recent response if available
        last_response = state.responses[-1] if state.responses else None
        if last_response is False:
            # Harsh feedback: perceived warmth/competence underestimated
            warmth_obs = max(0.01, warmth_obs - 0.15)
            competence_obs = max(0.01, competence_obs - 0.1)
            confidence = 0.9
        elif last_response is True:
            warmth_obs = min(0.99, warmth_obs + 0.05)
            confidence = 0.7

        self.mental_state.bayesian_update(
            observed_warmth=warmth_obs,
            observed_competence=competence_obs,
            observation_confidence=confidence
        )

    def get_mental_state(self):
        """Return a simple view of current beliefs for downstream scoring."""
        return type('ms', (object,), {
            'warmth': self.mental_state.warmth_belief,
            'competence': self.mental_state.competence_belief
        })
    
    def _bayesian_mental_update(self, chosen_offer: int, negotiation_state: NegotiationState,
                              utility_analysis: Dict) -> None:
        """Update mental state using proper Bayesian inference."""
        # Get the expected perception change for the chosen action
        perception_dist = self.social_scorer.predict_perception_distribution(
            chosen_offer, negotiation_state.total_resources
        )
        
        # Update beliefs using Bayesian inference
        self.mental_state.bayesian_update(
            observed_warmth=perception_dist['warmth_mean'],
            observed_competence=perception_dist['competence_mean'],
            observation_confidence=0.7  # Medium confidence in our psychological model
        )
    
    def get_belief_history(self) -> Dict:
        """Get the complete history of belief updates."""
        return {
            'mental_state': self.mental_state.belief_history,
            'decisions': self.decision_history
        }
    
    def get_current_beliefs(self) -> Dict:
        """Get current beliefs with uncertainty quantification."""
        ci = self.mental_state.get_credible_interval(0.9)
        return {
            'warmth': {
                'mean': self.mental_state.warmth_belief,
                'uncertainty': self.mental_state.warmth_uncertainty,
                '90_ci': ci['warmth'].tolist()
            },
            'competence': {
                'mean': self.mental_state.competence_belief, 
                'uncertainty': self.mental_state.competence_uncertainty,
                '90_ci': ci['competence'].tolist()
            }
        }
    
    def __str__(self):
        return f"BayesianMToM(λ={self.lambda_social}, prior_strength={self.prior_strength})"