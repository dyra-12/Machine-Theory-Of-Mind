"""Adversarial observer variants that inject noise or misleading feedback."""
from __future__ import annotations

from typing import Tuple, Optional, Sequence
import numpy as np

from src.observers.simple_observer import SimpleObserver
from src.models.negotiation_state import NegotiationState


class AdversarialObserver(SimpleObserver):
    """Observer that perturbs social feedback to stress-test agents.

    Parameters
    ----------
    noise_std:
        Standard deviation of Gaussian noise added to each signal dimension.
    deception_prob:
        Probability of inverting the signal (interpreting generous acts as selfish
        and vice versa).
    inversion_strength:
        Magnitude multiplier applied when deception triggers.
    bias:
        Constant offset applied to (warmth_delta, competence_delta) which can
        emulate cultural or framing biases.
    dropout_prob:
        Probability that the signal is fully replaced with noise, simulating a
        missing or scrambled communication channel.
    seed:
        Optional seed to make the adversarial process reproducible in tests.
    """

    def __init__(
        self,
        warmth_weight: float = 0.6,
        competence_weight: float = 0.4,
        *,
        noise_std: float = 0.35,
        deception_prob: float = 0.45,
        inversion_strength: float = 1.0,
        bias: Optional[Sequence[float]] = None,
        dropout_prob: float = 0.1,
        seed: Optional[int] = None,
    ) -> None:
        super().__init__(warmth_weight=warmth_weight, competence_weight=competence_weight)
        self.noise_std = max(0.0, float(noise_std))
        self.deception_prob = float(np.clip(deception_prob, 0.0, 1.0))
        self.inversion_strength = max(0.0, float(inversion_strength))
        bias = bias or (0.0, 0.0)
        self.bias = np.array(bias, dtype=float)
        if self.bias.shape != (2,):
            raise ValueError("bias must have exactly two elements for warmth/competence")
        self.dropout_prob = float(np.clip(dropout_prob, 0.0, 1.0))
        self._rng = np.random.default_rng(seed)

    def _gaussian_noise(self) -> np.ndarray:
        if self.noise_std == 0.0:
            return np.zeros(2)
        return self._rng.normal(0.0, self.noise_std, size=2)

    def observe_action(
        self,
        state: NegotiationState,
        action: Tuple[int, int],
        agent_id: int,
    ) -> Tuple[float, float]:
        base = np.array(super().observe_action(state, action, agent_id), dtype=float)
        signal = base.copy()

        # Intentional deception: flip the sign of the base signal and magnify it.
        if self.deception_prob > 0 and self._rng.random() < self.deception_prob:
            signal = -signal * (self.inversion_strength if self.inversion_strength > 0 else 1.0)

        # Apply systematic bias and additive Gaussian noise.
        signal += self.bias
        signal += self._gaussian_noise()

        # Dropout simulates a totally noisy channel regardless of the original action.
        if self.dropout_prob > 0 and self._rng.random() < self.dropout_prob:
            signal = self._gaussian_noise()

        return float(signal[0]), float(signal[1])

    @property
    def reliability(self) -> float:
        base = 1.0 - self.deception_prob - 0.5 * self.dropout_prob
        return float(np.clip(base, 0.0, 1.0))

    def describe_channel(self) -> dict:
        return {
            "noise_std": self.noise_std,
            "deception_prob": self.deception_prob,
            "dropout_prob": self.dropout_prob,
            "inversion_strength": self.inversion_strength,
            "bias": self.bias.tolist(),
            "reliability": self.reliability,
        }
