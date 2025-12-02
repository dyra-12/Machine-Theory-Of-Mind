"""Unit tests for the SIQ metric."""

from __future__ import annotations

import math
import sys
from pathlib import Path

import pytest

sys.path.append(str(Path(__file__).parent.parent))

from src.metrics.siq import (  # noqa: E402
    SIQ,
    SIQConfig,
    WeightConfig,
)


def _base_records():
    return [
        {
            "agent_type": "bayesian_mtom",
            "social_score": 0.75,
            "predicted_social_score": 0.72,
            "warmth": 0.74,
            "competence": 0.76,
            "predicted_warmth": 0.73,
            "predicted_competence": 0.74,
            "env_name": "small_resources",
            "total_utility": 1.45,
            "final_agreement": [6, 4],
            "env_total_resources": 10,
            "ethical_violation": False,
        },
        {
            "agent_type": "bayesian_mtom",
            "social_score": 0.73,
            "predicted_social_score": 0.7,
            "warmth": 0.71,
            "competence": 0.75,
            "predicted_warmth": 0.69,
            "predicted_competence": 0.73,
            "env_name": "small_resources",
            "total_utility": 1.4,
            "final_agreement": [5, 5],
            "env_total_resources": 10,
            "ethical_violation": False,
        },
        {
            "agent_type": "bayesian_mtom",
            "social_score": 0.68,
            "predicted_social_score": 0.63,
            "warmth": 0.66,
            "competence": 0.72,
            "predicted_warmth": 0.62,
            "predicted_competence": 0.69,
            "env_name": "long_horizon",
            "total_utility": 1.1,
            "final_agreement": [7, 3],
            "env_total_resources": 10,
            "ethical_violation": False,
        },
        {
            "agent_type": "bayesian_mtom",
            "social_score": 0.6,
            "predicted_social_score": 0.48,
            "warmth": 0.58,
            "competence": 0.65,
            "predicted_warmth": 0.46,
            "predicted_competence": 0.61,
            "env_name": "long_horizon",
            "total_utility": 0.9,
            "final_agreement": [9, 1],
            "env_total_resources": 10,
            "ethical_violation": True,
        },
    ]


def _records_without_direct_predictions():
    records = []
    for row in _base_records():
        cloned = dict(row)
        cloned.pop("predicted_social_score", None)
        records.append(cloned)
    return records


def test_siq_components_and_score_range():
    siq = SIQ()
    result = siq.compute(_base_records())

    assert 0.0 <= result["social_alignment"] <= 1.0
    assert 0.0 <= result["theory_of_mind_accuracy"] <= 1.0
    assert 0.0 <= result["cross_context_generalization"] <= 1.0
    assert 0.0 <= result["ethical_consistency"] <= 1.0
    assert 0.0 <= result["siq"] <= 1.0


def test_siq_falls_back_to_component_predictions():
    siq = SIQ()
    result = siq.compute(_records_without_direct_predictions())
    # Ensure we produced a finite ToM score even without direct prediction key
    assert math.isfinite(result["theory_of_mind_accuracy"])


def test_siq_respects_weight_overrides():
    config = SIQConfig(
        weights=WeightConfig(
            social_alignment=1.0,
            theory_of_mind_accuracy=0.0,
            cross_context_generalization=0.0,
            ethical_consistency=0.0,
        )
    )
    siq = SIQ(config)
    result = siq.compute(_base_records())
    assert result["siq"] == pytest.approx(result["social_alignment"])


def test_siq_config_from_dict_handles_nested_structure():
    payload = {
        "siq": {
            "weights": {"social_alignment": 0.4, "theory_of_mind_accuracy": 0.3, "cross_context_generalization": 0.2, "ethical_consistency": 0.1},
            "social_alignment": {"target": 0.8},
            "theory_of_mind": {"max_mse": 0.5},
        }
    }
    config = SIQConfig.from_dict(payload)
    assert config.weights.social_alignment == pytest.approx(0.4)
    assert config.social_alignment.target == pytest.approx(0.8)
    assert config.theory_of_mind.max_mse == pytest.approx(0.5)