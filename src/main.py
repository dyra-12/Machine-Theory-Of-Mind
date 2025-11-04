try:
    from src.agents.mtom_agent import SimpleMToMAgent
except ModuleNotFoundError:
    # When running `python src/main.py` the interpreter's sys.path
    # contains the `src/` directory as the script location, so
    # `import src...` fails. Add the project root to sys.path so
    # absolute imports using the `src` package work both when
    # running as a module and when running the script directly.
    import sys
    from pathlib import Path

    project_root = Path(__file__).resolve().parents[1]
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

    from src.agents.mtom_agent import SimpleMToMAgent

def debug_agent_values(agent, name):
    """Show the value calculations for each action"""
    print(f"\n{name} Agent Analysis:")
    print("Action".ljust(20) + "Task".ljust(10) + "Warmth".ljust(10) + "Competence".ljust(12) + "Total Value")
    print("-" * 60)
    
    for action_name, action in agent.actions.items():
        task_val = action.task_utility
        warmth_val = agent.warmth_weight * action.predicted_warmth_impact
        competence_val = agent.competence_weight * action.predicted_competence_impact
        total_val = action.total_value(agent.warmth_weight, agent.competence_weight)
        
        print(f"{action_name.ljust(20)}{task_val:.2f}".ljust(10) + 
              f"{warmth_val:.2f}".ljust(10) + 
              f"{competence_val:.2f}".ljust(12) + 
              f"{total_val:.2f}")


def main():
    print("🤖 Starting Machine Theory of Mind Agent - DEBUG")
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
        
        debug_agent_values(agent, name)
        print(f"  → Chosen action: {action}")

if __name__ == "__main__":
    main()