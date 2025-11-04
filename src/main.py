from src.agents.mtom_agent import SimpleMToMAgent

def main():
    print("🤖 Starting Machine Theory of Mind Agent")
    print("=" * 50)
    
    # Test different agent configurations
    configurations = [
        ("Task-focused", 0.1, 0.9),
        ("Social-focused", 0.9, 0.1), 
        ("Balanced", 0.5, 0.5)
    ]
    
    for name, warmth, competence in configurations:
        agent = SimpleMToMAgent(warmth_weight=warmth, competence_weight=competence)
        action = agent.choose_action()
        mental_state = agent.get_mental_state()
        
        print(f"\n{name} Agent:")
        print(f"  Weights: Warmth={warmth}, Competence={competence}")
        print(f"  Chosen action: {action}")
        print(f"  Mental state: Warmth={mental_state.warmth:.2f}, Competence={mental_state.competence:.2f}")

if __name__ == "__main__":
    main()