# src/kuramoto/solvers/quantum_rotor.py
"""
Quantum Rotor Solver for Kuramoto synchronization systems.

Implements hybrid quantum-classical Self-Consistent Field (SCF) time integration
using parallel single-qubit R_Z(phi) rotations with O(1) circuit depth.

Supported numerical schemes:
1. "statevector": Exact analytic unitary evolution of equatorial qubit states |+> under R_Z(phi).
2. "expectation": Exact Pauli expectation values <X> = cos(theta), <Y> = sin(theta).
3. "shot_sampling": Finite-shot projective measurement tomography with statistical sampling noise.

Author: Eigenscribe & Junie
Date: 10-2026
"""

from __future__ import annotations

import warnings
from typing import Final, Literal

import numpy as np
from numpy.typing import NDArray

from kuramoto.quantum.circuit_gen import export_to_qasm, generate_scf_angles
from kuramoto.utils import resolve_rng
from kuramoto.validation import (
    validate_intrinsic_frequency_array,
    validate_non_negative_scalar,
    validate_positive_scalar,
    validate_time_axis,
)

__all__: list[str] = [
    "QuantumRotorSolver",
    "step_quantum_scf",
]

# ---------------------------------------------------------------------------- #
# 0️⃣ / 🎭 Definitions, Constants & Types
# ---------------------------------------------------------------------------- #

PhaseArray = NDArray[np.floating]
TimeArray = NDArray[np.floating]
AdjacencyMatrix = NDArray[np.floating]

QuantumScheme = Literal["statevector", "expectation", "shot_sampling"]
VALID_SCHEMES: Final[tuple[str, ...]] = ("statevector", "expectation", "shot_sampling")


# ---------------------------------------------------------------------------- #
# 1️⃣ Public API
# ---------------------------------------------------------------------------- #


