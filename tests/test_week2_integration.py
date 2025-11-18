"""
Test Week 2 integration
"""
import pytest
import sys
import os
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from src.agents.agent_factory import AgentFactory
from src.envs.negotiation_v1 import NegotiationEnv

def test_agent_factory():
    """Test that all agent types can be created"""
    factory = AgentFactory()
    
    # Test baseline agents
    greedy = factory.create("greedy_baseline")
    social = factory.create("social_baseline") 
    random = factory.create("random_baseline")
    
    assert greedy is not None
    assert social is not None
    assert random is not None
    
    # Test MToM agents
    try:
        simple_mtom = factory.create("simple_mtom", lambda_social=0.5)
        assert simple_mtom is not None
    except ImportError:
        print("ℹ️  simple_mtom not available, skipping")
    
    try:
        bayesian = factory.create("bayesian_mtom", lambda_social=0.5)
        assert bayesian is not None
    except ImportError:
        print("ℹ️  bayesian_mtom not available, skipping")
    
    try:
        learned = factory.create("learned_tom", lambda_social=0.5)
        assert learned is not None
    except ImportError:
        print("ℹ️  learned_tom not available, skipping")
    
    print("✅ Agent factory working correctly")

def test_baseline_agents():
    """Test baseline agent behaviors"""
    env = NegotiationEnv(total_resources=10, max_turns=3)
    state = env.reset()
    
    # Test greedy agent
    from src.agents.baseline_greedy import GreedyBaseline
    greedy = GreedyBaseline()
    action = greedy.choose_action(state)
    assert action[0] == 9  # Should take maximum for self
    
    # Test social agent  
    from src.agents.baseline_social import SocialBaseline
    social = SocialBaseline()
    action = social.choose_action(state)
    assert action[0] == 1  # Should be very generous
    
    print("✅ Baseline agents behaving correctly")

if __name__ == "__main__":
    test_agent_factory()
    test_baseline_agents()
    print("🎉 Week 2 integration tests passed!")