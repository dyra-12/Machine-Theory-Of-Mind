import sys
from pathlib import Path

import pytest

sys.path.append(str(Path(__file__).resolve().parents[1]))

from src.agents.bayesian_mtom_agent import BayesianMToMAgent
from src.models.bayesian_mental_state import BayesianMentalState
from src.social.bayesian_social_scorer import BayesianSocialScorer


def test_cultural_templates_adjust_priors():
    """Collectivist templates should expect more warmth and tighter fairness."""
    collectivist = BayesianMentalState(cultural_template='collectivist')
    individualist = BayesianMentalState(cultural_template='individualist')

    assert collectivist.prior_warmth > individualist.prior_warmth
    assert collectivist.fairness_anchor < individualist.fairness_anchor
    assert collectivist.cultural_profile['name'] == 'collectivist'


@pytest.mark.parametrize('offer_self,total', [(6, 10), (7, 10)])
def test_fairness_anchor_shifts_perception(offer_self, total):
    """The same offer should feel fairer to an individualist template."""
    individualist_scorer = BayesianSocialScorer(fairness_anchor=0.6)
    collectivist_scorer = BayesianSocialScorer(fairness_anchor=0.45)

    ind_dist = individualist_scorer.predict_perception_distribution(offer_self, total)
    col_dist = collectivist_scorer.predict_perception_distribution(offer_self, total)

    assert ind_dist['warmth_mean'] > col_dist['warmth_mean']
    assert ind_dist['adjusted_ratio'] < col_dist['adjusted_ratio']


def test_agent_exposes_cultural_profile():
    """Agent wiring should keep mental state and social scorer in sync."""
    agent = BayesianMToMAgent(cultural_template='collectivist')

    assert agent.cultural_template == 'collectivist'
    assert pytest.approx(agent.social_scorer.fairness_anchor) == agent.mental_state.fairness_anchor
    assert pytest.approx(agent.social_scorer.warmth_bias) == agent.mental_state.warmth_bias