import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.agents.bayesian_mtom_agent import BayesianMToM_NegotiationAgent
from src.models.negotiation_state import NegotiationState

def test_bayesian_agent():
    """Test the Bayesian MToM agent with probabilistic reasoning."""
    print("🧠 Testing Bayesian MToM Agent with Probabilistic Reasoning")
    print("=" * 65)
    
    # Test different configurations
    configs = [
        ("Social-Bayesian", 1.5, 15.0),  # Strong social preference, confident priors
        ("Balanced-Bayesian", 0.8, 10.0), # Moderate, default confidence
        ("Cautious-Bayesian", 0.8, 5.0),  # Moderate, but uncertain priors
    ]
    
    for name, lambda_social, prior_strength in configs:
        print(f"\n--- {name} (λ={lambda_social}, prior_strength={prior_strength}) ---")
        agent = BayesianMToM_NegotiationAgent(
            lambda_social=lambda_social, 
            agent_type=name,
            prior_strength=prior_strength
        )
        negotiation = NegotiationState(total_resources=10, our_offer=0, their_offer=0)
        
        print(f"Initial: {agent.mental_state}")
        
        # Run multiple rounds to see belief evolution
        for round in range(3):
            offer = agent.make_offer(negotiation)
            beliefs = agent.get_current_beliefs()
            
            print(f"Round {round+1}: Offer {offer}/10")
            print(f"  Warmth: {beliefs['warmth']['mean']:.3f} ± {beliefs['warmth']['uncertainty']:.3f}")
            print(f"  Competence: {beliefs['competence']['mean']:.3f} ± {beliefs['competence']['uncertainty']:.3f}")
            print(f"  90% CI Warmth: [{beliefs['warmth']['90_ci'][0]:.3f}, {beliefs['warmth']['90_ci'][1]:.3f}]")
            
        # Show final belief state
        print(f"Final: {agent.mental_state}")

def analyze_bayesian_decision_making():
    """Analyze how Bayesian agent makes decisions under uncertainty."""
    print("\n" + "=" * 65)
    print("BAYESIAN DECISION ANALYSIS")
    print("=" * 65)
    
    agent = BayesianMToM_NegotiationAgent(lambda_social=1.0)
    negotiation = NegotiationState(total_resources=10, our_offer=0, their_offer=0)
    
    print("Offer | Exp Utility | Uncertainty | Risk Ratio | Category")
    print("-" * 65)
    
    for offer in [2, 4, 5, 6, 8]:
        analysis = agent.evaluate_offer_bayesian(offer, negotiation)
        print(f"{offer:5} | {analysis['expected_utility']:11.3f} | "
              f"{analysis['utility_uncertainty']:11.3f} | "
              f"{analysis['risk_ratio']:10.3f} | {analysis['perception_category']:>15}")

if __name__ == "__main__":
    test_bayesian_agent()
    analyze_bayesian_decision_making()