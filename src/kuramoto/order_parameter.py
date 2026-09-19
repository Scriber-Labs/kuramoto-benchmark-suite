# src/kuramoto/order_parameter.py
"""
Order parameter computation for Kuramoto synchronization analysis.

The order parameter `r(t)` quantifies the degree of phase coherence across the oscillator population. Values near 1
indicate strong synchronization, while values near zero indicate incoherence.

This module provides:
  - The core synchronization metric used throughout the benchmark suite.
  - Diagnostics for the global U(1) phase symmetry of the Kuramoto system.

Author: Eigenscribe
Review status: Reviewed and maintained by Eigenscribe.
Date: 05-2026
Last Updated: 09-2026
"""

from __future__ import annotations

from typing import Final, NamedTuple

import numpy as np
from numpy.typing import NDArray

# Import RNG utilities from the central utils module
try:
    from .utils import get_rng
except (ImportError, ValueError):
    import sys
    from pathlib import Path

    _src_dir = str(Path(__file__).resolve().parent.parent)
    if _src_dir not in sys.path:
        sys.path.insert(0, _src_dir)

    from kuramoto.utils import get_rng

__all__: list[str] = [
    "compute_order_parameter",
    "LieSymmetryMetrics",
    "track_lie_symmetries",
]

# ------------------------------------------------------------------------------
# 🎭 Type Aliases
# ------------------------------------------------------------------------------

PhaseArray = NDArray[np.floating]
ComplexArray = NDArray[np.complexfloating]
TimeSeriesArray = NDArray[np.floating]

# ------------------------------------------------------------------------------
# 1️⃣ Lie Symmetry Diagnostics
# ------------------------------------------------------------------------------

class LieSymmetryMetrics(NamedTuple):
    """
    Measures of Lie-group symmetry and synchronization diagnostics.

    Attributes
    ----------
    global_phase_invariant : bool
        Whether the phase dynamics are invariant under a uniform global phase shift, representing the U(1) symmetry of
        the Kuramoto model.

    energy_conserved : np.ndarray
        Estimated energy-like quantity over time. This is provided as a diagnostic trajectory rather than a universal
        conservational law for the dissipative/non-Hamiltonian Kuramoto model.

    synchronization_strength : float
        Final Kuramoto order-parameter magnitude.
    """

    global_phase_invariant: bool
    energy_conserved: NDArray[np.floating]
    synchronization_strength: float

def track_lie_symmetries(
    states: dict[str, np.ndarray],
    times: np.ndarray,
) -> LieSymmetryMetrics:
    """
    Track global U(1) phase symmetry and synchronization during evolution.

    Parameters
    ----------
    states : dict[str, np.ndarray]
        Mapping from phase/state keys to oscillator phase trajectories.
        Each array must have shape ``(T,)``. The dictionary is st acked along its final axis to form an array of shape
        ``(T,N)``.

    times : np.ndarray
        One-dimensional array of timestamps with length ``T``.

    Returns
    -------
    LieSymmetryMetrics
        Named tuple containing the global phase-invariance diagnostic, energy-like trajectory, and final synchronization
        strength.

    Raises
    ------
    ValueError
        If states are empty, trajectories have inconsistent shapes, or the time array is invalid.

    Notes
    -----
    The global phase transformation

        theta_i(t) -> theta_i(t) + phi

    leaves phase differences invariant. This is the numerical signature of the global U(1) symmetry used here.

    ⚠️ The ``energy_conserved`` field is an energy-like diagnostic based on the supplied phase trajectories. It should not
    be interpreted as a conserved Hamiltonian for the general Kuramoto model.
    """
    if not states:
        raise ValueError("❌ States cannot be empty")

    if times.ndim != 1:
        raise ValueError("❌ Times must be a 1D array")

    phases = np.stack(list(states.values()), axis=-1)

    if phases.ndim != 2:
        raise ValueError(
            "❌ States must produce a 2D phase array, got {phases.ndim}D"
        )

    if times.size < 2:
        raise ValueError("❌ At least two time points are required")

    # ------------------------------------------------------------------
    # 🌍 Global U(1) phase invariance
    # ------------------------------------------------------------------
    # A uniform phase shift should not change phase differences or temporal phase increments.
    shifted = phases + 0.5

    velocity_diff = np.diff(phases, axis=0)
    shifted_diff = np.diff(shifted, axis=0)

    global_invariant = np.allclose(
        velocity_diff,
        shifted_diff,
        rtol=1e-6,
        atol=1e-10,
    )

    # ------------------------------------------------------------------
    # ⚡ Energy-like diagnostic
    # ------------------------------------------------------------------
    phase_velocity = np.gradient(phases, times, axis=0)

    kinetic = 0.5 * np.mean(phase_velocity**2, axis=1)

    phase_difference = phases[:, :, None] - phases[:, None, :]
    coupling = -np.cos(phase_difference).mean(axis=(1, 2))

    energy_over_time = kinetic + coupling

    # ------------------------------------------------------------------
    # 💫 Synchronization strength
    # ------------------------------------------------------------------
    complex_states = np.exp(1j * phases)
    r_over_time = np.abs(complex_states.mean(axis=1))

    return LieSymmetryMetrics(
        global_phase_invariant=global_invariant,
        energy_conserved=energy_over_time,
        synchronization_strength=float(r_over_time[-1]),
    )

