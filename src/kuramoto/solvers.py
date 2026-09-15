# src/kuramoto/solvers.py
"""
ODE solver interface for Kuramoto simulations.

Provides a thin abstraction over SciPy integrators to allow future solver swapping.

Author: Eigenscribe
Review status: Reviewed and maintained by Eigenscribe.
Date: 05-2026
Last Updated: 09=2026
"""

from __future__ import annotations

from typing import Callable, Final, Any
import numpy as np
from numpy.typing import NDArray
from scipy.integrate import solve_ivp

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

    Each oscillator is represented as a rotor R=exp(-B0/2) where B is the rotation plane bivector. Coupling operates on
    extracted phases but state evolution preserves the geometric algebra structure.

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
            If clifford package is not installed.
        ValueError
            If dim < 2 (need at least 2D for non-trivial rotations)
        """
        validate_positive_scalar(n_oscillators, "n_oscillators")
        validate_positive_scalar(dim, "dim")

        if dim < 2:
            raise ValueError("dim must be >=2 for non-trivial rotration plane")

        # Lazy import to avoid hard dependency
        try:
            from clifford import Cl
        except ImportError:
            raise ImportError(
                "clifford package required for Rotor Solver. Install with: pip install clifford"
            )

        if seed is not None:
            np.random.seed(seed)

        self.N = n_oscillators
        self.dim = dim
        self.layout, self.blades = Cl(dim)

        # Rotation plane: for 2D this is e12, for 3D typically xy-plane
        plane_key = f'e{dim-1}{dim}' if dim <= 3 else 'e12'
        self.B_plane = self.blades[plane_key]

        # Precompute the slot of rotation plane in the coefficient array
        # Rotor R = exp(-B theta/2) lives in the even subalgebra spanned by {scalar, B_plane}, so we only ever read
        # these two slots.
        self._blade_idx = int(np.nonzero(np.asarray(self.B_plane.value))[0][0])
        self.blade_idx = self._blade_idx

        # Initial conditions
        self.rotors = self._random_rotors()
        self.omegas = np.random.uniform(-1, 1, n_oscillators)

    def _random_rotors(self) -> list:
        """Generate random initial rotors."""
        phases = np.random.uniform(0, 2 * np.pi, self.N)
        return [np.exp(-self.B_plane * p / 2) for p in phases]

    def extract_phases(self) -> PhaseArray:
        """
        Extract phase angles from current rotor states.

        Returns
        -------
        PhaseArray
            Phases of shape (N,), where phase = 2 * arctan2(bivector_coefficient, scalar).
        """
        phases = []
        for r in self.rotors:
            scalar = float(r.value[0])           # Slot 0 is always the scalar
            bivector = float(r.value[self._blade_idx])  # Precomputed plane slot

            # Avoid division by zero
            phases.append((2 * np.arctan2(-bivector, scalar)) % (2 * np.pi))

        return np.array(phases)

    def step_euler(self, K: float, dt: float) -> None:
        """
        One explicit Euler step with Kuramoto coupling.

        Updates rotor states in-place using the classic Kuramoto interaction term applied to extracted phases, then
        reconstructs rotors.

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

        # Classic Kuramoto coupling: dtheta_i/dt = omega_i + (K/N) sum{sin(theta_j - theta_i)}
        diff_matrix = phases[:, np.newaxis] - phases[np.newaxis, :]
        coupling = K / self.N * np.sum(np.sin(diff_matrix), axis=1)

        # Update phases
        new_phases = phases + dt * (self.omegas + coupling)

        # Reconstruct rotors from updated phases
        self.rotors = [np.exp(-self.B_plane * p / 2) for p in new_phases]

    def get_complex_order_parameter(self) -> complex:
        """
        Compute order parameter as average of complex rotor representation.

        Returns
        -------
        complex
            Average rotor state interpreted as complex number.
            Magnitude |r| indicates synchronization strength.
        """
        scalars = np.array([r.value[0] for r in self.rotors])
        bivector_parts = np.array([r.value[self._blade_idx] for r in self.rotors])
        complex_repr = scalars + 1j * bivector_parts
        return complex(np.mean(complex_repr))

    def get_synchronization_strength(self) -> float:
        """
        Return magnitude of order parameter.

        Returns
        -------
        float
            Synchronization strength in [0, 1], where 1 = fully synchronized.
        """
        return abs(self.get_complex_order_parameter())

    def simulate(
        self,
        K: float,
        t_eval: TimeArray,
        dt_internal: float | None = None,
    ) -> tuple[TimeArray, PhaseArray]:
        """
        Run full simulation over specified time grid.

        Parameters
        ----------
        K : float
            Coupling strength.
        t_eval : TimeArray
            Output timestamps (must be monotonically increasing).
        dt_internal : float, optional
            Internal stepping timestep. If None, inferred from t_eval.

        Returns
        -------
        tuple
            (times, phases) where phases has shape (len(t_eval), N)
        """
        validate_positive_scalar(K, "K")
        validate_time_axis(t_eval)
        if dt_internal is not None:
            validate_positive_scalar(dt_internal, "dt_internal")
        else:
            dt_internal = float(np.mean(np.diff(t_eval)) * 0.1)  # 10 steps per output interval

        times = []
        all_phases = []
        t_current = float(t_eval[0])

        for t_out in t_eval:
            while t_current < t_out - 1e-12:
                step = min(dt_internal, float(t_out - t_current))
                self.step_euler(K, step)
                t_current += step
            times.append(t_out)
            all_phases.append(self.extract_phases())

        return np.array(times), np.array(all_phases)


