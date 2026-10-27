# src/kuramoto/solvers/rotor.py
"""
Geometric GA-based Kuramoto solver using rotors in Cl(dim).

⚠️ Experimental / Research Mode

Unlike the standard solve_kuramoto() rapper (which uses adaptive RK45 with built-in error control), RotorSolver uses
fixed-step Euler integration.

The solver uses a Nyquist-inspired temporal resolution criterion to help ensure that high-frequency oscillator dynamics
are adequately resolved. This criterion is supplemented by an explicit maximum phase-increment constraint to prevent
numerical instabilities.

The Nyquist-inspired criterion is a resolution heuristic, not a claim that the Nyquist sampling theorem provides an
Euler stability condition. Explicit Euler accuracy and stability reamin separate numerical concerns.

Users should:
    - Choose a sufficiently small ``dt_internal``;
    - Use ``enforce_nyquist=True`` when high-frequency dynamics should be automatically checked;
    - Interpret warnings as indications of possible temporal under-resolution, not as formal stability proofs;
    - Verify results against the classic RK65 solver.

Future work:
    Implement an adaptive RK45/Dormand-Prince-style stepper for the rotor representation while retaining the geometric
    state representation.

Each oscillator is represented as a rotor

    R = exp(-B * theta / 2),

where B is the rotation plane bivector. Coupling is applied using the extracted physical phases, while the state itself
is stored as geometric-algebra rotors.

Author: Eigenscribe
Review status: Reviewed and maintained by Eigenscribe.
Date created: 05-2026
Last updated: 10-2026
"""

from __future__ import annotations

import warnings

import numpy as np
from numpy.typing import NDArray
from enum import IntEnum
from typing import Final, NamedTuple

# Import RNG utilities from the central utils module
from kuramoto.utils import resolve_rng

# Validation imports support both package execution and direct script execution.
from kuramoto.validation import (
    validate_adjacency,
    validate_intrinsic_frequency_array,
    validate_non_negative_scalar,
    validate_positive_scalar,
    validate_time_axis,
)

__all__: list[str] = ["RotorSolver", "AdaptiveStatus", "AdaptiveStepResult", "step_rkmk4"]

# ---------------------------------------------------------------------------- #
# 🎭 Type Aliases
# ---------------------------------------------------------------------------- #

PhaseArray = NDArray[np.floating]
TimeArray = NDArray[np.floating]
AdjacencyMatrix = NDArray[np.floating]


