"""Utilities for reproducible experiments: seeding RNGs and optional frameworks.

Provides `set_global_seeds(seed)` which sets python, numpy and (if available) torch seeds
and configures deterministic behavior where appropriate.
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
