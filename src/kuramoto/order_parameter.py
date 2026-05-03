# src/kuramoto/order_parameter.py

"""
Order parameter computation for Kuramoto synchronization analysis.

The order parameter `r(t)` quantifies the degree of phase coherence across the oscillator population. Values near 1 indicate strong synchronization, while values near zero indicate incoherence.

This module provides the core synchronization metric used throughout the benchmark suite.

Author: Eigenscribe
Development note: LLM assistance was used during construction; implementation has been reviewed and adapted for this project.
Review status: Reviewed and maintained by Eigenscribe.
Date: 05-2026
"""

from __future__ import annotations

from typing import Final
from numpy.typing import NDArray

import numpy as np

__all__: list[str] = [
    "compute_order_parameter",
]

# ------------------------------------------------------------------------------
# 0️⃣ Type Aliases
# ------------------------------------------------------------------------------
PhaseArray = NDArray[np.floating]
ComplexArray = NDArray[np.complexfloating]
TimeSeriesArray = NDArray[np.floating]

# ------------------------------------------------------------------------------
# 1️⃣ Validation Helpers
# ------------------------------------------------------------------------------

def _validate_phase_array(theta: PhaseArray) -> None:
    """
    Validate that the input array is suitable for order parameter computation.

    Parameters
    ----------
    theta : PhaseArray
        Phase array to validate.

    Raises
    ------
    ValueError
        If array is empty or has invalid dimensions.
    """
    if theta.size == 0:
        raise ValueError("✖️ Phase array cannot be empty")
    if theta.ndim not in (1, 2):
        raise ValueError(f"✖️ Phase array must be 1D or 2D, got {theta.ndim}D")

# ------------------------------------------------------------------------------
# 2️⃣ Core Computation
# ------------------------------------------------------------------------------
def compute_order_parameter(theta: PhaseArray) -> TimeSeriesArray:
    """
    Compute the Kuramoto order parameter r(t) from phase trajectories.

    This function calculates the magnitude of the mean phasor, providing a quantitative measure of global synchronization in the system.

    - **r approx 1**: Strong synchronization (phases clustered).
    - **r approx 0**: Incoherence (phases uniformly distributed).
    - **0 < r < 1**: Partial synchronization.

    Parameters
    ----------
    theta : PhaseArray
        Phase trajectories. Can be:
            - 1D array of shape (N,) for a single time snapshot.
            - 2D array of shape (T, N) for time series data.

    Returns
    -------
    TimeSeriesArray
        Order parameter values:
            - Scalar (0D) if input is 1D.
            - 1D array of shape (T,) if input is 2D.

    Raises
    ------
    ValueError
        If input array is empty or has invalid dimensions.

    """
