import sys
from pathlib import Path

import pytest

sys.path.append(str(Path(__file__).resolve().parents[1]))

from src.models.negotiation_state import NegotiationState
from src.observers.simple_observer import SimpleObserver
from src.observers.adversarial_observer import AdversarialObserver


@pytest.fixture
def base_state():
    return NegotiationState(total_resources=10)


def test_adversarial_observer_inverts_signal(base_state):
    base = SimpleObserver()
    adv = AdversarialObserver(
        noise_std=0.0,
        deception_prob=1.0,
        inversion_strength=1.0,
        bias=(0.0, 0.0),
        dropout_prob=0.0,
        seed=7,
    )

    base_w, base_c = base.observe_action(base_state, (8, 2), agent_id=0)
    adv_w, adv_c = adv.observe_action(base_state, (8, 2), agent_id=0)

    assert pytest.approx(adv_w) == -base_w
    assert pytest.approx(adv_c) == -base_c


def test_adversarial_observer_dropout_returns_noise(base_state):
    adv = AdversarialObserver(
        noise_std=0.0,
        deception_prob=0.0,
        dropout_prob=1.0,
        bias=(0.0, 0.0),
        seed=3,
    )

    w, c = adv.observe_action(base_state, (5, 5), agent_id=0)

    assert w == pytest.approx(0.0)
    assert c == pytest.approx(0.0)


def test_reliability_metric_matches_params():
    adv = AdversarialObserver(deception_prob=0.5, dropout_prob=0.2)
    expected = max(0.0, 1.0 - 0.5 - 0.1)
    assert pytest.approx(adv.reliability) == expected
