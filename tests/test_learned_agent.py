import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.agents.enhanced_learned_agent import EnhancedLearnedMToM
from src.models.negotiation_state import NegotiationState

def test_enhanced_learned_agent():
    """Test the Enhanced Learned MToM agent with advanced architecture."""
    print("🧠 Testing ENHANCED Learned MToM Agent (Advanced Neural Architecture)")
    print("=" * 75)
    
    # Train one model and share it
    print("Training advanced model (this may take a moment)...")
    first_agent = EnhancedLearnedMToM(lambda_social=1.0)
    shared_model = first_agent.model
    
    # Test different configurations
    configs = [
        ("Social-Enhanced-Learned", 1.5),
        ("Balanced-Enhanced-Learned", 0.8),
        ("Task-Enhanced-Learned", 0.3)
    ]
    
    for name, lambda_social in configs:
        print(f"\n--- {name} (λ={lambda_social}) ---")
        agent = EnhancedLearnedMToM(
            lambda_social=lambda_social, 
            agent_type=name,
            model=shared_model
        )
        negotiation = NegotiationState(total_resources=10, our_offer=0, their_offer=0)
        
        for round in range(3):
            offer = agent.make_offer(negotiation)
            mental_state = agent.get_mental_state()
            evaluation = agent.evaluate_offer(offer, negotiation)
            
            print(f"Round {round+1}: Offer {offer}/10")
            print(f"  Predicted: warmth={evaluation['predicted_warmth']:.2f}±{evaluation['warmth_uncertainty']:.2f}, "
                  f"competence={evaluation['predicted_competence']:.2f}±{evaluation['competence_uncertainty']:.2f}")
            print(f"  Utility: task={evaluation['task_reward']:.2f}, "
                  f"social={evaluation['social_reward']:.2f}, "
                  f"total={evaluation['expected_utility']:.2f}")

def compare_enhanced_decisions():
    """Compare decision making across different lambda values."""
    print("\n" + "=" * 75)
    print("ENHANCED LEARNED DECISION COMPARISON")
    print("=" * 75)
    
    # Train one shared model
    agent = EnhancedLearnedMToM(lambda_social=1.0)
    shared_model = agent.model
    
    lambda_values = [1.5, 0.8, 0.3]
    negotiation = NegotiationState(total_resources=10, our_offer=0, their_offer=0)
    
    for lambda_val in lambda_values:
        agent = EnhancedLearnedMToM(lambda_social=lambda_val, model=shared_model)
        print(f"\nλ={lambda_val}:")
        print("Offer | Task  | Warmth | Competence | Social | Total")
        print("-" * 55)
        
        for offer in [2, 4, 5, 6, 8]:
            evaluation = agent.evaluate_offer(offer, negotiation)
            print(f"{offer:5} | {evaluation['task_reward']:.3f} | "
                  f"{evaluation['predicted_warmth']:.3f} | "
                  f"{evaluation['predicted_competence']:10.3f} | "
                  f"{evaluation['social_reward']:6.3f} | {evaluation['expected_utility']:.3f}")

if __name__ == "__main__":
    test_enhanced_learned_agent()
    compare_enhanced_decisions()