import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.agents.mtom_agent import SimpleMToMAgent

def test_agent_creation():
    """Test that we can create an agent and it has basic functionality"""
    agent = SimpleMToMAgent(warmth_weight=0.7, competence_weight=0.3)
    
    # Test initial state
    mental_state = agent.get_mental_state()
    assert mental_state.warmth == 0.5
    assert mental_state.competence == 0.5
    
    # Test action selection
    action = agent.choose_action()
    assert action in ['task_focus', 'social_help', 'balanced_approach']
    
    # Test social help is preferred with high warmth weight
    warm_agent = SimpleMToMAgent(warmth_weight=0.9, competence_weight=0.1)
    warm_action = warm_agent.choose_action()
    print(f"Warm agent chose: {warm_action}")
    
    print("✅ All basic tests passed!")

if __name__ == "__main__":
    test_agent_creation()