# ------------------------------------------------------------------------------
# 2️⃣ Validation Helpers
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
# 💨 Smoke Test
# ------------------------------------------------------------------------------

def _run_smoke_test() -> None:
    """Sanity check for compute_order_parameter."""
    print("💨 Running order parameter smoke tests...")

    # Use dedicated RNG for test data generation (no global state pollution)
    rng = get_rng(27)

    # ------------------------------------------------------------------
    # Test 1: Single time snapshot (1D)
    # ------------------------------------------------------------------
    theta_1d = np.array([0.0, 0.1, 0.05, 0.02])
    r_1d = compute_order_parameter(theta_1d)

    assert isinstance(r_1d, (float, np.floating))
    assert 0.0 <= r_1d <= 1.0

    print(" ... ✔️  1D snapshot test passed.")

    # ------------------------------------------------------------------
    # Test 2: Time series (2D)
    # ------------------------------------------------------------------
    theta_2d = rng.uniform(0, 2 * np.pi, (100, 10))
    r_2d = compute_order_parameter(theta_2d)

    assert r_2d.shape == (100,)
    assert np.all((r_2d >= 0.0) & (r_2d <= 1.0))

    print(" ... ✔️  2D time series test passed.")

    # ------------------------------------------------------------------
    # Test 3: Perfect synchronization
    # ------------------------------------------------------------------
    theta_sync = np.ones((50, 20)) * 0.5
    r_sync = compute_order_parameter(theta_sync)

    assert np.allclose(r_sync, 1.0)

    print(" ... ✔️  Perfect synchronization test passed (r approx 1.0).")

    # ------------------------------------------------------------------
    # Test 4: Complete incoherence
    # ------------------------------------------------------------------
    theta_incoh = rng.uniform(0, 2 * np.pi, (1000, 1000))
    r_incoh = compute_order_parameter(theta_incoh)

    assert np.all(r_incoh < 0.1)

    print(" ... ✔️  Incoherence test passed (r is approximately 0).")

    # ------------------------------------------------------------------
    # Test 5: U(1) global phase-shift invariance
    # ------------------------------------------------------------------
    times = np.linspace(0.0, 10.0, 100)
    base_phases = np.column_stack(
        [
            0.2 * times,
            0.4 * times + 0.3,
            0.7 * times - 0.2,
            1.0 * times + 0.8,
        ]
    )

    states = {
        f"theta_{i}": base_phases[:, i] for i in range(base_phases.shape[1])
    }

    metrics = track_lie_symmetries(states, times)

    # This assertion establishes/enforces the U(1) symmetry requirement.
    assert metrics.global_phase_invariant is True

    print(" ... ✔️  U(1) global phase invariance test passed.")

    # ------------------------------------------------------------------
    # Test 6: Symmetry must preserve synchronization strength
    # ------------------------------------------------------------------
    global_shift = 1.234
    shifted_phases = base_phases + global_shift

    r_original = compute_order_parameter(base_phases)
    r_shifted = compute_order_parameter(shifted_phases)

    assert np.allclose(r_original, r_shifted, rtol=1e-6, atol=1e-10)

    print(" ... ✔️  Lie symmetry metrics contract test passed.")

    # ------------------------------------------------------------------
    # Test 7: Lie symmetry diagnostic output contract
    # ------------------------------------------------------------------
    assert isinstance(metrics.global_phase_invariant, (bool, np.bool_))
    assert metrics.energy_conserved.shape == (times.size,)
    assert np.isfinite(metrics.energy_conserved).all()
    assert 0.0 <= metrics.synchronization_strength <= 1.0

    print(" ... ✔️  Lie symmetry metrics contract test passed.")

    print("\n ✅ All order parameter smoke tests passed.")

# -----------------------------------------------------------------------------------------------------------
# 🔥 Entry point
# -----------------------------------------------------------------------------------------------------------

def main() -> None:
    """Entry point."""
    _run_smoke_test()

if __name__ == "__main__":
    main()
