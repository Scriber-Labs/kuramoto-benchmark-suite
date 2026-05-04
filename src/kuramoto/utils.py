# src/kuramoto/utils.py
"""
utils.py

Utility helpers for the Kuramoto benchmark suite.

These functions are deliberately designed to be lightweight. Specifically, they 
do not depend on any project-specific modules. This makes them easy to reuse in 
notebooks and implement in future projects.

Author: Eigenscribe
Date: May 2026
"""

from __future__ import annotations

import random
from typing import Optional

import numpy as np
from numpy.typing import NDArray

# ------------------------------------------------------------------------------ #
# 1️⃣ Core definitions
# ------------------------------------------------------------------------------ #

def get_rng(seed: Optional[int] = None) -> np.random.Generator:
    """
    Get a numpy random number generator.

    Parameters
    ----------
    seed : int, optional
        Seed for the RNG.

    Returns
    -------
    np.random.Generator
        A numpy random number generator.
    """
    return np.random.default_rng(seed)


def wrap_phase(theta: NDArray[np.floating]) -> NDArray[np.floating]:
    """
    Wrap phases to the interval [0, 2*pi).

    Parameters
    ----------
    theta : NDArray
        Array of phases.

    Returns
    -------
    NDArray
        Wrapped phases.
    """
    return np.mod(theta, 2 * np.pi)

# ------------------------------------------------------------------------------ #
# 2️⃣ Public API
# ------------------------------------------------------------------------------ #

def set_global_seed(
    seed: int,
    *,
    deterministic: bool = False
) -> None:
    """
    Seed the random number generators used throughout the project repository.

    Parameters
    ----------
    seed : int
        The integer seed to initialize all RNGs.
    deterministic : bool, default=False
        This parameter is kept for backward compatibility but currently has no effect 
        as PyTorch dependency has been removed.

    Notes
    -----
    - Python's ``random`` module and NumPy are seeded.
    """
    random.seed(seed)
    np.random.seed(seed)

# ------------------------------------------------------------------------------ #
# 4️⃣ Smoke tests / example usage
# ------------------------------------------------------------------------------ #

def _run_smoke_test() -> None:
    """
    Run sanity checks for utility functions.
    """
    print("💨 Running utils smoke test...")

    # Test set_global_seed
    set_global_seed(27, deterministic=True)

    # Test get_rng
    rng = get_rng(27)
    val = rng.random()
    assert isinstance(val, float)

    # Test wrap_phase
    theta = np.array([0.0, 2 * np.pi, 3 * np.pi])
    wrapped = wrap_phase(theta)
    assert np.allclose(wrapped, [0.0, 0.0, np.pi])

    print("✔️ utils.py sanity check passed")

# ------------------------------------------------------------------------------ #
# 5️⃣ Entry point
# ------------------------------------------------------------------------------ #

def main() -> None:
    """
    Main entry point for smoke tests.
    """
    _run_smoke_test()

if __name__ == "__main__":
    main()
