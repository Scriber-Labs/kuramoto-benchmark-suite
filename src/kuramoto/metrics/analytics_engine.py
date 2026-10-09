"""
src/kuramoto/metrics/analytics_engine.py

Unified analysis engine computing structural invariants, phase-space contractions,
and spectral metrics across non-uniform network topologies.
"""

from __future__ import annotations

from typing import Dict, NamedTuple

import numpy as np
from numpy.typing import NDArray

# Seamless local imports inside your project layout
from kuramoto.analysis.graphs import build_adjacency
from kuramoto.analysis.spectral import compute_psd, compute_spectral_decomposition

# ------------------------------------------------------------------------------
# 0️⃣ Definitions, Constants & Types
# ------------------------------------------------------------------------------


class ComprehensiveMetrics(NamedTuple):
    """Aggregated structural and frequency domain diagnostics."""

    energy_trajectory: NDArray[np.floating]
    lambda_trajectory: NDArray[np.floating]
    spectral_frequencies: NDArray[np.floating]
    spectral_psd_mean: NDArray[np.floating]
    energy_decomposition: Dict[str, float]
    total_energy_drift: float


# ------------------------------------------------------------------------------
# 1️⃣ Public API
# ------------------------------------------------------------------------------


def compute_comprehensive_diagnostics(
    rotor_history: NDArray[np.complexfloating] | NDArray[np.floating],
    times: NDArray[np.floating],
    K: float,
    adjacency_in: NDArray[np.floating] | None = None,
    target_freq: float | None = None,
    blade_idx: int = 1,
) -> ComprehensiveMetrics:
    """
    Computes Hamiltonian invariants, phase-space contractions, and spectral breakdowns
    by binding graphs.py topology and spectral.py Fourier tools.

    Parameters
    ----------
    rotor_history : NDArray[np.complexfloating] | NDArray[np.floating]
        Simulation history of rotors. If complex, shape is (T, N).
        If real array, shape is (T, N, D) or (T, N, 2+).
    times : NDArray[np.floating]
        Time evaluation array of shape (T,).
    K : float
        Coupling strength.
    adjacency_in : NDArray[np.floating] | None, optional
        Adjacency matrix of the graph. If None, a fully connected graph is assumed.
    target_freq : float | None, optional
        Base frequency of interest for spectral decomposition. If None, inferred
        from peak PSD.
    blade_idx : int, optional
        Index of the bivector component if rotors are represented as real components.
        Default is 1.

    Returns
    -------
    ComprehensiveMetrics
        Named tuple containing energy trajectory, lambda trajectory, frequencies,
        mean PSD, spectral decomposition, and total energy drift.
    """
    rotors = np.asarray(rotor_history)
    T, N = rotors.shape[0], rotors.shape[1]

    # Infer sampling timestep and frequency
    dt = float(times[1] - times[0]) if len(times) > 1 else 1.0
    fs = 1.0 / dt

    # 1. Resolve network structure using graphs.py matrix factory
    A = build_adjacency(N, adjacency_in)

    # 2. Map coordinates cleanly from Geometric Algebra representation layout
    if np.iscomplexobj(rotors):
        scalars = rotors.real
        bivectors = -rotors.imag
    else:
        scalars = rotors[..., 0]
        bivectors = rotors[..., blade_idx]

    # Calculate bivector velocities via smooth time-gradients (Omega = -2 * dR/dt * R_dagger)
    d_scalars = np.gradient(scalars, times, axis=0)
    d_bivectors = np.gradient(bivectors, times, axis=0)
    velocities = 2.0 * (bivectors * d_scalars - scalars * d_bivectors)

    # 3. Structural invariant loops (Vectorized over time frames)
    kinetic_energy = 0.5 * np.mean(velocities**2, axis=1)
    potential_energy = np.zeros(T)
    lambda_trajectory = np.zeros(T)

    for t in range(T):
        s_t = scalars[t, :, np.newaxis]
        b_t = bivectors[t, :, np.newaxis]
        cos_matrix = (s_t @ s_t.T) + (b_t @ b_t.T)

        # Non-uniform matrix potential masking
        potential_energy[t] = -(K / N) * np.sum(A * cos_matrix) / N
        # Phase-space volume contraction rate tracking diagonal elements of system Jacobian
        lambda_trajectory[t] = -(K / N) * np.sum(A * cos_matrix)

    total_energy = kinetic_energy + potential_energy
    total_drift = float(np.max(total_energy) - np.min(total_energy))

    # 4. Frequency-domain processing utilizing spectral.py algorithms
    freqs, pxx = compute_psd(velocities, fs=fs, nperseg=min(256, T // 2))
    psd_mean = np.mean(pxx, axis=1)

    # Infer target base frequency if none was provided
    if target_freq is None:
        target_freq = float(freqs[np.argmax(psd_mean)])

    energy_decomp = compute_spectral_decomposition(freqs, pxx, target_freq=target_freq)

    return ComprehensiveMetrics(
        energy_trajectory=total_energy,
        lambda_trajectory=lambda_trajectory,
        spectral_frequencies=freqs,
        spectral_psd_mean=psd_mean,
        energy_decomposition=energy_decomp,
        total_energy_drift=total_drift,
    )


# ------------------------------------------------------------------------------
# 💨 Smoke Tests
# ------------------------------------------------------------------------------


def _run_smoke_test() -> None:
    """Sanity check for analytics engine."""
    print("💨 Running analytics engine smoke tests...")
    t = np.linspace(0, 10, 200)
    theta = np.outer(t, np.array([1.0, 1.2, 0.8]))
    # Represent as complex rotors exp(-I theta / 2) = cos(theta/2) - I sin(theta/2)
    # scalars = cos(theta/2), bivectors = sin(theta/2) -> rotor = cos - 1j*sin
    rotors = np.cos(theta / 2.0) - 1j * np.sin(theta / 2.0)

    metrics = compute_comprehensive_diagnostics(
        rotor_history=rotors,
        times=t,
        K=1.5,
    )
    assert metrics.energy_trajectory.shape == (200,)
    assert metrics.lambda_trajectory.shape == (200,)
    assert len(metrics.spectral_frequencies) > 0
    assert "fundamental" in metrics.energy_decomposition
    print("✅ All analytics engine smoke tests passed.")


# ------------------------------------------------------------------------------
# 🔥 Entry Point
# ------------------------------------------------------------------------------


def main() -> None:
    _run_smoke_test()


if __name__ == "__main__":
    main()
