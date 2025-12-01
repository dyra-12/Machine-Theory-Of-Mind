import numpy as np
import pymc as pm
import arviz as az
from typing import Dict, Tuple

class BayesianMentalState:
    """
    Represents probabilistic beliefs about human perceptions using Bayesian modeling.
    Models warmth and competence as probability distributions with uncertainty.
    """
    
    def __init__(self, prior_warmth: float = 0.5, prior_competence: float = 0.5,
                 prior_strength: float = 10.0, adaptive_offset: float = 0.0):
        self.prior_warmth = prior_warmth
        self.prior_competence = prior_competence
        self.prior_strength = prior_strength  # Equivalent to "pseudo-observations"
        self.adaptive_offset = adaptive_offset
        
        # Current beliefs (will be updated via Bayesian inference)
        self.warmth_belief = np.clip(prior_warmth + adaptive_offset, 0.01, 0.99)
        self.competence_belief = np.clip(prior_competence + adaptive_offset, 0.01, 0.99)
        self.warmth_uncertainty = 0.3  # Standard deviation
        self.competence_uncertainty = 0.3
        
        # Track belief history
        self.belief_history = {
            'warmth': [prior_warmth],
            'competence': [prior_competence],
            'warmth_uncertainty': [0.3],
            'competence_uncertainty': [0.3]
        }
    
    def bayesian_update(self, observed_warmth: float, observed_competence: float, 
                    observation_confidence: float = 0.7) -> None:
        """
        FIXED: Much stronger belief updates to actually change mental states
        """
        # Convert to "success" and "failure" counts for Beta distribution
        prior_alpha_w = self.prior_warmth * self.prior_strength
        prior_beta_w = (1 - self.prior_warmth) * self.prior_strength
        
        prior_alpha_c = self.prior_competence * self.prior_strength
        prior_beta_c = (1 - self.prior_competence) * self.prior_strength
        
        # CRITICAL FIX: Much stronger evidence (was 1.0, now 3.0)
        evidence_strength = observation_confidence * self.prior_strength * 3.0
        
        obs_alpha_w = observed_warmth * evidence_strength
        obs_beta_w = (1 - observed_warmth) * evidence_strength
        
        obs_alpha_c = observed_competence * evidence_strength
        obs_beta_c = (1 - observed_competence) * evidence_strength
        
        # Bayesian update: posterior = prior + evidence
        posterior_alpha_w = prior_alpha_w + obs_alpha_w
        posterior_beta_w = prior_beta_w + obs_beta_w
        
        posterior_alpha_c = prior_alpha_c + obs_alpha_c
        posterior_beta_c = prior_beta_c + obs_beta_c
        
        # Update beliefs
        self.warmth_belief = posterior_alpha_w / (posterior_alpha_w + posterior_beta_w)
        self.competence_belief = posterior_alpha_c / (posterior_alpha_c + posterior_beta_c)
        
        # Update uncertainties (Beta distribution variance)
        total_w = posterior_alpha_w + posterior_beta_w
        total_c = posterior_alpha_c + posterior_beta_c
        self.warmth_uncertainty = np.sqrt(
            (posterior_alpha_w * posterior_beta_w) / (total_w ** 2 * (total_w + 1))
        )
        self.competence_uncertainty = np.sqrt(
            (posterior_alpha_c * posterior_beta_c) / (total_c ** 2 * (total_c + 1))
        )
        
        # Track history
        self.belief_history['warmth'].append(self.warmth_belief)
        self.belief_history['competence'].append(self.competence_belief)
        self.belief_history['warmth_uncertainty'].append(self.warmth_uncertainty)
        self.belief_history['competence_uncertainty'].append(self.competence_uncertainty)
    
    
    def sample_possible_states(self, n_samples: int = 1000) -> Tuple[np.ndarray, np.ndarray]:
        """
        Sample possible mental states from current belief distribution.
        Useful for probabilistic planning and considering multiple hypotheses.
        """
        warmth_samples = np.random.beta(
            self.warmth_belief * self.prior_strength,
            (1 - self.warmth_belief) * self.prior_strength,
            n_samples
        )
        competence_samples = np.random.beta(
            self.competence_belief * self.prior_strength,
            (1 - self.competence_belief) * self.prior_strength,
            n_samples
        )
        return warmth_samples, competence_samples
    
    def get_credible_interval(self, interval: float = 0.95) -> Dict:
        """
        Get credible intervals for warmth and competence beliefs.
        """
        warmth_samples, competence_samples = self.sample_possible_states(10000)
        
        lower_bound = (1 - interval) / 2
        upper_bound = 1 - lower_bound
        
        return {
            'warmth': np.quantile(warmth_samples, [lower_bound, upper_bound]),
            'competence': np.quantile(competence_samples, [lower_bound, upper_bound])
        }
    
    def __str__(self):
        ci = self.get_credible_interval(0.9)
        return (f"BayesianMentalState(\n"
                f"  warmth: {self.warmth_belief:.3f} ± {self.warmth_uncertainty:.3f}\n"
                f"  competence: {self.competence_belief:.3f} ± {self.competence_uncertainty:.3f}\n"
                f"  90% CI warmth: [{ci['warmth'][0]:.3f}, {ci['warmth'][1]:.3f}]\n"
                f"  90% CI competence: [{ci['competence'][0]:.3f}, {ci['competence'][1]:.3f}]\n"
                f")")