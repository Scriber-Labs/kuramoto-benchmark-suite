# src/kuramoto/utils/phase.py
"""
phase.py

Phase-angle helpers for the Kuramoto benchmark suite.

Lightweight, project-agnostic utilities for working with oscillator phase
angles. Kept dependency-free (NumPy only) so they are trivially reusable in
notebooks and downstream projects.

Author: Eigenscribe
Date: May 2026
"""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray

__all__ = ["wrap_phase"]

# ------------------------------------------------------------------------------ #
# 1️⃣ Public API
# ------------------------------------------------------------------------------ #


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
# 💨 Smoke tests / example usage
# ------------------------------------------------------------------------------ #


def _run_smoke_test() -> None:
    """Sanity check for phase utilities."""
    print("💨 Running phase utils smoke test...")

    theta = np.array([0.0, 2 * np.pi, 3 * np.pi])
    wrapped = wrap_phase(theta)
    assert np.allclose(wrapped, [0.0, 0.0, np.pi])

    print("✔️ phase.py sanity check passed")


# ------------------------------------------------------------------------------ #
# 🔥 Entry point
# ------------------------------------------------------------------------------ #


def main() -> None:
    """Main entry point for smoke tests."""
    _run_smoke_test()


if __name__ == "__main__":
    main()
