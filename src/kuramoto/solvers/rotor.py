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
Last updated: 09-2026
"""

from __future__ import annotations

import warnings
from typing import Final

import numpy as np
from numpy.typing import NDArray

# Import RNG utilities from the central utils module
from kuramoto.utils import get_rng

# Validation imports support both package execution and direct script execution.
from kuramoto.validation import (
    validate_positive_scalar,
    validate_time_axis,
)

__all__: list[str] = ["RotorSolver"]

# ---------------------------------------------------------------------------- #
# 🎭 Type Aliases
# ---------------------------------------------------------------------------- #

PhaseArray = NDArray[np.floating]
TimeArray = NDArray[np.floating]


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

        Raises
        ------
        ImportError
            If the ``clifford`` package is not installed.
        ValueError
            If ``dim < 2`` or if the oscillator count is invalid.
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

        self.rng = get_rng(seed)

        self.N = n_oscillators
        self.dim = dim
        self.layout, self.blades = Cl(dim)

        # Rotation plane: for 2D this is e12, for 3D typically xy-plane
        plane_key = f'e{dim-1}{dim}' if dim <= 3 else 'e12'
        self.B_plane = self.blades[plane_key]

        # Precompute the slot of rotation plane in coefficent array
        self._blade_idx = int(
            np.nonzero(np.asarray(self.B_plane.value))[0][0]
        )

        # Initial condition
        self.rotors = self._random_rotors()
        self.omegas = self.rng.uniform(
            -1.0, 1.0, n_oscillators,
        )

    def _random_rotors(self) -> list:
        """Generate random initial rotors."""
        phases = self.rng.uniform(0, 2 * np.pi, self.N)
        return [np.exp(-self.B_plane * p / 2.0) for p in phases]

    def extract_phases(self) -> PhaseArray:
        """"
        Extract physical phase angles from current rotor states.

        Returns
        -------
        PhaseArray
            Phases of shape ``(N,)``, wrapped to ``[0, 2*pi)``.
        """
        phases = []
        for r in self.rotors:
            scalar = float(r.value[0])
            bivector = float(r.value[self._blade_idx])
            phases.append((2.0 * np.arctan2(-bivector, scalar)) % (2.0 * np.pi))
        return np.array(phases)

    def step_euler(
        self,
        K: float,
        dt: float,
    ) -> None:
        """
        Advance the Kuramoto system by one explicit Euler step.

        The standard attractive Kuramoto interaction is

            dtheta_i/dt = omega_i + (K/N) * sum_j sin(theta_j - theta_i).

        Parameters
        ----------
        K : float
            Coupling strength (positive for attraction).
        dt : float
            Timestep size.
        """
        validate_positive_scalar(K, "K")
        validate_positive_scalar(dt, "dt")

        phases = self.extract_phases()

        # Standard attractive Kuramoto coupling
        diff_matrix = phases[np.newaxis, :] - phases[:, np.newaxis]
        coupling = (K / self.N) * np.sum(np.sin(diff_matrix), axis=1)

        # Update phases
        new_phases = phases + dt * (self.omegas + coupling)

        # Reconstruct rotors from updated phases
        self.rotors = [np.exp(-self.B_plane * p / 2.0) for p in new_phases]

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
        Therefore rotor coefficients must not be averaged directly.
        This method extracts physical phases first for canonical Kuramoto observvable.
        """
        phases = self.extract_phases()
        return complex(np.mean(np.exp(1j * phases)))

    def get_synchronization_strength(self) -> float:
        """Return the magnitude of the standard Kuramoto order parameter."""
        return float(abs(self.get_complex_order_parameter()))

    def simulate(
        self,
        K: float,
        t_eval: TimeArray,
        dt_internal: float | None = None,
        enforce_nyquist: bool = True,
        max_phase_increment: float = 1.0,
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

        Returns
        -------
        tuple[TimeArray, PhaseArray]
            ``(times, phases)`` where ``phases`` has shape ``(len(t_eval),N)``.

        Raises
        ------
        ValueError
            If the time axis or timestep paramaters are invalid.
        """
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

        # Nyquist-inspired temporal-resolution check
        if enforce_nyquist:
            max_omega = float(np.max(np.abs(self.omegas)))
            estimated_max_rate = max_omega + abs(K)

            if estimated_max_rate > 0.0:
                nyquist_dt = 1.0 / (2.0 * estimated_max_rate)
                phase_increment_dt = max_phase_increment / estimated_max_rate
                dt_safe = min(nyquist_dt, phase_increment_dt)

                if dt_internal > dt_safe:
                    warnings.warn(
                        f"dt_internal={dt_internal:.6g} may under-resolve the oscillator dynamics. "
                        f"The current Nyquist-inspired resolution estimate gives dt <= {nyquist_dt:.6g}, "
                        f"while the maximum phase increment constraint gives dt <= {phase_increment_dt:.6h}. "
                        f"Recommended dt <= {dt_safe:.6g} for estimated maximum phase rate {estimated_max_rate:.6g} "
                        f"rad/time. This is a temporal-resolution heuristic, not a formal Euler stability bound.",
                        RuntimeWarning,
                        stacklevel=2,
                    )

        times: list[float] = []
        all_phases: list[PhaseArray] = []

        current_time = float(t_eval[0])

        for t_out in t_eval:
            while current_time < t_out - 1e-12:
                dt = min(dt_internal, t_out - current_time)
                self.step_euler(K, dt)
                current_time += dt

            times.append(float(t_out))
            all_phases.append(self.extract_phases())

        return np.asarray(times), np.asarray(all_phases)

    def step_rk45_adaptive(
        self,
        K: float,
        dt: float,
        rtol: float = 1e-6,
    ) -> tuple[float, float]:
        """
        Future work: adaptive RK45-like step with error estimation.

        This method is intentionally retained as a development placeholder to preserve the intended future extenion
        point.


        Raises
        ------
        NotImplementedError
            Always, until the adaptive rotor integrator is implemented.
        """
        raise NotImplementedError(
            "✖️🚧 Adaptive RK45-like rotor stepping is reserved for future development."
        )

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
            np.exp(-rotor.B_plane * phase / 2.0)
            for phase in phases_init
        ]

        for original, reconstructed in zip(
            rotor.rotors,
            reconstructed_rotors,
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

        direct_r = np.abs(
            np.mean(np.exp(1j * phases_init))
        )

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

        separation_before = np.abs(
            np.angle(
                np.exp(
                    1j * (before[1] - before[0])
                )
            )
        )

        directional.step_euler(
            K=1.0,
            dt=0.01,
        )

        after = directional.extract_phases()

        separation_after = np.abs(
            np.angle(
                np.exp(
                    1j * (after[1] - after[0])
                )
            )
        )

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
            np.exp(
                -shifted.B_plane * phase / 2.0
            )
            for phase in shifted_phases
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
            raise AssertionError(
                " ... ❌ RotorSolver accepted a negative dt_internal"
            )


        # --------------------------------------------------------------
        # Test 9: Invalid time axis validation
        # --------------------------------------------------------------
        try:
            simulation.simulate(
                K=1.2,
                t_eval=np.array(
                    [0.0, 0.5, 0.4]
                ),
            )
        except ValueError:
            print(" ... ✔️ Invalid time-axis validation passed")
        else:
            raise AssertionError(
                " ... ❌ RotorSolver accepted a non-monotonic t_eval"
            )

        # --------------------------------------------------------------
        # Test 10: Future adaptive method remains unimplemented
        # --------------------------------------------------------------
        try:
            simulation.step_rk45_adaptive(
                K=1.2,
                dt=0.01,
            )
        except NotImplementedError:
            print(" ... 🚧 Future KR45 placeholder test passed")
        else:
            raise AssertionError(
                " ... ❌ step_rk45_adaptive should remain explicitly unimplemented until appropriate updates are "
                "implemented"
            )

        print(" ... ✔️ Future adaptive-method boundary test passed")

    except ImportError:
        print(
            " ⚠️ Skipping geometric algebra tests "
            "(clifford not installed)"
        )

    print("\n✅ All RotorSolver smoke tests passed")

# ---------------------------------------------------------------------------- #
# 🔥 Entry point
# ---------------------------------------------------------------------------- #

def main() -> None:
    _run_smoke_test()


if __name__ == "__main__":
    main()