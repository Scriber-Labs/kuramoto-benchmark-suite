"""
ZBW Kuramoto Data Generator — Mesoscale ensemble with golden-ratio frequencies.

Specialized model variant featuring:
1. **The phi-Shield**: Worst-case irrational frequency distribution based on the Golden Ratio.
2. **Sparse Coprime Adjacency**: Network topology where nodes couple only if their indices are coprime.
3. **LED Macroscopic Vector Torque**: External driving field modeling Critical Flicker Fusion (CFF) effects.
"""

from __future__ import annotations

import math
from typing import Final

import numpy as np
from numpy.typing import NDArray

# 0️⃣ Definitions, Constants & Types

GOLDEN_RATIO: Final[float] = (1.0 + np.sqrt(5.0)) / 2.0
"""Golden ratio φ ≈ 1.618 used for irrational frequency spacing."""


# 1️⃣ Public API


class ZBWKuramotoDataGenerator:
    """
    Scriber Labs Data Generator for Mesoscale ZBW Ensembles.

    Enforces a golden-ratio frequency grid and a sparse coprime adjacency lattice
    driven by an external macroscopic LED torque operator.

    Parameters
    ----------
    num_oscillators : int
        Number of oscillators in the ensemble.
    omega_0 : float
        Base natural frequency.
    coupling_K : float
        Coupling strength parameter.

    Attributes
    ----------
    N : int
        Number of oscillators.
    omega_0 : float
        Base natural frequency.
    K : float
        Coupling strength.
    phi : float
        Golden ratio constant.
    intrinsic_frequencies : NDArray[np.floating]
        Golden-ratio spaced frequency array.
    adjacency_matrix : NDArray[np.floating]
        Coprime-index adjacency matrix.
    coupling_matrix : NDArray[np.floating]
        Scaled coupling matrix (K/N * adjacency).
    """

    def __init__(
        self,
        num_oscillators: int = 100,
        omega_0: float = 1.0,
        coupling_K: float = 0.5,
    ) -> None:
        self.N = num_oscillators
        self.omega_0 = omega_0
        self.K = coupling_K

        # 1. The phi-Shield: Worst-case irrational frequency distribution
        self.phi: float = GOLDEN_RATIO
        self.intrinsic_frequencies: NDArray[np.floating] = np.array(
            [self.omega_0 * (self.phi**i) for i in range(self.N)]
        )

        # 2. Sparse Coprime Network Adjacency Matrix
        # Nodes are 1-indexed internally to avoid gcd(0, x) edge cases
        self.adjacency_matrix: NDArray[np.floating] = _build_coprime_adjacency(self.N)
        self.coupling_matrix: NDArray[np.floating] = (
            self.K / self.N
        ) * self.adjacency_matrix

    def phase_evolution_derivatives(
        self,
        time: float,
        phases: NDArray[np.floating],
        led_frequency: float = 40.0,
        led_amplitude: float = 1.0,
    ) -> NDArray[np.floating]:
        """
        Calculate phase derivatives d(theta_i)/dt across the ensemble.

        Combines intrinsic clocks, mesoscopic bivector coupling, and the
        external LED vector torque operator.

        Parameters
        ----------
        time : float
            Current simulation time.
        phases : NDArray[np.floating]
            Array of current phases, shape ``(N,)``.
        led_frequency : float
            Frequency of the external LED driving field (Hz).
        led_amplitude : float
            Amplitude of the external LED driving field.

        Returns
        -------
        NDArray[np.floating]
            Phase derivatives ``dtheta_dt``, shape ``(N,)``.
        """
        # Broadcast phase differences: phase_diff[i, j] = theta_j - theta_i
        phase_diff: NDArray[np.floating] = phases[None, :] - phases[:, None]

        # Coupled interior interaction field
        coupling_interaction: NDArray[np.floating] = np.sum(
            self.coupling_matrix * np.sin(phase_diff), axis=1
        )

        # 3. External LED Macroscopic Vector Torque Operator
        # Models projection of external field driving toward Critical Flicker Fusion
        led_torque: NDArray[np.floating] = (
            led_amplitude * np.sin(led_frequency * time) * np.cos(phases)
        )

        # Full evolution: intrinsic + coupling + external torque
        dtheta_dt: NDArray[np.floating] = (
            self.intrinsic_frequencies + coupling_interaction + led_torque
        )
        return dtheta_dt

    def compute_order_parameter(self, phases: NDArray[np.floating]) -> complex:
        """
        Compute the mesoscopic Kuramoto order parameter.

        Returns the complex order parameter ``r(t) * exp(I * Psi(t))``,
        where ``r`` is the synchronization magnitude and ``Psi`` is the
        mean phase.

        Parameters
        ----------
        phases : NDArray[np.floating]
            Current phase array, shape ``(N,)``.

        Returns
        -------
        complex
            Complex order parameter value.
        """
        return np.sum(np.exp(1j * phases)) / self.N


# 2️⃣ Internal Logic & Helpers


def _build_coprime_adjacency(n: int) -> NDArray[np.floating]:
    """
    Build an adjacency matrix where node i couples to node j iff gcd(i+1, j+1) == 1.

    Nodes are 1-indexed internally to avoid gcd(0, x) edge cases.

    Parameters
    ----------
    n : int
        Number of nodes.

    Returns
    -------
    NDArray[np.floating]
        Binary adjacency matrix of shape ``(n, n)``.
    """
    adj = np.zeros((n, n), dtype=float)
    for i in range(n):
        for j in range(n):
            if i != j and math.gcd(i + 1, j + 1) == 1:
                adj[i, j] = 1.0
    return adj


# 💨 Smoke Tests


def _run_smoke_test() -> None:
    """Quick sanity check: small ensemble initializes and evolves without error."""
    gen = ZBWKuramotoDataGenerator(num_oscillators=10, omega_0=1.0, coupling_K=0.5)

    # Check shapes
    assert gen.intrinsic_frequencies.shape == (10,)
    assert gen.adjacency_matrix.shape == (10, 10)
    assert gen.coupling_matrix.shape == (10, 10)

    # Check phi-shield frequencies are strictly increasing
    freqs = gen.intrinsic_frequencies
    assert np.all(
        np.diff(freqs) > 0
    ), "Phi-shield frequencies should be strictly increasing"

    # Check adjacency is symmetric and zero-diagonal
    assert np.allclose(
        gen.adjacency_matrix, gen.adjacency_matrix.T
    ), "Adjacency should be symmetric"
    assert np.all(np.diag(gen.adjacency_matrix) == 0.0), "Diagonal should be zero"

    # Check derivatives shape
    phases = np.random.uniform(0, 2 * np.pi, 10)
    dtheta = gen.phase_evolution_derivatives(time=0.0, phases=phases)
    assert dtheta.shape == (10,), f"Expected shape (10,), got {dtheta.shape}"

    # Check order parameter magnitude is in [0, 1]
    z = gen.compute_order_parameter(phases)
    r = abs(z)
    assert 0.0 <= r <= 1.0 + 1e-6, f"Order parameter magnitude {r} out of bounds"

    print("✅ ZBW smoke test passed.")


# 🔥 Entry Point


def main() -> None:
    """Entry point for module-level smoke testing."""
    _run_smoke_test()


if __name__ == "__main__":
    main()