class RotorSolver:
    """
    Geometric Algebra-based Kuramoto solver using rotors in Cl(dim).

    Attributes
    ----------
    N : int
        Number of oscillators.
    dim : int
        Dimensionality of GA space (typically 2 for planar rotations).
    layout : clifford.Layout
        GA layout object defining basis vectors and multiplication rules.
    blades : dict
        Precomputed blade references (e.g., blades['e12'] for 2D rotation plane).
    rotors : list
        Current rotor state for each oscillator.
    omegas : NDArray[np.floating]
        Natural frequencies (shape (N,)).
    """

    def __init__(
        self,
        n_oscillators: int,
        dim: int = 2,
        seed: int | None = None,
        adjacency_matrix: AdjacencyMatrix | None = None,
        natural_frequencies: NDArray[np.floating] | None = None,
        initial_phases: PhaseArray | None = None,
        initial_rotors: list | None = None,
        rng: np.random.Generator | None = None,
    ) -> None:
        """
        Initialize rotor-based Kuramoto solver.

        Parameters
        ----------
        n_oscillators : int
            Number of coupled oscillators.
        dim : int, optional
            GA dimensionality (default: 2 for SO(2) plane rotations).
        seed : int, optional
            Random seed for reproducibility.
        rng : numpy.random.Generator, optional
            Explicit generator to inject. Takes precedence over ``seed`` when
            provided (dependency-injection for reproducible pipelines).
        adjacency_matrix : AdjacencyMatrix, optional
            Network topology matrix of shape (N, N). If None, all-to-all complete graph
            without self-loops is assumed.
        natural_frequencies : NDArray[np.floating], optional
            Intrinsic natural frequencies of shape (N,). If None, drawn uniformly from [-1.0, 1.0].
        initial_phases : PhaseArray, optional
            Explicit initial phases in radians of shape (N,).
        initial_rotors : list, optional
            Explicit initial Clifford multivector rotors of length N.

        Raises
        ------
        ImportError
            If the ``clifford`` package is not installed.
        ValueError
            If ``dim < 2`` or if the oscillator count or input dimensions are invalid.
        """
        validate_positive_scalar(n_oscillators, "n_oscillators")
        validate_positive_scalar(dim, "dim")

        if dim < 2:
            raise ValueError("❌ dim must be >=2 from non-trivial rotation plane")

        # Lazy import to avoid hard dependency
        try:
            from clifford import Cl
        except ImportError as exc:
            raise ImportError(
                "❌ clifford package is required for Rotor Solver. "
                "⬆️ Install with: pip install clifford"
            ) from exc

        self.rng = resolve_rng(rng, seed)

        self.N = n_oscillators
        self.dim = dim
        self.layout, self.blades = Cl(dim)

        if adjacency_matrix is None:
            A = np.ones((self.N, self.N), dtype=np.float64)
            np.fill_diagonal(A, 0.0)
            self._is_complete = True
        else:
            validate_adjacency(adjacency_matrix, self.N)
            A = np.asarray(adjacency_matrix, dtype=np.float64)
            # Pre-calculate if complete graph to allow O(N) Mean-Field optimizations
            self._is_complete = bool(
                np.allclose(A, np.ones((self.N, self.N)) - np.eye(self.N))
            )
        self.A: AdjacencyMatrix = A

        # Rotation plane: for 2D this is e12, for 3D typically xy-plane
        plane_key = f"e{dim-1}{dim}" if dim <= 3 else "e12"
        self.B_plane = self.blades[plane_key]

        # Precompute indices for rotor components in the multivector value array
        # For any dim, we always want the scalar (index 0)
        # For dim=2, we want e12
        # For dim=3, we want e12, e23, e31
        if dim == 2:
            self._blade_indices = [
                0,
                int(np.nonzero(np.asarray(self.B_plane.value))[0][0]),
            ]
        elif dim == 3:
            # Cl(3) bivector indices for e12, e13, e23
            # We identify them by name length (e.g., 'e12') or bit count
            self._blade_indices = [0] + [
                i
                for i, name in enumerate(self.layout.names)
                if len(name.replace("e", "")) == 2
            ]
        else:
            # Fallback for higher dim
            self._blade_indices = [
                0,
                int(np.nonzero(np.asarray(self.B_plane.value))[0][0]),
            ]

        # Initial condition
        if initial_rotors is not None:
            if len(initial_rotors) != self.N:
                raise ValueError(
                    f"❌ initial_rotors length ({len(initial_rotors)}) must match n_oscillators ({self.N})"
                )
            self.rotors = list(initial_rotors)
        elif initial_phases is not None:
            init_p = np.asarray(initial_phases, dtype=np.float64)
            if init_p.shape != (self.N,):
                raise ValueError(
                    f"❌ initial_phases shape {init_p.shape} must match ({self.N},)"
                )
            self.rotors = [np.exp(-self.B_plane * p / 2.0) for p in init_p]
        else:
            self.rotors = self._random_rotors()

        # Optimized array representation
        self._rotor_array = np.array(
            [r.value[self._blade_indices] for r in self.rotors]
        )

        # Adaptive-stepper diagnostics (read-only telemetry for the benchmark suite)
        self._consecutive_rejections: int = 0

        # Natural frequencies
        if natural_frequencies is not None:
            validate_intrinsic_frequency_array(natural_frequencies, self.N)
            self.omegas = np.asarray(natural_frequencies, dtype=np.float64).copy()
        elif dim == 2:
            self.omegas = self.rng.uniform(-1.0, 1.0, n_oscillators)
        else:
            # For dim=3, we can have 3D natural frequency bivectors
            # We'll store them as an (N, 3) array of bivector coefficients
            # But to keep compatibility with existing code that expects scalar self.omegas,
            # we'll store the 'primary' frequency as a scalar and have an optional
            # self.omega_bivectors for the full 3D case.
            self.omegas = self.rng.uniform(-1.0, 1.0, n_oscillators)
            # Initialize 3D bivector frequencies (random axes)
            num_bivectors = len(self._blade_indices) - 1
            self.omega_bivectors = self.rng.uniform(
                -0.5, 0.5, (n_oscillators, num_bivectors)
            )

    def _random_rotors(self) -> list:
        """Generate random initial rotors."""
        if self.dim == 2:
            phases = self.rng.uniform(0, 2 * np.pi, self.N)
            return [np.exp(-self.B_plane * p / 2.0) for p in phases]

        # For dim=3 (S^2), generate random unit vectors and find rotors
        e1 = self.layout.basis_vectors["e1"]
        rotors = []
        for _ in range(self.N):
            # Sample from isotropic distribution on sphere
            v_raw = self.rng.standard_normal(self.dim)
            v = v_raw / np.linalg.norm(v_raw)
            v_ga = sum(
                c * self.layout.basis_vectors[f"e{i+1}"] for i, c in enumerate(v)
            )

            # Rotor that takes e1 to v_ga
            # R = (1 + v*e1) / sqrt(2*(1 + v.e1))
            dot = float((v_ga | e1).value[0])
            if dot < -0.9999:  # Handle south pole singularity
                # Rotate by pi around e2
                r = self.layout.basis_vectors["e1"] * self.layout.basis_vectors["e2"]
                rotors.append(r)
            else:
                r_unnorm = 1 + v_ga * e1
                r = r_unnorm / np.sqrt(2 * (1 + dot))
                rotors.append(r)
        return rotors

    def extract_phases(self) -> PhaseArray:
        """ "
        Extract physical phase angles from current rotor states.

        Returns
        -------
        PhaseArray
            Phases of shape ``(N,)``, wrapped to ``[0, 2*pi)``.
            For dim > 2, this projects the rotor onto the primary B_plane.
        """
        if (
            self.dim == 2
            and hasattr(self, "_rotor_array")
            and self._rotor_array.shape[1] == 2
        ):
            # Use optimized array if available
            a = self._rotor_array[:, 0]
            b = self._rotor_array[:, 1]
            return (2.0 * np.arctan2(-b, a)) % (2.0 * np.pi)

        phases = []
        # Find the index of the B_plane blade again to be sure
        b_idx = int(np.nonzero(np.asarray(self.B_plane.value))[0][0])

        for r in self.rotors:
            scalar = float(r.value[0])
            bivector = float(r.value[b_idx])
            phases.append((2.0 * np.arctan2(-bivector, scalar)) % (2.0 * np.pi))
        return np.array(phases)

    def step_euler(
        self,
        K: float,
        dt: float,
    ) -> None:
        """
        Advance the Kuramoto system by one explicit Euler step.

        The standard attractive Kuramoto interaction on graph A is

            dtheta_i/dt = omega_i + (K/N) * sum_j A_ij * sin(theta_j - theta_i).

        Parameters
        ----------
        K : float
            Coupling strength (non-negative for standard attraction).
        dt : float
            Timestep size.
        """
        validate_non_negative_scalar(K, "K")
        validate_positive_scalar(dt, "dt")

        phases = self.extract_phases()

        # Standard attractive Kuramoto coupling with adjacency topology
        diff_matrix = phases[np.newaxis, :] - phases[:, np.newaxis]
        coupling = (K / self.N) * np.sum(self.A * np.sin(diff_matrix), axis=1)

        # Update phases
        new_phases = phases + dt * (self.omegas + coupling)

        # Reconstruct rotors from updated phases
        self.rotors = [np.exp(-self.B_plane * p / 2.0) for p in new_phases]
        self._sync_array_from_rotors()

    def step_euler_geometric(
        self,
        K: float,
        dt: float,
    ) -> None:
        """
        Advance the rotor solver one step using pure geometric algebra bivector torque.

        This method leverages the bivector torque formulation,
        computing network-weighted mean-field polarization and wedge-product torques
        without extracting phase angles at every step. Works for any dim >= 2.

        Parameters
        ----------
        K : float
            Coupling strength (non-negative for standard attraction).
        dt : float
            Timestep size.
        """
        validate_non_negative_scalar(K, "K")
        validate_positive_scalar(dt, "dt")

        e1 = self.layout.basis_vectors["e1"]

        # 1. Transform reference vector e1 under each rotor to get orientation vectors O(N)
        v_i = [r_i * e1 * r_i.conjugate() for r_i in self.rotors]

        new_rotors = []
        for i, (r_i, vi) in enumerate(zip(self.rotors, v_i, strict=True)):
            # 2. Compute local network-weighted polarization vector
            v_mean_i = sum(self.A[i, j] * v_i[j] for j in range(self.N)) / self.N

            # 3. Compute interaction bivector torque: (v_mean_i ^ v_i)
            torque_bivector = K * (v_mean_i ^ vi)

            # 4. Synthesize total bivector velocity generator
            # We subtract torque_bivector to achieve attraction (theta_i toward theta_mean)
            omega_nat = self.omegas[i] * self.B_plane

            # If 3D natural bivectors are defined, add them
            if self.dim == 3 and hasattr(self, "omega_bivectors"):
                # bivector indices are at indices 1, 2, 3 of our _blade_indices [scalar, e12, e13, e23]
                for j, b_idx in enumerate(self._blade_indices[1:]):
                    b_val = np.zeros(self.layout.ga_dims)
                    b_val[b_idx] = self.omega_bivectors[i, j]
                    omega_nat += self.layout.MultiVector(b_val)

            omega_total = omega_nat - torque_bivector

            # 5. Advance the rotor state explicitly using rotor exponential update
            d_rotor = np.exp(-omega_total * dt / 2.0)
            new_rotors.append(d_rotor * r_i)

        self.rotors = new_rotors
        self._sync_array_from_rotors()

    def _compute_bivector_omega_2d(
        self,
        rotor_array: NDArray[np.floating],
        K: float,
    ) -> NDArray[np.floating]:
        """Compute scalar angular velocity generator omega_total for 2D rotors."""
        a = rotor_array[:, 0]
        b = rotor_array[:, 1]
        x = a**2 - b**2
        y = -2.0 * a * b
        V = np.column_stack((x, y))

        if self._is_complete:
            # O(N) Self-Consistent Field (SCF) optimization
            v_sum = np.sum(V, axis=0)
            v_mean = (v_sum - V) / self.N
        else:
            # O(N^2) or O(E) general graph coupling
            v_mean = (self.A @ V) / self.N

        torque = v_mean[:, 0] * y - v_mean[:, 1] * x
        return self.omegas - K * torque

    def _estimate_lte(
        self,
        w1: NDArray[np.float64],
        w2: NDArray[np.float64],
        dt: float,
    ) -> float:
        """Return the bivector-space embedded local-truncation error estimate.

        Parameters
        ----------
        w1 : NDArray[np.float64]
            Bivector velocity at the base state, shape ``(N,)`` for dim=2 or ``(N,3)`` for dim=3.
        w2 : NDArray[np.float64]
            Bivector velocity at the predicted state, same shape as ``w1``.
        dt : float
            Trial step size.

        Returns
        -------
        float
            ``0.25 * dt * max_i |w2,i - w1,i|``, in radians.

        Notes
        -----
        MAX-NORM, not RMS. Rational: the max-norm resolves the worst-behaved oscillator, which is the correct behavior
        for partially synchronized and chimera-like states where a single outlier can carry the fastest local dynamics.
        An RMS norm would let that oscillator be under-resolved in exchange for a larger dt. This chois is isolated here
        so it lives in exactly one place.
        """
        assert w1.shape == w2.shape, "Bivector velocity shapes must match."
        return float(0.25 * dt * np.max(np.abs(w1 - w2)))

    def _effective_tolerance(
        self,
        rtol: float,
        atol: float,
    ) -> float:
        """Return the scalar tolerance compared against the bivector-space LTE estimate.

        Parameters
        ----------
        rtol : float
            Relative tolerance contribution.
        atol : float
            Absolute tolerance floor, in radians.

        Returns
        -------
        float
            Effective tolerance in radians.

        Notes
        -----
        The textbook criterion ``atol + rtol * |R|`` degenerates for unit rotors: ``|R| = 1`` for every state on
        Spin(n), so ``rtol`` would carry no dimensional information at all. The LTE returned by
        ``step_predictor_corrector`` is an angle in radians, so the tolerance is expressed in radians and ``rtol`` is
        interpreted relative to a unit-radian angle scale.

        DELIBERATELY dt-INDEPENDENT. Making the tolerance depend on ``dt`` (for example scaling by ``|Omega| * dt``)
        contaminates the controller asymptotics: with ``lte ~ dt^2`` and ``tol ~ dt``, the scaling factor becomes
        ``s ~ dt^(-1/2)`` and the clean ``dt ~ tol^(1/2)`` law is destroyed. If later you want a state-magnitude-aware
        tolerance, scale by a quantity that is fixed for the duration of a run.
        """
        return atol + rtol * _ROTOR_ANGLE_SCALE

    def _apply_bivector_step_2d(
        self,
        rotor_array: NDArray[np.floating],
        omega_total: NDArray[np.floating],
        dt: float,
    ) -> NDArray[np.floating]:
        """Apply exponential rotation map exp(-omega_total * dt * B / 2) * R."""
        phi = -omega_total * dt / 2.0
        c = np.cos(phi)
        s = np.sin(phi)
        a = rotor_array[:, 0]
        b = rotor_array[:, 1]
        return np.column_stack((a * c - b * s, a * s + b * c))

    def _compute_bivector_omega_3d(
        self,
        rotor_array: NDArray[np.floating],
        K: float,
    ) -> tuple[NDArray[np.floating], NDArray[np.floating], NDArray[np.floating]]:
        """Compute 3D bivector velocity components (v12, v13, v23)."""
        a = rotor_array[:, 0]
        b12 = rotor_array[:, 1]
        b13 = rotor_array[:, 2]
        b23 = rotor_array[:, 3]

        x = a**2 + b12**2 + b13**2 - b23**2
        y = -2.0 * a * b12 + 2.0 * b13 * b23
        z = -2.0 * a * b13 - 2.0 * b12 * b23

        V = np.column_stack((x, y, z))

        if self._is_complete:
            # O(N) Self-Consistent Field (SCF) optimization
            v_sum = np.sum(V, axis=0)
            v_mean = (v_sum - V) / self.N
        else:
            v_mean = (self.A @ V) / self.N

        x_m = v_mean[:, 0]
        y_m = v_mean[:, 1]
        z_m = v_mean[:, 2]

        t12 = K * (x_m * y - y_m * x)
        t13 = K * (x_m * z - z_m * x)
        t23 = K * (y_m * z - z_m * y)

        v12 = self.omegas - t12
        v13 = -t13
        v23 = -t23
        if hasattr(self, "omega_bivectors"):
            v12 = v12 + self.omega_bivectors[:, 0]
            v13 = v13 + self.omega_bivectors[:, 1]
            v23 = v23 + self.omega_bivectors[:, 2]
        return v12, v13, v23

    def _apply_bivector_step_3d(
        self,
        rotor_array: NDArray[np.floating],
        v12: NDArray[np.floating],
        v13: NDArray[np.floating],
        v23: NDArray[np.floating],
        dt: float,
    ) -> NDArray[np.floating]:
        """Apply 3D exponential quaternion/rotor multiplication."""
        phi12 = -v12 * dt / 2.0
        phi13 = -v13 * dt / 2.0
        phi23 = -v23 * dt / 2.0

        phi_mag = np.sqrt(phi12**2 + phi13**2 + phi23**2)
        c = np.cos(phi_mag)
        s = np.zeros_like(phi_mag)
        mask = phi_mag > 1e-12
        s[mask] = np.sin(phi_mag[mask]) / phi_mag[mask]
        s[~mask] = 1.0

        ma, mb12, mb13, mb23 = c, s * phi12, s * phi13, s * phi23
        a = rotor_array[:, 0]
        b12 = rotor_array[:, 1]
        b13 = rotor_array[:, 2]
        b23 = rotor_array[:, 3]

        return np.column_stack(
            (
                ma * a - mb12 * b12 - mb13 * b13 - mb23 * b23,
                ma * b12 + a * mb12 - mb13 * b23 + mb23 * b13,
                ma * b13 + a * mb13 + mb12 * b23 - mb23 * b12,
                ma * b23 + a * mb23 - mb12 * b13 + mb13 * b12,
            )
        )

    def step_euler_vectorized_geometric(
        self,
        K: float,
        dt: float,
    ) -> None:
        """
        Fast vectorized Euler step using pure GA bivector torque logic.

        This method avoids Python loops and object overhead by using NumPy
        broadcasting and graph adjacency matrix operations. Supports dim=2 and dim=3.

        Parameters
        ----------
        K : float
            Coupling strength (non-negative for standard attraction).
        dt : float
            Timestep.
        """
        validate_non_negative_scalar(K, "K")
        validate_positive_scalar(dt, "dt")

        if self.dim == 2:
            omega_total = self._compute_bivector_omega_2d(self._rotor_array, K)
            self._rotor_array = self._apply_bivector_step_2d(
                self._rotor_array, omega_total, dt
            )
        elif self.dim == 3:
            v12, v13, v23 = self._compute_bivector_omega_3d(self._rotor_array, K)
            self._rotor_array = self._apply_bivector_step_3d(
                self._rotor_array, v12, v13, v23, dt
            )

    def step_midpoint_geometric(
        self,
        K: float,
        dt: float,
    ) -> None:
        """
        2nd-order geometric midpoint step on Spin(n) manifold.

        Parameters
        ----------
        K : float
            Coupling strength (non-negative).
        dt : float
            Timestep.
        """
        validate_non_negative_scalar(K, "K")
        validate_positive_scalar(dt, "dt")

        if self.dim == 2:
            omega_0 = self._compute_bivector_omega_2d(self._rotor_array, K)
            r_mid = self._apply_bivector_step_2d(self._rotor_array, omega_0, dt * 0.5)
            omega_mid = self._compute_bivector_omega_2d(r_mid, K)
            self._rotor_array = self._apply_bivector_step_2d(
                self._rotor_array, omega_mid, dt
            )
        elif self.dim == 3:
            v12_0, v13_0, v23_0 = self._compute_bivector_omega_3d(self._rotor_array, K)
            r_mid = self._apply_bivector_step_3d(
                self._rotor_array, v12_0, v13_0, v23_0, dt * 0.5
            )
            v12_m, v13_m, v23_m = self._compute_bivector_omega_3d(r_mid, K)
            self._rotor_array = self._apply_bivector_step_3d(
                self._rotor_array, v12_m, v13_m, v23_m, dt
            )

    def step_rkmk4(
        self,
        K: float,
        dt: float,
    ) -> None:
        """
        4th-order Runge-Kutta-Munthe-Kaas (RKMK4) Lie-group geometric integrator.

        Advances the rotor state directly on the Spin(n) manifold with O(dt^4)
        accuracy while strictly preserving unit rotor norms and Lie invariants.

        Parameters
        ----------
        K : float
            Coupling strength (non-negative).
        dt : float
            Timestep.
        """
        validate_non_negative_scalar(K, "K")
        validate_positive_scalar(dt, "dt")

        if self.dim == 2:
            y0 = self._rotor_array
            w1 = self._compute_bivector_omega_2d(y0, K)
            y1 = self._apply_bivector_step_2d(y0, w1, dt * 0.5)

            w2 = self._compute_bivector_omega_2d(y1, K)
            y2 = self._apply_bivector_step_2d(y0, w2, dt * 0.5)

            w3 = self._compute_bivector_omega_2d(y2, K)
            y3 = self._apply_bivector_step_2d(y0, w3, dt)

            w4 = self._compute_bivector_omega_2d(y3, K)
            w_eff = (w1 + 2.0 * w2 + 2.0 * w3 + w4) / 6.0
            self._rotor_array = self._apply_bivector_step_2d(y0, w_eff, dt)

        elif self.dim == 3:
            y0 = self._rotor_array
            v12_1, v13_1, v23_1 = self._compute_bivector_omega_3d(y0, K)
            y1 = self._apply_bivector_step_3d(y0, v12_1, v13_1, v23_1, dt * 0.5)

            v12_2, v13_2, v23_2 = self._compute_bivector_omega_3d(y1, K)
            y2 = self._apply_bivector_step_3d(y0, v12_2, v13_2, v23_2, dt * 0.5)

            v12_3, v13_3, v23_3 = self._compute_bivector_omega_3d(y2, K)
            y3 = self._apply_bivector_step_3d(y0, v12_3, v13_3, v23_3, dt)

            v12_4, v13_4, v23_4 = self._compute_bivector_omega_3d(y3, K)
            v12_eff = (v12_1 + 2.0 * v12_2 + 2.0 * v12_3 + v12_4) / 6.0
            v13_eff = (v13_1 + 2.0 * v13_2 + 2.0 * v13_3 + v13_4) / 6.0
            v23_eff = (v23_1 + 2.0 * v23_2 + 2.0 * v23_3 + v23_4) / 6.0
            self._rotor_array = self._apply_bivector_step_3d(
                y0, v12_eff, v13_eff, v23_eff, dt
            )

    def _sync_rotors_from_array(self) -> None:
        """Synchronize clifford rotor objects from internal array."""
        for i, r in enumerate(self.rotors):
            r.value[self._blade_indices] = self._rotor_array[i, :]

    def _sync_array_from_rotors(self) -> None:
        """Synchronize internal array from clifford rotor objects."""
        self._rotor_array = np.array(
            [r.value[self._blade_indices] for r in self.rotors]
        )

    def step_euler_fast(
        self,
        K: float,
        dt: float,
    ) -> None:
        """
        Fast Euler step for the Kuramoto model.

        Parameters
        ----------
        K : float
            Coupling strength (non-negative for standard attraction).
        dt : float
            Time step size.
        """
        validate_non_negative_scalar(K, "K")
        validate_positive_scalar(dt, "dt")

        phases = self.extract_phases()

        # Check if complete all-to-all graph with standard mean-field order parameter
        complete_graph = np.allclose(self.A, np.ones((self.N, self.N)) - np.eye(self.N))
        if complete_graph:
            # 1. Compute global order parameter in O(N)
            order_param = np.mean(np.exp(1j * phases))
            R = np.abs(order_param)
            psi = np.angle(order_param)
            # 2. Compute coupling vector in O(N) without a distance matrix
            coupling = K * R * np.sin(psi - phases)
        else:
            # General graph coupling
            diff_matrix = phases[np.newaxis, :] - phases[:, np.newaxis]
            coupling = (K / self.N) * np.sum(self.A * np.sin(diff_matrix), axis=1)

        # 3. Update state
        new_phases = phases + dt * (self.omegas + coupling)
        half = new_phases * 0.5
        cos_half = np.cos(half)
        sin_half = -np.sin(half)
        blade_idx = self._blade_indices[1]
        for i, rot in enumerate(self.rotors):
            rot.value[0] = cos_half[i]
            rot.value[blade_idx] = sin_half[i]
        self._sync_array_from_rotors()

    def get_complex_order_parameter(self) -> complex:
        """
        Compute the standard complex Kuramoto order parameter.

        Returns
        -------
        complex
            ``mean(exp(1j * theta))``. Magnitude is synchronization strength.

        Notes
        -----
        The rotor contains half-angle information through
            R(theta) = exp(-B * theta / 2).
        Therefore, rotor coefficients must not be averaged directly.
        This method extracts physical phases first for canonical Kuramoto observvable.
        """
        phases = self.extract_phases()
        return complex(np.mean(np.exp(1j * phases)))

    def get_order_parameter_vector(self) -> NDArray[np.floating]:
        """
        Compute the mean orientation vector (Order Parameter) in dim-space.

        For dim=2, this is equivalent to the complex order parameter.
        For dim=3, this is the 3D synchronization vector on S^2.

        Returns
        -------
        NDArray
            Mean vector of shape ``(dim,)``.
        """
        e1 = self.layout.basis_vectors["e1"]
        # Transform e1 under each rotor
        v_i = np.array(
            [(r * e1 * r.conjugate()).value[1 : self.dim + 1] for r in self.rotors]
        )
        return np.mean(v_i, axis=0)

    def get_synchronization_strength(self) -> float:
        """Return the magnitude of the synchronization order parameter."""
        if self.dim == 2:
            return float(abs(self.get_complex_order_parameter()))
        return float(np.linalg.norm(self.get_order_parameter_vector()))

    def step_predictor_corrector(
        self,
        K: float,
        dt: float,
    ) -> tuple[NDArray[np.float64], float]:
        """
        Take one 2nd-order Lie-algebra Heun predictor-corrector step on Spin(n).

        Computes a 1st-order Lie-Euler predictor and a 2nd-order Lie-algebra-average corrector from the SAME base state,
        and returns the corrector together with an embedded local-truncation-error estimate. The solver state is NOT
        modified.

        Parameters
        ----------
        K : float
           Global coupling strength. Must be non-negative.
        dt : float
           Trial step size. Must be strictly positive.

        Returns
        -------
        tuple[NDArray[np.float64], float]
            ``(y_corr, let)`` -- candidate rotor array of shape ``(N, n_components)`` and a scalar
            local-truncation-error estimate in radians.

        Raises
        ------
        ValueError
            If ``K`` is negative, ``dt`` is non-positive, or ``dim`` is unsupported.

        Notes
        -----
        PURITY CONTRACT: this method does not assign to ``self._rotor_array``. Both ``_apply_bivector_step_2d`` and
        ``_apply_bivector_step_3d`` allocate frash arrays via ``np.column_stack``, so no defensive copy of ``y0`` is
        required. The accept/reject decision belongs to ``step_adaptive_embedded``.

        ANCHORING: the corrector re-exponentiates from the BASE state ``y0``, never from the predictor. Averaging
        bivectors is a 2nd-order construction only when both are anchored at the same point; anchoring the corrector at
        ``y_predict`` silently drops you to 1st order.

        ERROR SCALE: ``lte`` is measured in bivector space as ``(dt / 4) * max_i |w2, i - w1, i|``. This is teh error
        of the LOWER-order (predictor) member, hence O(dt^2). Tolerances passed to the adaptive driver are calibrated
        against THIS definition.
        """
        validate_non_negative_scalar(K, "K")
        validate_positive_scalar(dt, "dt")

        y0 = self._rotor_array
        if self.dim == 2:
            # 1. Predictor: 1st-order Lie-Euler, anchored at y0.
            w1 = self._compute_bivector_omega_2d(y0, K)
            y_pred = self._apply_bivector_step_2d(y0, w1, dt)

            #2. Corrector: 2nd-order Lie-algebra average, anchored at y0.
            w2 = self._compute_bivector_omega_2d(y_pred, K)
            w_eff = 0.5 * (w1 + w2)
            y_corr = self._apply_bivector_step_2d(y0, w_eff, dt)

            lte = self._estimate_lte(w1, w2, dt)

        elif self.dim == 3:
            v12_1, v13_1, v23_1 = self.compute_bivector_omega_3d(y0, K)
            y_pred = self._apply_bivector_step_3d(y0, v12_1, v13_1, v23_1, dt)

            v12_2, v13_2, v23_2 = self._compute_bivector_omega_3d(y_pred, K)
            v12_eff = 0.5 * (v12_1 + v12_2)
            v13_eff = 0.5 * (v13_1 + v13_2)
            v23_eff = 0.5 * (v23_1 + v23_2)
            y_corr = self._apply_bivector_step_3d(y0, v12_eff, v13_eff, v23_eff, dt)

            # Stack the three planes into (N, 3) so ONE error estimator serves both dimensions.
            w1 = np.stack([v12_1, v13_1, v23_1], axis=-1)
            w2 = np.stack([v12_2, v13_2, v23_2], axis=-1)
            lte = self._estimate_lte(w1, w2, dt)

        else:
            raise ValueError(
                f"Unsopported dim-{self.dim}; predictor-corrector supports dim in (2, 3)."
            )

        return y_corr, lte

    def step_adaptive_embedded(
        self,
        K: float,
        dt_current: float,
        rtol: float = 1e-5,
        atol: float = 1e-7,
        dt_min: float = 1e-5,
        dt_max: float = 0.1,
    ) -> AdaptiveStepResult:
        """Attempt a single adaptive embedded step on Spin(n) and propose the next step size.

        Wraps ``step_predictor_corrector`` with an elementary step-size controller. On acceptance the solver state is
        advanced and committed; on rejection the state is restored and a reduced trial step is proposed.


        Parameters
        ----------
        K : float
            Global coupling strength. Must be non-negative.
        dt_current :  float
            Trial step size for this attempt. Must be strictly positive.
        rtol : float, optional
            Relative tolerance contribution. Default ``1e-5``.
        atol : float, optional
            Absolute tolerance floor, in radians. Default ``1e-7``.
        dt_min : float, optional
            Lower clamp on any proposed step size. Default ``1e-5``.
        dt_max :
            Upper clamp on any proposed step size. Default ``0.1``.

        Returns
        -------
        AdaptiveStepResult
            ``(dt_taken, dt_next, status)``. ``dt_taken`` is ``0.0`` on any non-acceptance.

        Notes
        -----
        CONTROLLER EXPONENT: the embedded estimate tracks the 1st-order parameter, so the scaling exponent is
        ``1 / (q + 1) = 1/2``, NOT ``1/3``. See the derivation block. Getting this wrong makes the asymptotic step-size
        law ``dt ~ tol^(1/3)`` instead of ``dt ~ tol^(1/2)`` and will fail the controller-law assertion in the sanity
        check notebook.

        PROGRESS GUARANTEE: a rejected step is never allowed to propose a step size greater than or equal to the one
        that just failed. If shrinking cannot make progress (the proposal clamps back up to ``dt_current``), the status
        becomes `DT_MIN_EXHAUSTED` instead of looping forever.

        REPRODUCIBILITY CAVEAT: the controller is deterministic, so a fixed seed plus a recorded dt history replays
        bitwise. What adaptive stepping DOES break is comparison against a fixed-grid baseline -- run the
        ``rk45_parity_rmse`` failure-mode check in fixed-dt mode, or interpolate both solutions onto a common grid.
        """
        validate_non_negative_scalar(K, "K")
        validate_positive_scalar(dt_current, "dt_current")
        validate_positive_scalar(rtol, "rtol")
        validate_positive_scalar(atol, "atol")
        validate_positive_scalar(dt_min, "dt_min")
        validate_positive_scalar(dt_max, "dt_max")

        if dt_min >= dt_max:
            raise ValueError(
                f"dt_main ({dt_min:g}) must be strictly less than dt_max ({dt_max:g})."
            )

        # Snapshot: the trial step is pure, so this is the only state we might need to restore.
        y_backup = self._rotor_array.copy()

        y_corr, lte = self.step_predictor_corrector(K, dt_current)

        tol = self._effective_tolerance(rtol, atol)
        s = _ADAPTIVE_SAFETY * (tol / (lte + _ADAPTIVE_EPS)) ** 0.5
        s = float(np.clip(s, _ADAPTIVE_S_FLOOR, _ADAPTIVE_S_CEIL))

        # ---- ACCEPT ----------------------------------------------------------------------------
        if lte <= tol:
            self._rotor_array = y_corr
            self._consecutive_rejections = 0
            dt_next = float(np.clip(dt_current * s, dt_min, dt_max))
            return AdaptiveStepResult(dt_current, dt_next, AdaptiveStatus.ACCEPTED)

        # ---- REJECT ----------------------------------------------------------------------------
        self._rotor_array = y_backup
        self._consecutive_rejections += 1

        # min(s, 1.0) is belt-and braces: on rejection s <= safety < 1 by construction, but the clamp makes the "never
        # grow a failed step" invariant explicit rather than incidental.
        dt_proposed = float(np.clip(dt_current * min(s, 1.0), dt_min, dt_max))

        if dt_proposed >= dt_current:
            warnings.warn(
                f"⚠️ Adaptive stepper cannot reduce dt below {dt_current:g} (dt_min={dt_min:g}); "
                f"last LTE={lte:.3e} exceeded tol={tol:.3e}. Loosen rtol/atol, lower dt_min, or "
                f"inspect the stiffness regime near K_c.",
                RuntimeWarning,
                stacklevel=2,
            )
            return AdaptiveStepResult(0.0, dt_curent, AdaptiveStatus.DT_MIN_EXHAUSTED)

        return AdaptiveStepResult(0.0, dt_proposed, AdaptiveStatus.REJECTED)


    def simulate(
        self,
        K: float,
        t_eval: TimeArray,
        dt_internal: float | None = None,
        enforce_nyquist: bool = True,
        max_phase_increment: float = 1.0,
        method: str = "fast",
        adaptive_rtol: float = 1e-5,
        adaptive_atol: float = 1e-7,
        dt_min: float = 1e-5,
        dt_max: float | None = None,        # None -> dt_internal
    ) -> tuple[TimeArray, PhaseArray]:
        """
        Run a full rotor simulation.

        Parameters
        ----------
        K : float
            Coupling strength.
        t_eval : TimeArray
            Output timestamps (must be monotonically increasing, begin at zero).
        dt_internal : float, optional
            Internal Euler timestep. If None, infer from output spacing.
        enforce_nyquist : bool, optional
            If True, apply Nyquist-inspired temporal-resolution criterion.
        max_phase_increment : float, optional
            Maximum estimated angular phase advance per internal step (radians).
        method : str, optional
            Stepping method to use: 'fast' (vectorized order parameter Euler),
            'standard' (standard pairwise Euler), or 'geometric' (pure GA bivector torque Euler).
            Default is 'fast'.

        Returns
        -------
        tuple[TimeArray, PhaseArray]
            ``(times, phases)`` where ``phases`` has shape ``(len(t_eval),N)``.

        Raises
        ------
        ValueError
            If the time axis or timestep paramaters are invalid, or if method is unrecognized.
        """
        validate_non_negative_scalar(K, "K")
        validate_time_axis(t_eval)

        if t_eval.size < 2:
            raise ValueError("❌ t_eval must contain at least two time points.")

        if not np.isclose(t_eval[0], 0.0):
            raise ValueError("❌ t_eval must begin at 0.0")

        if dt_internal is not None:
            validate_positive_scalar(dt_internal, "dt_internal")

        validate_positive_scalar(max_phase_increment, "max_phase_increment")

        output_dt = np.diff(t_eval)

        if dt_internal is None:
            dt_internal = float(np.min(output_dt)) * 0.1

        # Nyquist-inspired temporal-resolution check and safe sub-stepping
        if enforce_nyquist:
            max_omega = float(np.max(np.abs(self.omegas)))
            estimated_max_rate = max_omega + abs(K)

            if estimated_max_rate > 0.0:
                nyquist_dt = 1.0 / (2.0 * estimated_max_rate)
                phase_increment_dt = max_phase_increment / estimated_max_rate
                dt_safe = min(nyquist_dt, phase_increment_dt)

                if dt_internal > dt_safe:
                    warnings.warn(
                        f"⚠️ Temporal resolution warning: dt_internal={dt_internal:.6g} exceeds "
                        f"the stability/Nyquist threshold ({dt_safe:.6g}) for max rate {estimated_max_rate:.6g}. "
                        f"Automatically adapting dt_internal to {dt_safe:.6g} to preserve dynamics without modifying frequencies.",
                        RuntimeWarning,
                        stacklevel=2,
                    )
                    dt_internal = dt_safe

        method_norm = method.lower()
        valid_methods = (
            "rkmk4",
            "rkmk",
            "rk4",
            "geometric_rk4",
            "midpoint",
            "midpoint_geometric",
            "euler_midpoint",
            "vectorized_geometric",
            "geometric",
            "euler_geometric",
            "rotor_geometric",
            "fast",
            "euler_fast",
            "fast_euler",
            "standard",
            "euler",
            "euler_standard",
            "predictor_corrector",
            "pc",
            "adaptive",
            "adaptive_embedded",
            "embedded",
        )
        if method_norm not in valid_methods:
            raise ValueError(
                f"❌ Unknown simulation method: '{method}'. Expected one of: "
                f"'rkmk4', 'midpoint', 'vectorized_geometric', 'fast', 'standard', 'adaptive', 'adaptive_embedded', "
                f"'embedded')."
            )

        times: list[float] = []
        all_phases: list[PhaseArray] = []

        current_time = float(t_eval[0])
        current_phases = self.extract_phases()
        times.append(current_time)
        all_phases.append(current_phases.copy())

        for t_out in t_eval[1:]:
            while current_time < t_out - 1e-12:
                dt = min(dt_internal, t_out - current_time)
                if method_norm in ("rkmk4", "rkmk", "rk4", "geometric_rk4"):
                    self.step_rkmk4(K, dt)
                elif method_norm in (
                    "midpoint",
                    "midpoint_geometric",
                    "euler_midpoint",
                ):
                    self.step_midpoint_geometric(K, dt)
                elif method_norm in (
                    "vectorized_geometric",
                    "geometric",
                    "euler_geometric",
                    "rotor_geometric",
                ):
                    self.step_euler_vectorized_geometric(K, dt)
                elif method_norm in ("standard", "euler", "euler_standard"):
                    self.step_euler(K, dt)
                elif method_norm in ("adaptive", "adaptive_embedded", "embedded"):
                    dt_trial = dt_internal
                    dt_ceiling = dt_max if dt_max is not None else dt_internal
                    while current_time < t_out - 1e-12:
                        dt_trial = min(dt_trial, t_out - current_time)
                        result = self.step_adaptive_embedded(
                            K,
                            dt_current=dt_trial,
                            rtol=adaptive_rtol,
                            atol=adaptive_atol,
                            dt_min=dt_min,
                            dt_max=dt_ceiling,
                        )
                        if result.status == AdaptiveStatus.DT_MIN_EXHAUSTED:
                            raise RuntimeError(
                                f"Adaptive stepper exhausted dt_min={dt_min:g} at t={current_time:.6g}."
                            )
                        if result.accepted:
                            current_time += result.dt_taken
                        dt_trial = result.dt_next
                else:
                    while current_time < t_out - 1e-12:
                        dt = min(dt_internal, t_out - current_time)
                    self.step_euler_fast(K, dt)

                current_time += dt

            # Extract phases once per output point for performance
            current_phases = self.extract_phases()
            times.append(float(t_out))
            all_phases.append(current_phases.copy())

        # Sync final rotor states from internal array
        self._sync_rotors_from_array()

        return np.asarray(times), np.asarray(all_phases)