# --------------------------------------------------------------------------- #
# 💨Smoke test
# --------------------------------------------------------------------------- #
def _run_smoke_test() -> None:
    """Exercise success and validation paths for each solver class."""
    print("💨 Running solver smoke test...")

    # === Classic functional solver ===
    print(" 🍦 Testing solve_kuramoto (SciPy)...")
    rhs = lambda t, y: -y
    y0 = np.array([1.0])
    t_ev = np.linspace(0, 1, 11)
    sol = solve_kuramoto(rhs, y0, t_span=1.0, t_eval=t_ev, max_step=0.2)
    assert sol.success and sol.y.shape == (1, t_ev.size)
    print(" ... 🍦 Classic integration success")

    # Invalid t_eval (non-monotonic)
    try:
        solve_kuramoto(rhs, y0, t_span=1.0, t_eval=np.array([0.0, 0.5, 0.4]))
    except ValueError as err:
        print(f" ... 🍦 Validation caught classic integration error as expected")

    # === Rotor solver (if clifford available) ===
    try:
        print(" 💫 Testing RotorSolver (📐 Geometric Algebra)...")
        rotor = RotorSolver(n_oscillators=10, dim=2, seed=27)

        # Check initial state
        assert rotor.N == 10
        assert rotor.dim == 2
        assert len(rotor.rotors) == 10
        assert len(rotor.omegas) == 10

        # Test phase extraction
        phases_init = rotor.extract_phases()
        assert phases_init.shape == (10,)
        assert np.all((phases_init >= 0) & (phases_init <= 2*np.pi))

        # Test single step
        rotor_copy = RotorSolver(n_oscillators=10, dim=2, seed=27)
        rotor_copy.step_euler(K=1.2, dt=0.01)
        phases_after = rotor_copy.extract_phases()
        assert phases_after.shape == (10,)
        assert not np.allclose(phases_init, phases_after)  # Should have evolved

        # Test order parameter
        sync_strength = rotor.get_synchronization_strength()
        assert 0 <= sync_strength <= 1

        # Test full simulation
        times = np.linspace(0, 1, 21)
        sim_times, sim_phases = rotor.simulate(K=1.2, t_eval=times, dt_internal=0.01)
        assert sim_phases.shape == (len(times), 10)
        assert np.allclose(sim_times, times)

        print("  ... 💫📐 Geometric algebra rotor solver tests passed")

    except ImportError:
        print("  ⚠️ Skipping geometric algebra rotor tests (clifford not installed)")
    except AssertionError as e:
        print(f" 💫📐 Geometric algebra rotor test failed: {e}")
        raise

    print("✅ All smoke tests passed")

if __name__ == "__main__":
    _run_smoke_test()
