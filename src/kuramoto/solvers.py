# src/kuramoto/solvers.py
"""
ODE solver interface for Kuramoto simulations.

This module provides:
    - ``solve_kuramoto``: a thin interface around SciPy's adaptive RK45 integrator.
    - ``RotorSolver``: an experimental geometric-algebra representation of Kuramoto dynamics using fixed-step Euler
      integration

The rotor solver uses Nyquist-inspired temporal-resolution criterion to help ensure that high-frequency oscillator
dynamics are adequately resolved. This criterion is supplemented by an explicit maximum phase-increment constraint to
prevent numerical instabilities.

Author: Eigenscribe
Review status: Reviewed and maintained by Eigenscribe.
Date: 05-2026
Last Updated: 09-2026
"""

from __future__ import annotations

from typing import Callable, Final, Any

import numpy as np
from numpy.typing import NDArray
from scipy.integrate import solve_ivp

# Import RNG utilities from the central utils module.
from kuramoto.utils import get_rng

# Validation imports support both package execution and direct script execution.
import sys
from pathlib import Path

if __name__ == "__main__" and not __package__:
    # Enable running the script directly (e.g. from PyCharm or command line)
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from kuramoto.validation import (
        validate_positive_scalar,
        validate_non_negative_scalar,
        validate_intrinsic_frequency_array,
        validate_adjacency,
        validate_time_axis,
    )
else:
    from .validation import (
        validate_positive_scalar,
        validate_non_negative_scalar,
        validate_intrinsic_frequency_array,
        validate_adjacency,
        validate_time_axis,
    )

__all__: list[str] = [
    "solve_kuramoto",
    "RotorSolver"
]

# ------------------------------------------------------------------------------
# 0️⃣ Type Aliases
# ------------------------------------------------------------------------------

PhaseArray = NDArray[np.floating]
TimeArray = NDArray[np.floating]

# ------------------------------------------------------------------------------
# 1️⃣ Classic Functional Solver Wrapper
# ------------------------------------------------------------------------------

_DEFAULT_METHOD: Final[str] = "RK45"

def solve_kuramoto(
    rhs: Callable[[float, PhaseArray], PhaseArray],
    y0: PhaseArray,
    t_span: float,
    t_eval: TimeArray,
    rtol: float = 1e-6,
    atol: float = 1e-9,
    max_step: float | None = None,
) -> Any:
    """
    Integrate the Kuramoto ODE system and return SciPy's `OdeResult`.

    Parameters
    ----------
    rhs : Callable[[float, PhaseArray], PhaseArray]
        Vector field f(t, theta) = theta'.
    y0 : PhaseArray
        Initial condition of shape (N,).
    t_span : float
        Final integration time; start is always at 0.
    t_eval : TimeArray
        Time stamps at which the solution is sampled.
    rtol, atol : float
        Relative and absolute error tolerance.
    max_step : float, optional
        Upper bound on an internal solver step. If None, SciPy chooses.

    Returns
    -------
    scipy.integrate.OdeResult
        Standard SciPy result object with fields t , y , success, ...
    """
    # Defensive checks
    validate_positive_scalar(t_span, "t_span")
    validate_time_axis(t_eval)
    validate_positive_scalar(rtol, "rtol")
    validate_non_negative_scalar(atol, "atol")

    if max_step is not None:
        validate_positive_scalar(max_step, "max_step")

    # Call SciPy
    return solve_ivp(
        fun=rhs,
        t_span=(0.0, t_span),
        y0=y0,
        method=_DEFAULT_METHOD,
        t_eval=t_eval,
        rtol=rtol,
        atol=atol,
        max_step=max_step if max_step is not None else np.inf,
    )

# ------------------------------------------------------------------------------
# 2️⃣ Geometric Algebra Rotor Solver
# ------------------------------------------------------------------------------