def step_quantum_scf(
    phases: PhaseArray,
    omegas: NDArray[np.floating],
    K: float,
    dt: float,
    scheme: QuantumScheme = "statevector",
    shots: int = 1024,
    rng: np.random.Generator | None = None,
) -> PhaseArray:
    """
    Perform a single forward time step using the Quantum SCF R_Z scheme.

    Parameters
    ----------
    phases : PhaseArray
        Current oscillator phases (theta_i) of shape (N,).
    omegas : NDArray[np.floating]
        Natural frequencies (omega_i) of shape (N,).
    K : float
        Coupling strength.
    dt : float
        Integration time step.
    scheme : {"statevector", "expectation", "shot_sampling"}, optional
        Numerical quantum scheme to apply (default: "statevector").
    shots : int, optional
        Number of measurement shots if using "shot_sampling" (default: 1024).
    rng : np.random.Generator, optional
        Random number generator for stochastic sampling.

    Returns
    -------
    PhaseArray
        Updated phase array of shape (N,) wrapped to [-pi, pi].
    """
    if scheme not in VALID_SCHEMES:
        raise ValueError(
            f"Invalid scheme '{scheme}'. Expected one of {VALID_SCHEMES}."
        )

    # 1. Compute parallel rotation angles via the Self-Consistent Field (SCF) torque
    # phi_j = (omega_j + K * R * sin(psi - theta_j)) * dt
    dtheta = generate_scf_angles(phases, omegas, K=K, dt=dt)
    target_phases = phases + dtheta

    if scheme == "statevector":
        # Scheme 1: Ideal unitary single-qubit rotation on |+> state
        # |psi> = R_Z(theta) |+> = ( |0> + e^{i theta} |1> ) / sqrt(2)
        # Exact phase update with zero sampling error:
        return np.arctan2(np.sin(target_phases), np.cos(target_phases))

    elif scheme == "expectation":
        # Scheme 2: Exact Pauli expectation values <X> = cos(theta), <Y> = sin(theta)
        exp_x = np.cos(target_phases)
        exp_y = np.sin(target_phases)
        return np.arctan2(exp_y, exp_x)

    else:  # "shot_sampling"
        # Scheme 3: Projective measurement tomography on Pauli X and Y bases with finite shots
        gen = resolve_rng(rng)
        p_x_plus = (1.0 + np.cos(target_phases)) / 2.0
        p_y_plus = (1.0 + np.sin(target_phases)) / 2.0

        p_x_plus = np.clip(p_x_plus, 0.0, 1.0)
        p_y_plus = np.clip(p_y_plus, 0.0, 1.0)

        # Draw counts for X basis and Y basis
        shots_per_basis = max(1, shots // 2)
        counts_x = gen.binomial(shots_per_basis, p_x_plus)
        counts_y = gen.binomial(shots_per_basis, p_y_plus)

        meas_x = 2.0 * (counts_x / shots_per_basis) - 1.0
        meas_y = 2.0 * (counts_y / shots_per_basis) - 1.0

        return np.arctan2(meas_y, meas_x)


class QuantumRotorSolver:
    """
    Hybrid Quantum-Classical Kuramoto solver using parallel R_Z gates.

    Simulates N oscillators mapped to N quantum qubits with constant circuit depth O(1)
    per step using the Self-Consistent Field (SCF) geometric torque mapping.

    Attributes
    ----------
    N : int
        Number of oscillators / qubits.
    omegas : NDArray[np.floating]
        Natural frequencies array of shape (N,).
    phases : PhaseArray
        Current phase state array of shape (N,).
    rng : np.random.Generator
        Internal pseudorandom generator.
    """

    def __init__(
        self,
        n_oscillators: int,
        seed: int | None = None,
        natural_frequencies: NDArray[np.floating] | None = None,
        initial_phases: PhaseArray | None = None,
        rng: np.random.Generator | None = None,
    ) -> None:
        """
        Initialize the Quantum Rotor Kuramoto solver.

        Parameters
        ----------
        n_oscillators : int
            Number of coupled oscillators (qubits).
        seed : int, optional
            Seed for random number generator.
        natural_frequencies : NDArray[np.floating], optional
            Array of intrinsic frequencies omega_i. Defaults to standard normal.
        initial_phases : PhaseArray, optional
            Initial phases theta_0. Defaults to uniform [-pi, pi).
        rng : np.random.Generator, optional
            Pre-configured NumPy generator.
        """
        validate_positive_scalar(n_oscillators, "n_oscillators")
        self.N: int = int(n_oscillators)
        self.rng: np.random.Generator = resolve_rng(rng or seed)

        if natural_frequencies is not None:
            self.omegas: NDArray[np.floating] = np.asarray(
                validate_intrinsic_frequency_array(natural_frequencies, self.N),
                dtype=float,
            )
        else:
            self.omegas = self.rng.normal(0.0, 1.0, size=self.N)

        if initial_phases is not None:
            if len(initial_phases) != self.N:
                raise ValueError(
                    f"initial_phases length {len(initial_phases)} must match n_oscillators {self.N}."
                )
            self.phases: PhaseArray = np.asarray(initial_phases, dtype=float)
        else:
            self.phases = self.rng.uniform(-np.pi, np.pi, size=self.N)

    def step(
        self,
        K: float,
        dt: float,
        scheme: QuantumScheme = "statevector",
        shots: int = 1024,
    ) -> PhaseArray:
        """
        Advance oscillator phases by time increment dt.

        Parameters
        ----------
        K : float
            Coupling strength.
        dt : float
            Time step size.
        scheme : {"statevector", "expectation", "shot_sampling"}, optional
            Quantum execution scheme (default: "statevector").
        shots : int, optional
            Shot count for "shot_sampling" (default: 1024).

        Returns
        -------
        PhaseArray
            Updated phase state.
        """
        validate_non_negative_scalar(K, "K")
        validate_positive_scalar(dt, "dt")

        self.phases = step_quantum_scf(
            self.phases,
            self.omegas,
            K=K,
            dt=dt,
            scheme=scheme,
            shots=shots,
            rng=self.rng,
        )
        return self.phases

    def simulate(
        self,
        K: float,
        t_eval: TimeArray,
        dt_internal: float | None = None,
        scheme: QuantumScheme = "statevector",
        shots: int = 1024,
    ) -> tuple[TimeArray, NDArray[np.floating]]:
        """
        Simulate Kuramoto dynamics over evaluation time grid t_eval.

        Parameters
        ----------
        K : float
            Coupling constant.
        t_eval : TimeArray
            Array of output timestamps.
        dt_internal : float, optional
            Internal integration sub-step. If None, uses min(diff(t_eval)).
        scheme : {"statevector", "expectation", "shot_sampling"}, optional
            Quantum scheme used for time stepping.
        shots : int, optional
            Measurement shots for "shot_sampling".

        Returns
        -------
        t_eval : TimeArray
            Time points.
        history : NDArray[np.floating]
            Trajectory array of shape (len(t_eval), N).
        """
        validate_non_negative_scalar(K, "K")
        validate_time_axis(t_eval)

        n_times = len(t_eval)
        history = np.zeros((n_times, self.N), dtype=float)
        history[0] = self.phases.copy()

        diffs = np.diff(t_eval)
        if dt_internal is None:
            dt_internal = float(np.min(diffs))
        validate_positive_scalar(dt_internal, "dt_internal")

        # Check Nyquist condition
        omega_max = float(np.max(np.abs(self.omegas)))
        if omega_max > 0 and dt_internal > np.pi / omega_max:
            warnings.warn(
                f"dt_internal ({dt_internal:.4f}) exceeds the Nyquist resolution limit "
                f"(pi / omega_max = {np.pi / omega_max:.4f}). High-frequency dynamics may alias.",
                UserWarning,
                stacklevel=2,
            )

        for i in range(1, n_times):
            t_prev = t_eval[i - 1]
            t_target = t_eval[i]
            t_curr = t_prev

            while t_curr < t_target - 1e-14:
                step_dt = min(dt_internal, t_target - t_curr)
                self.step(K=K, dt=step_dt, scheme=scheme, shots=shots)
                t_curr += step_dt

            history[i] = self.phases.copy()

        return t_eval, history

    def to_qasm(self, K: float, dt: float) -> str:
        """
        Generate OpenQASM 2.0 source for the current step's parallel R_Z layer.

        Parameters
        ----------
        K : float
            Coupling strength.
        dt : float
            Time step size.

        Returns
        -------
        str
            OpenQASM 2.0 code representation.
        """
        angles = generate_scf_angles(self.phases, self.omegas, K=K, dt=dt)
        return export_to_qasm(angles)


# ---------------------------------------------------------------------------- #
# 💨 Smoke Test
# ---------------------------------------------------------------------------- #


def _run_smoke_test() -> None:
    """Quick sanity check for QuantumRotorSolver."""
    solver = QuantumRotorSolver(n_oscillators=5, seed=42)
    t_eval = np.linspace(0.0, 1.0, 10)
    t_out, traj_sv = solver.simulate(K=1.5, t_eval=t_eval, scheme="statevector")
    assert traj_sv.shape == (10, 5)

    solver_exp = QuantumRotorSolver(n_oscillators=5, seed=42)
    _, traj_exp = solver_exp.simulate(K=1.5, t_eval=t_eval, scheme="expectation")
    assert np.allclose(traj_sv, traj_exp, atol=1e-5)

    qasm = solver.to_qasm(K=1.5, dt=0.05)
    assert "rz(" in qasm
    print("✅ QuantumRotorSolver smoke test passed successfully!")


# ---------------------------------------------------------------------------- #
# 🔥 Entry Point
# ---------------------------------------------------------------------------- #


def main() -> None:
    """Module entry point."""
    _run_smoke_test()


if __name__ == "__main__":
    main()
