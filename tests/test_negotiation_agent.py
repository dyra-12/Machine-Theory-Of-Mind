import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.agents.mtom_negotiation_agent import MToM_NegotiationAgent
from src.models.negotiation_state import NegotiationState

def test_final_agent():
    """Test the final calibrated MToM agent."""
    print("🤖 FINAL MToM Negotiation Agent - Properly Calibrated")
    print("=" * 60)
    
    # More reasonable lambda values
    configs = [
        ("Social-focused", 2.0),  # Even higher social weighting
        ("Balanced", 1.0),        # Equal weighting  
        ("Task-focused", 0.3)     # Low social weighting
    ]
    
    for name, lambda_social in configs:
        print(f"\n--- {name} Agent (λ={lambda_social}) ---")
        agent = MToM_NegotiationAgent(lambda_social=lambda_social, agent_type=name)
        negotiation = NegotiationState(total_resources=10, our_offer=0, their_offer=0)
        
        print(f"Initial mental state: {agent.get_mental_state()}")
        
        for round in range(2):
            offer = agent.make_offer(negotiation)
            mental_state = agent.get_mental_state()
            
            # Show the reasoning
            task_reward = (offer / 10) ** 0.8
            delta_w, delta_c = agent.social_scorer.predict_perception_change(offer, 10)
            social_score = agent.social_scorer.compute_social_score(delta_w, delta_c)
            total_utility = task_reward + lambda_social * social_score
            
            print(f"Round {round+1}: Offer {offer}/10")
            print(f"  Reasoning: Task={task_reward:.2f}, Social={social_score:.2f}, Total={total_utility:.2f}")
            print(f"  Mental State: warmth={mental_state.warmth:.2f}, competence={mental_state.competence:.2f}")

def comprehensive_analysis():
    """Show the full decision landscape."""
    print("\n" + "=" * 60)
    print("COMPREHENSIVE DECISION ANALYSIS")
    print("=" * 60)
    
    negotiation = NegotiationState(total_resources=10, our_offer=0, their_offer=0)
    lambda_values = [2.0, 1.0, 0.3]
    
    for lambda_val in lambda_values:
        agent = MToM_NegotiationAgent(lambda_social=lambda_val)
        print(f"\nλ={lambda_val}:")
        print("Offer | Task  | Social | Total | WarmthΔ | CompetenceΔ")
        print("-" * 55)
        
        best_offer = 1
        best_utility = -float('inf')
        
        for offer in range(1, 10):
            task_reward = (offer / 10) ** 0.8
            delta_w, delta_c = agent.social_scorer.predict_perception_change(offer, 10)
            social_score = agent.social_scorer.compute_social_score(delta_w, delta_c)
            total_utility = task_reward + lambda_val * social_score
            
            if total_utility > best_utility:
                best_utility = total_utility
                best_offer = offer
                
            print(f"{offer:5} | {task_reward:.3f} | {social_score:6.3f} | {total_utility:5.3f} | {delta_w:8.1f} | {delta_c:12.1f}")
        
        print(f"→ BEST OFFER: {best_offer} (utility: {best_utility:.3f})")

if __name__ == "__main__":
    test_final_agent()
    comprehensive_analysis()