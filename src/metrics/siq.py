"""Social Intelligence Quotient (SIQ) metric.

Defines a composite score built from four normalized components:

1. Social alignment: how close the realized observer score is to a
   configurable normative target.
2. Theory-of-mind accuracy: how well the agent's internal predictions match
   observer ratings.
3. Cross-context generalization: how small the performance drop is on
   held-out contexts.
4. Ethical consistency: frequency of episodes that satisfy minimum fairness
   constraints or explicit violation flags.

Each component scales to [0, 1] and the final SIQ score is an affine
combination controlled by weights (α, β, γ, δ) that default to equal values
and can be overridden via YAML config (see
``experiments/config/week6_siq.yaml``).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Mapping, MutableMapping, Optional, Sequence, Union

import numpy as np
import pandas as pd

from src.utils.config import load_config

RecordLike = Union[Mapping[str, Any], MutableMapping[str, Any]]
Frameable = Union[pd.DataFrame, Sequence[RecordLike]]


def _clamp(value: float, lower: float = 0.0, upper: float = 1.0) -> float:
    """Clamp *value* to the [lower, upper] interval."""

    return max(lower, min(value, upper))


@dataclass
class WeightConfig:
    """Weights (α, β, γ, δ) used to combine individual SIQ components."""

    social_alignment: float = 0.25
    theory_of_mind_accuracy: float = 0.25
    cross_context_generalization: float = 0.25
    ethical_consistency: float = 0.25

    def as_dict(self) -> Dict[str, float]:
        return {
            "social_alignment": float(self.social_alignment),
            "theory_of_mind_accuracy": float(self.theory_of_mind_accuracy),
            "cross_context_generalization": float(self.cross_context_generalization),
            "ethical_consistency": float(self.ethical_consistency),
        }


@dataclass
class SocialAlignmentConfig:
    observer_key: str = "social_score"
    target: float = 0.7


@dataclass
class TheoryOfMindConfig:
    observer_key: str = "social_score"
    prediction_key: Optional[str] = "predicted_social_score"
    actual_components: Sequence[str] = ("warmth", "competence")
    predicted_components: Sequence[str] = ("predicted_warmth", "predicted_competence")
    component_weights: Sequence[float] = (0.6, 0.4)
    max_mse: float = 0.25


@dataclass
class GeneralizationConfig:
    context_key: str = "env_name"
    reference_contexts: Sequence[str] = ("small_resources",)
    held_out_contexts: Optional[Sequence[str]] = None
    performance_key: str = "total_utility"
    epsilon: float = 1e-6


@dataclass
class EthicsConfig:
    final_agreement_key: str = "final_agreement"
    total_resources_key: str = "env_total_resources"
    violation_flag_key: Optional[str] = "ethical_violation"
    min_other_share: float = 0.25
    treat_missing_agreement_as_violation: bool = False


@dataclass
class SIQConfig:
    weights: WeightConfig = field(default_factory=WeightConfig)
    social_alignment: SocialAlignmentConfig = field(default_factory=SocialAlignmentConfig)
    theory_of_mind: TheoryOfMindConfig = field(default_factory=TheoryOfMindConfig)
    cross_context: GeneralizationConfig = field(default_factory=GeneralizationConfig)
    ethical: EthicsConfig = field(default_factory=EthicsConfig)

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any]) -> "SIQConfig":
        """Build a config from nested dicts."""

        data = payload.get("siq", payload)
        return cls(
            weights=WeightConfig(**data.get("weights", {})),
            social_alignment=SocialAlignmentConfig(**data.get("social_alignment", {})),
            theory_of_mind=TheoryOfMindConfig(**data.get("theory_of_mind", {})),
            cross_context=GeneralizationConfig(**data.get("cross_context", {})),
            ethical=EthicsConfig(**data.get("ethical", {})),
        )

    @classmethod
    def from_yaml(cls, path: Union[str, Path]) -> "SIQConfig":
        """Load settings from a YAML file."""

        return cls.from_dict(load_config(str(path)))

    def as_dict(self) -> Dict[str, Any]:
        return {
            "weights": self.weights.as_dict(),
            "social_alignment": vars(self.social_alignment),
            "theory_of_mind": {
                "observer_key": self.theory_of_mind.observer_key,
                "prediction_key": self.theory_of_mind.prediction_key,
                "actual_components": tuple(self.theory_of_mind.actual_components),
                "predicted_components": tuple(self.theory_of_mind.predicted_components),
                "component_weights": tuple(self.theory_of_mind.component_weights),
                "max_mse": self.theory_of_mind.max_mse,
            },
            "cross_context": {
                "context_key": self.cross_context.context_key,
                "reference_contexts": tuple(self.cross_context.reference_contexts),
                "held_out_contexts": None
                if self.cross_context.held_out_contexts is None
                else tuple(self.cross_context.held_out_contexts),
                "performance_key": self.cross_context.performance_key,
                "epsilon": self.cross_context.epsilon,
            },
            "ethical": {
                "final_agreement_key": self.ethical.final_agreement_key,
                "total_resources_key": self.ethical.total_resources_key,
                "violation_flag_key": self.ethical.violation_flag_key,
                "min_other_share": self.ethical.min_other_share,
                "treat_missing_agreement_as_violation": self.ethical.treat_missing_agreement_as_violation,
            },
        }


class SIQ:
    """Compute SIQ scores from per-episode records."""

    def __init__(self, config: Optional[SIQConfig] = None):
        self.config = config or SIQConfig()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def compute(self, records: Frameable) -> Dict[str, float]:
        """Compute the SIQ score for the given records.

        Args:
            records: Either a pandas DataFrame or sequence of mappings where each
                row contains observer ratings, predictions, context tags, and
                fairness metadata.

        Returns:
            Dict with per-component contributions and the final SIQ score.
        """

        df = self._ensure_dataframe(records)
        if df.empty:
            raise ValueError("Cannot compute SIQ for empty inputs")

        components = {
            "social_alignment": self._social_alignment(df),
            "theory_of_mind_accuracy": self._theory_of_mind_accuracy(df),
            "cross_context_generalization": self._cross_context_generalization(df),
            "ethical_consistency": self._ethical_consistency(df),
        }

        score = self._aggregate_components(components)
        return {"siq": score, **components}

    def compute_by_group(self, records: Frameable, group_key: str = "agent_type") -> Dict[str, Dict[str, float]]:
        """Compute SIQ per group (agent type, policy label, etc.)."""

        df = self._ensure_dataframe(records)
        if group_key not in df.columns:
            raise KeyError(f"Column '{group_key}' not present in provided records")
        results: Dict[str, Dict[str, float]] = {}
        for value, sub_df in df.groupby(group_key):
            results[str(value)] = self.compute(sub_df)
        return results

    # ------------------------------------------------------------------
    # Component helpers
    # ------------------------------------------------------------------

    def _social_alignment(self, df: pd.DataFrame) -> float:
        cfg = self.config.social_alignment
        if cfg.observer_key not in df.columns:
            return float("nan")

        mean_score = pd.to_numeric(df[cfg.observer_key], errors="coerce").dropna().mean()
        if not np.isfinite(mean_score):
            return float("nan")

        target = _clamp(cfg.target)
        max_deviation = max(target, 1.0 - target, 1e-6)
        deviation = abs(mean_score - target)
        normalized = 1.0 - min(deviation / max_deviation, 1.0)
        return _clamp(float(normalized))

    def _theory_of_mind_accuracy(self, df: pd.DataFrame) -> float:
        cfg = self.config.theory_of_mind
        if cfg.observer_key not in df.columns:
            return float("nan")

        actual = pd.to_numeric(df[cfg.observer_key], errors="coerce")

        predicted: Optional[pd.Series] = None
        composed_actual: Optional[pd.Series] = None
        if cfg.prediction_key and cfg.prediction_key in df.columns:
            predicted = pd.to_numeric(df[cfg.prediction_key], errors="coerce")
        else:
            predicted, composed_actual = self._composed_prediction(df, cfg)

        if predicted is None:
            return float("nan")

        if composed_actual is not None:
            actual = actual.fillna(composed_actual)

        paired = pd.DataFrame({"actual": actual, "pred": predicted}).dropna()
        if paired.empty:
            return float("nan")

        mse = float(((paired["actual"] - paired["pred"]) ** 2).mean())
        max_mse = max(cfg.max_mse, 1e-6)
        normalized = 1.0 - min(mse / max_mse, 1.0)
        return _clamp(normalized)

    def _composed_prediction(
        self, df: pd.DataFrame, cfg: TheoryOfMindConfig
    ) -> tuple[Optional[pd.Series], Optional[pd.Series]]:
        components_available = all(k in df.columns for k in cfg.predicted_components)
        actual_available = all(k in df.columns for k in cfg.actual_components)
        if not (components_available and actual_available):
            return None, None

        weights = np.array(cfg.component_weights, dtype=float)
        weight_sum = np.sum(weights)
        if weight_sum <= 0:
            weights = np.ones(len(weights)) / len(weights)
        else:
            weights = weights / weight_sum

        def _weighted_sum(keys: Sequence[str]) -> pd.Series:
            cols = [pd.to_numeric(df[k], errors="coerce") for k in keys]
            stacked = pd.concat(cols, axis=1)
            return (stacked * weights).sum(axis=1)

        composed_actual = _weighted_sum(cfg.actual_components)
        predicted = _weighted_sum(cfg.predicted_components)
        return predicted, composed_actual

    def _cross_context_generalization(self, df: pd.DataFrame) -> float:
        cfg = self.config.cross_context
        if cfg.context_key not in df.columns or cfg.performance_key not in df.columns:
            return float("nan")

        context = df[cfg.context_key]
        performance = pd.to_numeric(df[cfg.performance_key], errors="coerce")

        ref_mask = context.isin(cfg.reference_contexts)
        if not ref_mask.any():
            return float("nan")

        if cfg.held_out_contexts:
            held_mask = context.isin(cfg.held_out_contexts)
        else:
            held_mask = ~ref_mask

        if not held_mask.any():
            return float("nan")

        ref_mean = performance[ref_mask].mean()
        held_mean = performance[held_mask].mean()
        if not np.isfinite(ref_mean) or ref_mean <= cfg.epsilon:
            return float("nan")

        drop = max(ref_mean - held_mean, 0.0) / max(abs(ref_mean), cfg.epsilon)
        normalized = 1.0 - min(drop, 1.0)
        return _clamp(normalized)

    def _ethical_consistency(self, df: pd.DataFrame) -> float:
        cfg = self.config.ethical
        if cfg.final_agreement_key not in df.columns:
            return float("nan")

        agreements = df[cfg.final_agreement_key]
        totals = pd.to_numeric(
            df.get(cfg.total_resources_key, pd.Series(np.nan, index=df.index)),
            errors="coerce",
        )
        if cfg.violation_flag_key and cfg.violation_flag_key in df.columns:
            violation_flags = df[cfg.violation_flag_key].fillna(False).astype(bool)
        else:
            violation_flags = pd.Series(False, index=df.index)

        total_checked = 0
        consistent = 0

        for idx, agreement in agreements.items():
            if bool(violation_flags.loc[idx]):
                total_checked += 1
                continue

            total_resources = float(totals.loc[idx]) if pd.notna(totals.loc[idx]) else np.nan

            if agreement is None or (isinstance(agreement, float) and np.isnan(agreement)):
                if cfg.treat_missing_agreement_as_violation:
                    total_checked += 1
                continue

            if isinstance(agreement, (list, tuple)) and len(agreement) >= 2:
                opponent_share = agreement[1]
            elif isinstance(agreement, Mapping):
                opponent_share = agreement.get("other")
            else:
                continue

            if not np.isfinite(total_resources) and "env_total_resources" in df.columns:
                total_resources = float(pd.to_numeric(df["env_total_resources"], errors="coerce").loc[idx])

            if not np.isfinite(total_resources) or total_resources <= 0:
                continue

            pct_other = opponent_share / total_resources
            total_checked += 1
            if pct_other + 1e-9 >= cfg.min_other_share:
                consistent += 1

        if total_checked == 0:
            return float("nan")

        return _clamp(consistent / total_checked)

    def _aggregate_components(self, components: Dict[str, float]) -> float:
        weights = self.config.weights.as_dict()
        weighted_sum = 0.0
        total_weight = 0.0

        for name, value in components.items():
            weight = weights.get(name, 0.0)
            if weight <= 0.0 or not np.isfinite(value):
                continue
            weighted_sum += weight * value
            total_weight += weight

        if total_weight == 0.0:
            return float("nan")

        return _clamp(weighted_sum / total_weight)

    # ------------------------------------------------------------------
    # Utility helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _ensure_dataframe(records: Frameable) -> pd.DataFrame:
        if isinstance(records, pd.DataFrame):
            return records.copy()
        if isinstance(records, (list, tuple)):
            return pd.DataFrame(list(records))
        if isinstance(records, Mapping):
            return pd.DataFrame(records)
        raise TypeError("records must be a DataFrame or sequence of mappings")