class AdaptiveStatus(IntEnum):
    """Outcome of a single adaptive trial step.

    A bare bool cannot express "rejected AND we hae run out of room to shrink". That third state is what prevents an
    outer driver loop from spinning forever at dt_min.
    """

    ACCEPTED = 0
    REJECTED = 1
    DT_MIN_EXHAUSTED = 3


class AdaptiveStepResult(NamedTuple):
    """Result of one adaptive trial step.

    Still unpacks as plain 3-tuple, so ``dt_taken, dt_next, s tatus = result`` works, but the named fields keep cell
    sites still readable.

    Attributes
    ----------
    dt_taken : float
        Step size actually consumed. Zero when the step was rejcected.
    dt_next : float
        Suggested trial step size for the next attempt.
    status : AdaptiveStatus
        Acceptance outcome.
    """

    dt_taken: float
    dt_next: float
    status: AdaptiveStatus

    @property
    def accepted(self) -> bool:
        """True only when the step size was accepted."""
        return self.status == AdaptiveStatus.ACCEPTED

# Controller constants -- single source of truth
_ADAPTIVE_SAFETY: Final[float] = 0.85
_ADAPTIVE_S_FLOOR: Final[float] = 0.2
_ADAPTIVE_S_CEIL: Final[float] = 5.0
_ADAPTIVE_EPS: Final[float] = 1e-15
_ROTOR_ANGLE_SCALE: Final[float] = 1.0