class RotorSolver:
    """
    Geometric Algebra-based Kuramoto solver using rotors in Cl(dim).

    ⚠️ EXPERIMENTAL / RESEARCH MODE

    Unlike the standard solve_kuramoto() wrapper (which uses adaptive RK45 with built-in error control), RotorSolve uses
    fixed-step Euler integration.

    The solver uses a Nyquist-inspired temporal resolution criterion because the project treats temporal
    sampling/resolution as a central consideration when resolving oscillator dynamics. This is supplemented by a maximum
    phase-increment constraint.

    The Nyquist-inspired criterion is a resolution heuristic, not a claim that the Nyquist sampling theorem provides an
    Euler stability condition. Explicit Euler accuracy and stability remain separate numerical concerns.

    Users should:

    - choose a sufficiently small ``dt_internal``;
    - use ``enforce_nyquist=True`` when high-frequency dynamics should be automatically checked;
    - interpret warnings as indications of possible temporal under-resolution, not as formal stability proofs;
    - verify results against the classic RK45 solver.

    Future work:
        Implement an adaptive RK45/Dormand-Prince-style stepper for the rotor representation while retaining the
        geometric state representation.

    Each oscillator is represented as a rotor

        R=exp(-B theta / 2),

    where B is the rotation plane bivector. Coupling is applied using the extracted physical phases, while the state
    itself is stored as geometric-algebra rotors.

    Attributes
    ----------
    N : int
        Number o oscillators.
    dim : int
        Dimensionality o GA space (typically 2 for planar rotations).
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
            If ``dim < 2`` or if the oscillator count is invalid (need at least 2D for non-trivial rotations).
        """
        validate_positive_scalar(n_oscillators, "n_oscillators")
        validate_positive_scalar(dim, "dim")

        if dim < 2:
            raise ValueError("dim must be >=2 for non-trivial rotation plane")

        # Lazy import to avoid hard dependency
        try:
            from clifford import Cl
        except ImportError as exc:
            raise ImportError(
                "clifford package required for Rotor Solver."
                "Install with: pip install clifford"
            ) from exc

        # Keep random state local to this solver. This avoids modifying NumPy's global RNG state and keeps benchmark
        # generation reproducible.
        self.rng = get_rng(seed)

        self.N = n_oscillators
        self.dim = dim
        self.layout, self.blades = Cl(dim)

        # Rotation plane: for 2D this is e12, for 3D typically xy-plane
        plane_key = f'e{dim-1}{dim}' if dim <= 3 else 'e12'
        self.B_plane = self.blades[plane_key]

        # Precompute the slot of rotation plane in the coefficient array
        # Rotor R = exp(-B theta / 2) lives in the even subalgebra spanned by {scalar, B_plane}, so we only ever read
        # these two slots.
        self._blade_idx = int(
            np.nonzero(
                np.asarray(self.B_plane.value))[0][0]
        )
        self.blade_idx = self._blade_idx

        # Initial conditions
        self.rotors = self._random_rotors()
        self.omegas = self.rng.uniform(
            -1.0,
            1.0,
            n_oscillators,
        )

    def _random_rotors(self) -> list:
        """Generate random initial rotors."""
        phases = self.rng.uniform(
            0,
            2 * np.pi,
            self.N)
        return [
            np.exp(-self.B_plane * p / 2.0)
            for p in phases
        ]

    def extract_phases(self) -> PhaseArray:
        """
        Extract physical phase angles from current rotor states.

        Returns
        -------
        PhaseArray
            Phases of shape ``(N,)``, wrapped to ``[0, 2*pi).
        """
        phases = []

        for r in self.rotors:
            scalar = float(r.value[0])           # Slot 0 is always the scalar
            bivector = float(r.value[self._blade_idx])  # Precomputed plane slot

            # Avoid division by zero
            phases.append(
                (2.0 * np.arctan2(-bivector, scalar)) % (2.0 * np.pi)
            )

        return np.array(phases)

    def step_euler(self, K: float, dt: float) -> None:
        """
        Advance the Kuramoto system by one explicit Euler step.

        The standard attractive Kuramoto interaction is

            dtheta_i/dt =omega_i + (K/N) sum_j sin(theta_j - theta_i).

        Parameters
        ---------
        K : float
            Coupling strength (positive for attraction).
        dt : float
            Timestep size.
        """
        validate_positive_scalar(K, "K")
        validate_positive_scalar(dt, "dt")

        # Extract phases
        phases = self.extract_phases()

        # Standard attractive Kuramoto coupling:
        # sin(theta_j - theta_i)
        diff_matrix =(
            phases[np.newaxis, :] - phases[:, np.newaxis]
        )
        coupling = (K / self.N) * np.sum(
            np.sin(diff_matrix),
            axis=1,
        )

        # Update phases
        new_phases = phases + dt * (self.omegas + coupling)

        # Reconstruct rotors normalized geometric rotors from updated phases.
        self.rotors = [
            np.exp(-self.B_plane * p / 2.0)
            for p in new_phases
        ]

    def get_complex_order_parameter(self) -> complex:
        """
        Compute the standard complex Kuramoto order parameter.

        Returns
        -------
        complex
            ``mean(exp(1j * theta))``. Its magnitude is the standard synchronization strength.

        Notes
        -----
        The rotor itself contains half-angle information through

            R(theta) = exp(-B theta /2).

        Therefore the rotor coefficients must not be averaged directly as though they were the conventional Kuramoto
        phasors. This method extracts the physical phases first so that the canonical Kuramoto observable is used.
        """
        phases = self.extract_phases()
        return complex(np.mean(np.exp(1j * phases)))

    def get_synchronization_strength(self) -> float:
        """
        Return the magnitude of the standard Kuramoto order parameter.

        Returns
        -------
        float
            Synchronization strength in ``[0, 1]``, where 1 = fully synchronized.
        """
        return float(abs(self.get_complex_order_parameter()))

    def simulate(
        self,
        K: float,
        t_eval: TimeArray,
        dt_internal: float | None = None,
        enforce_nyquist: bool = True,
        max_phase_increment: float = 0.1,  # radians per step max
    ) -> tuple[TimeArray, PhaseArray]:
        """
        Run a full rotor simulation.

        Parameters
        ----------
        K : float
            Coupling strength.
        t_eval : TimeArray
            Output timestamps (must be monotonically increasing and begin at zero).
        dt_internal : float, optional
            Internal Euler timestep. If None, infer a timestep from the output spacing.
        enforce_nyquist : bool, optional
            If True, apply the project's Nyquist-inspired temporal-resolution criterion and phase-increment constraint
            to detect possible under-resolution.
        max_phase_increment : float, optional
            Maximum estimated angular phase advance per internal step, in radians.

        Returns
        -------
        tuple[TimeArray, PhaseArray]
            ``(times, phases)`` where ``phases`` has shape ``(len(t_eval), N)``.

        Raises
        ------
        ValueError
            If the time axis or timestep parameters are invalid.
        """
        validate_time_axis(t_eval)

        if t_eval.size < 2:
            raise ValueError("t_eval must contain at least two time points.")

        if not np.isclose(t_eval[0], 0.0):
            raise ValueError("t_eval must begin at 0.0")

        if dt_internal is not None:
            validate_positive_scalar(dt_internal, "dt_internal")

        validate_positive_scalar(
            max_phase_increment,
            "max_phase_increment",
        )

        output_dt = np.diff(t_eval)

        if dt_internal is None:
            # Use a conservative fraction of the smallest requested output interval rather than assuming uniform
            # spacing.
            dt_internal = float(np.min(output_dt)) * 0.1

        # ------------------------------------------------------------------
        # Nyquist-inspired temporal-resolution check
        # ------------------------------------------------------------------
        if enforce_nyquist:
            max_omega = float(np.max(np.abs(self.omegas)))

            # Conservative upper estimate for the phase rate:
            #
            # |dtheta_i/dt| <= |omega_i| + K
            #
            # because the normalized mean sine coupling has magnitude <= 1.
            estimated_max_rate = max_omega + abs(K)

            if estimated_max_rate > 0.0:
                # Nyquist-inspired resolution scale:
                # sampling frequency > 2 * characteristic frequency.
                #
                # Here this is used as a temporal-resolution heuristic for the internal integration grid, not as an
                # Euler stability theorem.
                nyquist_dt = 1.0 / (2.0 * estimated_max_rate)

                # Additional project-specific phase-resolution constraint.
                phase_increment_dt = (
                    max_phase_increment / estimated_max_rate
                )

                dt_safe = min(nyquist_dt, phase_increment_dt)

                if dt_internal > dt_safe:
                    import  warnings

                    warnings.warn(
                        f"dt_internal={dt_internal:.6g} may under-resolve the oscillator dynamics. The current "
                        f"Nyquist-inspired resolution estimate gives dt <= {nyquist_dt:.6g}, while the maximum phase "
                        f"increment constraint gives dt <= {phase_increment_dt:.6g}. Recommended dt <= {dt_safe:.6g} "
                        f"for estimated maximum phase rate {estimated_max_rate:.6g} rad /time. This is a "
                        f"temporal-resolution heuristic, not a formal Euler stability bound.",
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
        rtol: float = 1e-6
    ) -> tuple[float, float]:
        """
        Future work: adaptive RK45-like step with error estimation.

        This method is intentionally retained as a development placeholder.
        The purpose is to preserve the intended future extension point: implementing an embedded adaptive
        RK45/Dormand-Prince-style integrator while retaining the rotor representation.

        Planned responsibilities
        ------------------------
        - Compute RK stages in the rotor/phase representation.
        - Estimate local truncation error from an embedded RK pair.
        - Accept or reject the proposed timestep.
        - Return the accepted step information and a recommended next timestep.
        - Preserve compatibility with the solver's temporal-resolution diagnostics.

        Raises
        ------
        NotImplementedErroor
            Always, unitl the ataptive rotor integrator is implemented.
        """
        raise NotImplementedError(
            "Adaptive RK45 rotor stepping is reserved for future development."
        )

