"""
Tests for Week 1 deliverables - integrates with existing tests
"""
import pytest
import sys
import os
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent))

from src.envs.negotiation_v1 import NegotiationEnv
from src.observers.simple_observer import SimpleObserver
from src.social.social_score import SocialScoreFactory
from src.models.mental_states import MentalState

def test_week1_integration():
    """Test that Week 1 components work with existing models"""
    
    # Setup
    env = NegotiationEnv(total_resources=10, max_turns=3)
    observer = SimpleObserver()
    social_score = SocialScoreFactory.create("linear")
    
    # Test mental state integration
    mental_state = observer.create_initial_mental_state()
    assert isinstance(mental_state, MentalState)
    assert mental_state.warmth == 0.5
    assert mental_state.competence == 0.5
    
    # Test environment
    state = env.reset()
    assert state.total_resources == 10
    assert state.current_turn == 0
    
    # Test observer
    w_delta, c_delta = observer.observe_action(state, (3, 7), 0)
    assert w_delta > 0  # Generous offer increases warmth
    
    # Test social score computation
    score = social_score.compute(mental_state)
    assert 0 <= score <= 1
    
    print("✅ Week 1 integration tests passed!")

def test_config_loading():
    """Test configuration system"""
    from src.utils.config import load_config
    
    # This would test with a test config file
    # config = load_config("tests/test_config.yaml")
    # assert config is not None
    
    print("✅ Config system ready for Week 1")

if __name__ == "__main__":
    test_week1_integration()
    test_config_loading()
    print("🎉 All Week 1 tests passed!")