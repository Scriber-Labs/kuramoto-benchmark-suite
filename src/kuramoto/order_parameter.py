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

# Import RNG utilities from the central utils module
from .utils import get_rng

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
        raise ValueError("Error: Phase array cannot be empty")
    if theta.ndim not in (1, 2):
        raise ValueError(f"Error: Phase array must be 1D or 2D, got {theta.ndim}D")

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

    Examples
    --------
    >>> import numpy as np
    >>> theta = np.array([[0.0, 0.1, 0.05], [0.5, 0.6, 0.55]])
    >>> r = compute_order_parameter(theta)
    >>> r.shape
    (2,)

    Notes
    -----
    The computation uses vectorized operations for efficiency. For detailed mathematical derivations and physical interpretations, refer to the associated [lab notebook entry](https://scriber-labs.github.io/research-notebook/kuramoto-benchmark/kuramoto_order_parameter/).
    """
    _validate_phase_array(theta)

    # Convert to complex exponential representation
    phase_complex = np.exp(1j * theta)

    # Compute mean across oscillators (axis 1 for 2D, implicit for 1D)
    if theta.ndim == 2:
        r = np.abs(np.mean(phase_complex, axis=1))
    else:
        r = np.abs(np.mean(phase_complex))

    return r

# ------------------------------------------------------------------------------
# 3️⃣ Smoke Test
# ------------------------------------------------------------------------------

def _run_smoke_test() -> None:
    """Sanity check for compute_order_parameter."""
    print("💨 Running order parameter smoke tests...")

    # Use dedicated RNG for test data generation (no global state pollution)
    rng = get_rng(27)

    # Test 1: Single time snapshot (1D)
    theta_1d = np.array([0.0, 0.1, 0.05, 0.02])
    r_1d = compute_order_parameter(theta_1d)
    assert isinstance(r_1d, (float, np.floating))
    assert 0.0 <= r_1d <= 1.0
    print("    ✔️ 1D snapshot test passed")

    # Test 2: Time series (2D)
    theta_2d = rng.uniform(0, 2*np.pi, (100, 10))  # 100 time steps, 10 oscillators
    r_2d = compute_order_parameter(theta_2d)
    assert r_2d.shape == (100,)
    assert np.all((r_2d >= 0.0) & (r_2d <= 1.0))
    print("    ✔️ 2D time series test passed")

    # Test 3: Perfect synchronization
    theta_sync = np.ones((50, 20)) * 0.5  # All phases identical
    r_sync = compute_order_parameter(theta_sync)
    assert np.allclose(r_sync, 1.0)
    print("    ✔️ Perfect synchronization test passed (r approx 1.0)")

    # Test 4: Complete incoherence (random phases average to ~0)
    theta_incoh = rng.uniform(0, 2*np.pi, (1000, 1000))
    r_incoh = compute_order_parameter(theta_incoh)
    # Large N should give r close to 0, but not exactly 0
    assert np.all(r_incoh < 0.1)
    print("    ✔️ Incoherence test passed (r is approximately 0)")

    print("\n✅ All order parameter smoke tests passed.")

def main() -> None:
    """Entry point."""
    _run_smoke_test()

if __name__ == "__main__":
    main()
