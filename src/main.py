from .agents.mtom_negotiation_agent import MToM_NegotiationAgent
from .models.negotiation_state import NegotiationState

def main():
    """Main demonstration of the MToM negotiation agent."""
    print("🤖 Machine Theory of Mind - Negotiation Demo")
    print("=" * 50)
    
    # Create agents with different social preferences
    social_agent = MToM_NegotiationAgent(lambda_social=0.8)
    balanced_agent = MToM_NegotiationAgent(lambda_social=0.5)
    task_agent = MToM_NegotiationAgent(lambda_social=0.2)
    
    agents = [("Social-focused", social_agent),
              ("Balanced", balanced_agent), 
              ("Task-focused", task_agent)]
    
    # Test each agent
    for name, agent in agents:
        print(f"\n{name} Agent:")
        print("-" * 30)
        
        negotiation = NegotiationState(total_resources=10, our_offer=0, their_offer=0)
        
        for round in range(2):
            offer = agent.make_offer(negotiation)
            mental_state = agent.get_mental_state()
            print(f"  Round {round+1}: Offer {offer}/10")
            print(f"    Mental State: warmth={mental_state.warmth:.2f}, competence={mental_state.competence:.2f}")

if __name__ == "__main__":
    main()