# ---------------------------------------------------------------------------- #
# 2️⃣ Public Functional API
# ---------------------------------------------------------------------------- #


def step_rkmk4(
    solver: RotorSolver,
    K: float,
    dt: float,
) -> NDArray[np.floating]:
    """
    Perform a 4th-order Runge-Kutta-Munthe-Kaas (RKMK4) Lie-group geometric step.

    Parameters
    ----------
    solver : RotorSolver
        Rotor solver instance.
    K : float
        Coupling strength (non-negative).
    dt : float
        Time step size.

    Returns
    -------
    NDArray[np.floating]
        Updated internal rotor state array.
    """
    solver.step_rkmk4(K, dt)
    return solver._rotor_array


# --------------------------------------------------------------------------- #
# 💨 Smoke test
# --------------------------------------------------------------------------- #
def _run_smoke_test() -> None:
    """Exercise initialization, representation, dynamics, observables, and validation."""
    print("💨 Running RotorSolver smoke test...")

    # ==================================================================
    # 💫 Rotor solver
    # ==================================================================
    print(" 💫 Testing RotorSolver (📐 Geometric Algebra)...")

    try:
        rotor = RotorSolver(
            n_oscillators=10,
            dim=2,
            seed=27,
        )

        # --------------------------------------------------------------
        # Test 1: Initial state representation
        # --------------------------------------------------------------
        assert rotor.N == 10
        assert rotor.dim == 2
        assert len(rotor.rotors) == 10
        assert rotor.omegas.shape == (10,)

        phases_init = rotor.extract_phases()

        assert phases_init.shape == (10,)
        assert np.all(phases_init >= 0.0)
        assert np.all(phases_init < 2.0 * np.pi)

        print(" ... ✔️ Initial rotor state test passed")

        # --------------------------------------------------------------
        # Test 2: Rotor → phase → rotor round trip
        # --------------------------------------------------------------
        reconstructed_rotors = [
            np.exp(-rotor.B_plane * phase / 2.0) for phase in phases_init
        ]

        for original, reconstructed in zip(
            rotor.rotors,
            reconstructed_rotors,
            strict=True,
        ):
            assert np.allclose(
                original.value,
                reconstructed.value,
                atol=1e-12,
            )

        print(" ... ✔️ Rotor/phase round-trip test passed")

        # --------------------------------------------------------------
        # Test 3: Complex order parameter representation
        # --------------------------------------------------------------
        complex_r = rotor.get_complex_order_parameter()
        sync_strength = rotor.get_synchronization_strength()

        assert isinstance(complex_r, complex)
        assert np.isfinite(complex_r.real)
        assert np.isfinite(complex_r.imag)

        assert 0.0 <= sync_strength <= 1.0

        direct_r = np.abs(np.mean(np.exp(1j * phases_init)))

        assert np.isclose(
            sync_strength,
            direct_r,
            rtol=1e-12,
            atol=1e-12,
        )

        print(" ... ✔️ Standard order-parameter test passed")

        # --------------------------------------------------------------
        # Test 4: Attractive coupling direction
        # --------------------------------------------------------------
        directional = RotorSolver(
            n_oscillators=2,
            dim=2,
            seed=27,
        )

        directional.omegas[:] = 0.0

        # Construct two oscillators separated by pi/2.
        directional.rotors = [
            np.exp(-directional.B_plane * 0.0 / 2.0),
            np.exp(-directional.B_plane * (np.pi / 2.0) / 2.0),
        ]

        before = directional.extract_phases()

        separation_before = np.abs(np.angle(np.exp(1j * (before[1] - before[0]))))

        directional.step_euler(
            K=1.0,
            dt=0.01,
        )

        after = directional.extract_phases()

        separation_after = np.abs(np.angle(np.exp(1j * (after[1] - after[0]))))

        assert separation_after < separation_before

        print(" ... ✔️ Attractive coupling direction test passed")

        # --------------------------------------------------------------
        # Test 5: Euler step actually evolves the state
        # --------------------------------------------------------------
        rotor_copy = RotorSolver(
            n_oscillators=10,
            dim=2,
            seed=27,
        )

        phases_before = rotor_copy.extract_phases()

        rotor_copy.step_euler(
            K=1.2,
            dt=0.01,
        )

        phases_after = rotor_copy.extract_phases()

        assert phases_after.shape == (10,)
        assert np.all(np.isfinite(phases_after))

        assert not np.allclose(
            phases_before,
            phases_after,
        )

        print(" ... ✔️ Euler evolution test passed")

        # --------------------------------------------------------------
        # Test 5b: Fast Euler step consistency with standard Euler step
        # --------------------------------------------------------------
        rotor_standard = RotorSolver(
            n_oscillators=15,
            dim=2,
            seed=42,
        )
        rotor_fast = RotorSolver(
            n_oscillators=15,
            dim=2,
            seed=42,
        )

        # Confirm initial states match
        assert np.allclose(
            rotor_standard.extract_phases(),
            rotor_fast.extract_phases(),
            rtol=1e-12,
            atol=1e-12,
        )

        # Step both solvers multiple times with identical parameters
        for _ in range(5):
            rotor_standard.step_euler(K=1.5, dt=0.02)
            rotor_fast.step_euler_fast(K=1.5, dt=0.02)

        standard_phases = rotor_standard.extract_phases()
        fast_phases = rotor_fast.extract_phases()

        assert fast_phases.shape == (15,)
        assert np.all(np.isfinite(fast_phases))

        assert np.allclose(
            standard_phases,
            fast_phases,
            rtol=1e-10,
            atol=1e-12,
        )

        assert np.isclose(
            rotor_standard.get_synchronization_strength(),
            rotor_fast.get_synchronization_strength(),
            rtol=1e-10,
            atol=1e-12,
        )

        print(" ... ✔️ Fast Euler consistency test passed")

        # --------------------------------------------------------------
        # Test 5c: Geometric Euler step consistency with standard Euler step
        # --------------------------------------------------------------
        rotor_geom = RotorSolver(
            n_oscillators=15,
            dim=2,
            seed=42,
        )

        for _ in range(5):
            rotor_geom.step_euler_geometric(K=1.5, dt=0.02)

        geom_phases = rotor_geom.extract_phases()

        assert geom_phases.shape == (15,)
        assert np.all(np.isfinite(geom_phases))

        assert np.allclose(
            fast_phases,
            geom_phases,
            rtol=1e-10,
            atol=1e-12,
        )

        print(" ... ✔️ Geometric Euler consistency test passed")

        # --------------------------------------------------------------
        # Test 6: Global U(1) phase-shift invariance
        # --------------------------------------------------------------
        original = RotorSolver(
            n_oscillators=10,
            dim=2,
            seed=27,
        )

        shifted = RotorSolver(
            n_oscillators=10,
            dim=2,
            seed=27,
        )

        original_phases = original.extract_phases()
        shifted_phases = shifted.extract_phases()

        assert np.allclose(
            original_phases,
            shifted_phases,
        )

        shift = 0.73

        shifted_phases = shifted_phases + shift

        shifted.rotors = [
            np.exp(-shifted.B_plane * phase / 2.0) for phase in shifted_phases
        ]

        original_r = original.get_synchronization_strength()
        shifted_r = shifted.get_synchronization_strength()

        assert np.isclose(
            original_r,
            shifted_r,
            rtol=1e-10,
            atol=1e-12,
        )

        print(" ... ✔️ Global U(1) phase-shift invariance test passed")

        # --------------------------------------------------------------
        # Test 7: Full simulation
        # --------------------------------------------------------------
        simulation = RotorSolver(
            n_oscillators=10,
            dim=2,
            seed=27,
        )

        times = np.linspace(
            0.0,
            1.0,
            21,
        )

        sim_times, sim_phases = simulation.simulate(
            K=1.2,
            t_eval=times,
            dt_internal=0.01,
        )

        assert sim_times.shape == times.shape

        assert np.allclose(
            sim_times,
            times,
        )

        assert sim_phases.shape == (
            len(times),
            10,
        )

        assert np.isfinite(sim_phases).all()

        print(" ... ✔️ Full rotor simulation test passed")

        # --------------------------------------------------------------
        # Test 8: Invalid timestep validation
        # --------------------------------------------------------------
        try:
            simulation.simulate(
                K=1.2,
                t_eval=times,
                dt_internal=-0.01,
            )
        except ValueError:
            print(" ... ✔️ Invalid timestep validation passed")
        else:
            raise AssertionError(" ... ❌ RotorSolver accepted a negative dt_internal")

        # --------------------------------------------------------------
        # Test 9: Invalid time axis validation
        # --------------------------------------------------------------
        try:
            simulation.simulate(
                K=1.2,
                t_eval=np.array([0.0, 0.5, 0.4]),
            )
        except ValueError:
            print(" ... ✔️ Invalid time-axis validation passed")
        else:
            raise AssertionError(" ... ❌ RotorSolver accepted a non-monotonic t_eval")

        # --------------------------------------------------------------
        # Test 10: Future adaptive method remains unimplemented
        # --------------------------------------------------------------
        adaptive = RotorSolver(n_oscillators=10, dim=2, seed=27)

        dt_trial = 0.05
        accepted_count = 0
        rejectred_count = 0

        for _ in range (300):
            result = adaptive.step_adaptive_embedded(
                K=1.5,
                dt_current=dt_trial,
                rtol=1e-6,
                atol=1e-9,
                dt_min=1e-7,
                dt_max=0.1,
            )
            if result.accepted:
                accepted_count += 1
            else:
                rejectred_count += 1
            dt_trial = result.dt_next

            normas = np.sum(adaptive._rotor_array**2, axis=1)
            assert np.allclose(norms, 1.0, atol=1e-12), (
                "Rotor norm drifted off the Spin(n) manifold under adaptive sampling."
            )

        assert accepted_count > 250, "Controller rejected far too many steps."
        assert np.all(np.isfinite(adaptive._rotor_array))

        print(
            f" ... ✔️ Adaptive embedded step test passed "
            f"(accepted={accepted_count}, rejected={rejectred_count})"
        )

        # --------------------------------------------------------------
        # Test 11: Nyquist temporal adaptation warning & frequency preservation
        # --------------------------------------------------------------
        nyquist_test = RotorSolver(n_oscillators=3, dim=2, seed=42)
        initial_omegas = np.array([100.0, 0.0, -100.0])
        nyquist_test.omegas = initial_omegas.copy()
        # Safe limit for dt=0.1 with omega=100 is <= 0.005
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            nyquist_test.simulate(
                K=0.0,
                t_eval=np.linspace(0, 1, 11),
                dt_internal=0.1,
                enforce_nyquist=True,
            )
            assert any("Temporal resolution warning" in str(warn.message) for warn in w)

        # Verify omegas were never mutated in-place
        assert np.allclose(nyquist_test.omegas, initial_omegas)
        print(" ... ✔️ Temporal adaptation & frequency non-mutation test passed")

        # --------------------------------------------------------------
        # Test 12: 3D Lohe Model (S^2)
        # --------------------------------------------------------------
        print("🚀 Running Test 12: 3D Lohe Model (S^2) synchronization...")
        solver_3d = RotorSolver(n_oscillators=10, dim=3, seed=42)

        # Initial synchronization strength should be low
        r_start = solver_3d.get_synchronization_strength()
        print(f"  - Initial R: {r_start:.4f}")

        # Run attractive simulation with RKMK4 in 3D
        solver_3d.simulate(
            K=5.0, t_eval=np.linspace(0, 2, 21), dt_internal=0.05, method="rkmk4"
        )

        r_end = solver_3d.get_synchronization_strength()
        print(f"  - Final R: {r_end:.4f}")
        assert r_end > r_start
        print(" ... ✔️ 3D Lohe Model test passed")

        # --------------------------------------------------------------
        # Test 13: 4th-Order Lie-Group RKMK4 vs Midpoint vs Vectorized Euler
        # --------------------------------------------------------------
        init_p = np.array([0.0, 0.5, 1.2])
        freqs = np.array([0.2, -0.1, 0.0])
        s_rkmk = RotorSolver(
            n_oscillators=3, dim=2, natural_frequencies=freqs, initial_phases=init_p
        )
        s_mid = RotorSolver(
            n_oscillators=3, dim=2, natural_frequencies=freqs, initial_phases=init_p
        )
        s_vec = RotorSolver(
            n_oscillators=3, dim=2, natural_frequencies=freqs, initial_phases=init_p
        )

        t_eval_test = np.linspace(0, 1.0, 21)
        _, ph_rkmk = s_rkmk.simulate(
            K=1.5, t_eval=t_eval_test, dt_internal=0.01, method="rkmk4"
        )
        _, ph_mid = s_mid.simulate(
            K=1.5, t_eval=t_eval_test, dt_internal=0.01, method="midpoint"
        )
        _, ph_vec = s_vec.simulate(
            K=1.5, t_eval=t_eval_test, dt_internal=0.01, method="vectorized_geometric"
        )

        # All geometric methods should stay bounded and close on small dt
        assert np.allclose(ph_rkmk, ph_mid, atol=1e-2)
        assert np.allclose(ph_rkmk, ph_vec, atol=2e-2)

        # Test standalone step_rkmk4 function
        s_func = RotorSolver(
            n_oscillators=3, dim=2, natural_frequencies=freqs, initial_phases=init_p
        )
        updated_rotors = step_rkmk4(s_func, K=1.5, dt=0.01)
        assert isinstance(updated_rotors, np.ndarray)
        assert updated_rotors.shape == (3, 2)
        assert np.allclose(s_func._rotor_array, updated_rotors)
        print(" ... ✔️ RKMK4 and Midpoint Lie-group integrators test passed")

    except ImportError:
        print(" ⚠️ Skipping geometric algebra tests " "(clifford not installed)")

    print("\n✅ All RotorSolver smoke tests passed")


# ---------------------------------------------------------------------------- #
# 🔥 Entry point
# ---------------------------------------------------------------------------- #


def main() -> None:
    _run_smoke_test()


if __name__ == "__main__":
    main()
