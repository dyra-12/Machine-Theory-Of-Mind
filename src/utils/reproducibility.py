"""Utilities for reproducible experiments: seeding RNGs and device selection.

This module centralizes recommended reproducibility primitives used across the
experiments. It provides:

- `set_global_seeds(seed)` — sets Python, NumPy and (if available) PyTorch RNGs
    to the provided integer seed and toggles deterministic cuDNN flags where
    appropriate.
- `make_numpy_generator(seed)` — returns a `numpy.random.Generator` instance
    seeded deterministically (preferred for local randomness control).
- `get_preferred_device(prefer_cuda=True)` — returns a `torch.device('cuda')`
    when CUDA is available and preferred, otherwise `torch.device('cpu')`.

Usage examples
--------------
>>> from src.utils.reproducibility import set_global_seeds, make_numpy_generator, get_preferred_device
>>> set_global_seeds(42)
>>> rng = make_numpy_generator(42)
>>> device = get_preferred_device()

Notes
-----
- Deterministic settings for CUDA (cuDNN) may reduce performance and are not
    a perfect guarantee of reproducibility across different GPUs or CUDA
    versions. Use fixed seeds + logged config files + saved checkpoints for
    strongest reproducibility guarantees.
"""
import random
import os
from typing import Optional

import numpy as np


def set_global_seeds(seed: Optional[int]) -> None:
    """Set seeds for Python, NumPy and (optionally) PyTorch.

    Args:
        seed: integer seed to set. If `None`, function is a no-op.
    """
    if seed is None:
        return

    try:
        seed = int(seed)
    except Exception:
        return

    random.seed(seed)
    np.random.seed(seed)
    os.environ['PYTHONHASHSEED'] = str(seed)

    # Optional: set torch seeds if available
    try:
        import torch

        torch.manual_seed(seed)
        if torch.cuda.is_available():
            torch.cuda.manual_seed_all(seed)

        # Recommended deterministic flags (may impact performance)
        torch.backends.cudnn.deterministic = True
        torch.backends.cudnn.benchmark = False
    except Exception:
        # Torch not installed or failed to configure — that's fine for reproducibility fallback
        pass


def make_numpy_generator(seed: Optional[int] = None) -> np.random.Generator:
    """Return a NumPy ``Generator`` instance seeded with ``seed``.

    Prefer this generator for per-experiment randomness instead of the global
    NumPy RNG when you need reproducible but independent streams.

    Args:
        seed: integer seed or ``None`` to use a nondeterministic seed.

    Returns:
        A ``numpy.random.Generator`` instance.
    """
    if seed is None:
        return np.random.default_rng()
    return np.random.default_rng(int(seed))


def get_preferred_device(prefer_cuda: bool = True):
    """Return a device object for computation.

    If PyTorch is available, prefer CUDA when ``prefer_cuda`` is True and a
    CUDA device is present. Otherwise return a CPU device. This helper keeps
    device-selection in one place so experiments can document/override it.

    Returns:
        `torch.device` if PyTorch is installed, otherwise the string `'cpu'`.
    """
    try:
        import torch

        if prefer_cuda and torch.cuda.is_available():
            return torch.device("cuda")
        return torch.device("cpu")
    except Exception:
        # PyTorch not installed — return a simple string indicator for callers
        return "cpu"