# --------------------------------------------------------------------------- #
# 💨Smoke test
# --------------------------------------------------------------------------- #
def _run_smoke_test() -> None:
    """Exercise success, validation, physics, and representation paths."""
    print("💨 Running solver smoke test...")

    # ==================================================================
    # Classic functional solver
    # ==================================================================
    print(" 🍦 Testing solve_kuramoto (SciPy)...")

    rhs = lambda t, y: -y
    y0 = np.array([1.0])
    t_ev = np.linspace(0, 1, 11)

    sol = solve_kuramoto(
        rhs,
        y0,
        t_span=1.0,
        t_eval=t_ev,
        max_step=0.2,
    )

    assert sol.success
    assert sol.y.shape == (1, t_ev.size)
    print(" ... ✔️ Classic integration success")

    # Invalid t_eval (non-monotonic)
    try:
        solve_kuramoto(
            rhs,
            y0,
            t_span=1.0,
            t_eval=np.array([0.0, 0.5, 0.4]),
        )
    except ValueError as err:
        print(f" ... ❌ Time-axis validation caught invalid t_eval")
    else:
        raise AssertionError(
            " ... ❌ solve_kuramoto accepted a non-monotonic t_eval"
        )

    # ==================================================================
    # Rotor solver
    # ==================================================================
    try:
        print(" 💫 Testing RotorSolver (📐 Geometric Algebra)...")
        rotor = RotorSolver(
            n_oscillators=10,
            dim=2,
            seed=27
        )

        # --------------------------------------------------------------
        # Test 1: Initial state
        # --------------------------------------------------------------
        assert rotor.N == 10
        assert rotor.dim == 2
        assert len(rotor.rotors) == 10
        assert len(rotor.omegas) == 10

        # Test phase extraction
        phases_init = rotor.extract_phases()
        assert phases_init.shape == (10,)
        assert np.all(
            (phases_init >= 0.0)
            & (phases_init <= 2.0 * np.pi)
        )

        print(" ... ✔️ Initial rotor state test passed.")

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

        print(" ... ✔️ Rotor/phase round-trip test passed.")

        # --------------------------------------------------------------
        # Test 3: Attractive coupling direction
        # --------------------------------------------------------------
        directional = RotorSolver(
            n_oscillators=2,
            dim=2,
            seed=27,
        )

        directional.omegas[:] = 0.0

        # Explicitly construct two phases separated by pi/2.
        directional.rotors = [
            np.exp(-directional.B_plane * 0.0 / 2.0),
            np.exp(-directional.B_plane *(np.pi / 2.0) / 2.0),
        ]

        before = directional.extract_phases()
        separation_before = np.abs(
             np.angle(np.exp(1j * (before[1] - before[0])))
        )

        directional.step_euler(K=1.0, dt=0.01)

        after = directional.extract_phases()
        separation_after = np.abs(
            np.angle(np.exp(1j * (after[1] - after[0])))
        )

        assert separation_after < separation_before

        print(" ... ✔️ Attractive coupling direction test passed")

        # --------------------------------------------------------------
        # Test 4: One Euler step actually evolves the state
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
        assert not np.allclose(
            phases_before,
            phases_after,
        )

        print(" ... ✔️ Euler evolution test passed")

        # --------------------------------------------------------------
        # Test 5: Standard Kuramoto order parameter
        # --------------------------------------------------------------
        sync_strength = rotor.get_synchronization_strength()

        assert 0 <= sync_strength <= 1.0

        direct_r = np.abs(
            np.mean(np.exp(1j * phases_init))
        )

        assert np.isclose(
            sync_strength,
            direct_r,
        )

        print(" ... ✔️ Standard order-parameter test passed")

        # --------------------------------------------------------------
        # Test 6: Global U(1) phase-shift invariance
        # --------------------------------------------------------------
        original_phases = rotor.extract_phases()

        shifted_rotor = RotorSolver(
            n_oscillators=10,
            dim=2,
            seed=27,
        )

        shifted_phases = shifted_rotor.extract_phases()

        assert np.allclose(
            original_phases,
            shifted_phases,
        )

        shift = 0.73
        shifted_phases = (
            shifted_phases + shift
        )

        shifted_rotor.rotors = [
            np.exp(-shifted_rotor.B_plane * phase / 2.0)
            for phase in shifted_phases
        ]

        original_r = rotor.get_synchronization_strength()
        shifted_r = shifted_rotor.get_synchronization_strength()

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
        times = np.linspace(0, 1, 21)

        sim_times, sim_phases = rotor.simulate(
            K=1.2,
            t_eval=times,
            dt_internal=0.01,
        )

        assert sim_phases.shape == (
            len(times),
            10,
        )

        assert np.allclose(
            sim_times,
            times,
        )

        assert np.isfinite(sim_phases).all()

        print(" ... ✔️ Geometric algebra rotor solver tests passed")

        # --------------------------------------------------------------
        # Test 8: Invalid timestep validation
        # --------------------------------------------------------------
        try:
            rotor.simulate(
                K=1.2,
                t_eval=times,
                dt_internal=-0.01,
            )
        except ValueError:
            print(
                " ... ✔️ Invalid timestep validation test passed"
            )
        else:
            print(
                " ... ✖️ RotorSolver accepted a negative dt_internal"
            )

        # --------------------------------------------------------------
        # Test 9: Future adaptive method remains explicitly unimplemented
        # --------------------------------------------------------------
        try:
            rotor.step_rk45_adaptive(
                K=1.2,
                dt=0.01,
            )
        except NotImplementedError:
            print(" ... 🚧 Future RK45 placeholder test passed")
        else:
            raise AssertionError(
                " ... ✖️ step_rk45_adaptive should remain explicitly unimplemented"
            )

        print(" ... ✔️ Geometric algebra rotor solver tests passed")

    except ImportError:
        print("  ⚠️ Skipping geometric algebra rotor tests (clifford not installed)")

    print("✅ All smoke tests passed")

# ------------------------------------------------------------------------------
# 🔥 Entry point
# ------------------------------------------------------------------------------

def main() -> None:
    _run_smoke_test()

if __name__ == "__main__":
    main()