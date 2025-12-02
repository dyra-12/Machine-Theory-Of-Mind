import numpy as np
from typing import Dict, List, Optional
from ..models.bayesian_mental_state import BayesianMentalState
from ..models.negotiation_state import NegotiationState
from ..social.bayesian_social_scorer import BayesianSocialScorer

class BayesianMToMAgent:
    """
    A Bayesian Theory of Mind agent that maintains probabilistic beliefs about
    human mental states and uses Bayesian decision theory for action selection.
    """
    
    def __init__(
        self,
        lambda_social: float = 0.5,
        agent_id: int = 0,
        agent_type: str = "bayesian",
        prior_strength: float = 6.0,
        adaptive_prior_offset: float = 0.0,
        risk_weight: float = 0.15,
        lambda_schedule: Optional[Dict[str, float]] = None,
    ):
        self.lambda_social = lambda_social
        self.agent_id = agent_id
        self.agent_type = agent_type
        self.prior_strength = prior_strength
        self.adaptive_prior_offset = adaptive_prior_offset or 0.0
        self.risk_weight = risk_weight
        self.lambda_schedule = lambda_schedule
        
        # Probabilistic mental state
        self.mental_state = BayesianMentalState(
            prior_strength=prior_strength,
            adaptive_offset=self.adaptive_prior_offset,
        )
        
        # Bayesian social reasoning
        self.social_scorer = BayesianSocialScorer()
        
        # Decision history for analysis
        self.decision_history = []
    
    def evaluate_offer_bayesian(
        self,
        offer_self: int,
        negotiation_state: NegotiationState,
        lambda_override: Optional[float] = None,
    ) -> Dict:
        """
        Evaluate an offer using full Bayesian decision theory.
        Returns comprehensive utility analysis with uncertainty quantification.
        """
        lambda_to_use = lambda_override if lambda_override is not None else self.lambda_social
        utility_analysis = self.social_scorer.bayesian_utility(
            offer_self,
            self.mental_state,
            lambda_to_use,
            negotiation_state.total_resources,
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
        lambda_for_turn = self._effective_lambda(negotiation_state)
        
        # Evaluate all possible offers
        for offer in range(1, negotiation_state.total_resources):
            analysis = self.evaluate_offer_bayesian(offer, negotiation_state, lambda_for_turn)
            evaluations.append((offer, analysis))
            
            # Prefer higher expected utility, with stronger penalty on very risky
            # options when social preferences are low. When lambda_social is high,
            # allow more exploration of generous actions.
            risk_adj = self.risk_weight if lambda_for_turn < 0.8 else self.risk_weight * 0.6
            expected_util = analysis.get('expected_utility')
            if not isinstance(expected_util, (int, float)) or np.isnan(expected_util):
                expected_util = 0.0
            risk_ratio = analysis.get('risk_ratio')
            if not isinstance(risk_ratio, (int, float)) or np.isnan(risk_ratio):
                risk_ratio = 0.0
            risk_adjusted_utility = expected_util * (1 - risk_adj * risk_ratio)

            # Encourage reclaiming task reward when social incentive remains high
            task_reward_val = analysis.get('task_reward')
            if not isinstance(task_reward_val, (int, float)) or np.isnan(task_reward_val):
                task_reward_val = 0.0
            selfish_bonus = task_reward_val * max(0.0, 0.4 - lambda_for_turn * 0.2)
            if self.mental_state.warmth_belief < 0.45:
                selfish_bonus += 0.05 * task_reward_val
            risk_adjusted_utility += selfish_bonus
            
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
            'warmth': float(self.mental_state.warmth_belief),
            'competence': float(self.mental_state.competence_belief)
        })
    
    def _bayesian_mental_update(self, chosen_offer: int, negotiation_state: NegotiationState,
                              utility_analysis: Dict) -> None:
        """Update mental state using proper Bayesian inference."""
        # Get the expected perception change for the chosen action
        perception_dist = self.social_scorer.predict_perception_distribution(
            chosen_offer, negotiation_state.total_resources
        )
        
        # Update beliefs using Bayesian inference
        confidence = 0.7 + 0.1 * self.adaptive_prior_offset
        confidence = min(0.95, max(0.4, confidence))
        self.mental_state.bayesian_update(
            observed_warmth=perception_dist['warmth_mean'],
            observed_competence=perception_dist['competence_mean'],
            observation_confidence=confidence
        )

    def _effective_lambda(self, negotiation_state: NegotiationState) -> float:
        """Compute lambda for current turn based on optional schedule and interaction context."""
        schedule_factor = 1.0
        if self.lambda_schedule and self.lambda_schedule.get("decay_turns", 0) > 0:
            start = self.lambda_schedule.get("start_factor", 1.0)
            end = self.lambda_schedule.get("end_factor", 1.0)
            decay_turns = max(1, self.lambda_schedule.get("decay_turns", 1))
            current_turn = getattr(negotiation_state, "current_turn", 0)
            progress = min(1.0, max(0.0, current_turn / decay_turns))
            schedule_factor = start + (end - start) * progress

        interaction_factor = self._interaction_lambda_factor(negotiation_state)
        lambda_val = self.lambda_social * schedule_factor * interaction_factor
        return max(0.15, min(lambda_val, self.lambda_social * 1.6))

    def _interaction_lambda_factor(self, negotiation_state: NegotiationState) -> float:
        """Adaptive scaling that reduces social weight when opponent seems cold or turns are low."""
        factor = 1.0
        turns_left = max(0, getattr(negotiation_state, "max_turns", 3) - getattr(negotiation_state, "current_turn", 0))
        if turns_left <= 1:
            factor *= 0.55
        elif turns_left <= 2:
            factor *= 0.75

        warmth = float(self.mental_state.warmth_belief)
        if warmth < 0.4:
            factor *= 0.75
        elif warmth < 0.5:
            factor *= 0.85
        elif warmth > 0.65:
            factor *= 1.08

        responses = getattr(negotiation_state, "responses", None)
        if responses:
            last_response = responses[-1]
            if last_response is False:
                factor *= 0.85
            elif last_response is True and warmth > 0.5:
                factor *= 1.04

        return factor
    
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