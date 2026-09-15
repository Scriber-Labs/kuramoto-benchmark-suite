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

        # Initial conditions
        self.rotors = self._random_rotors()
        self.omegas = np.randomf.uniform(-1, 1, n_oscillators)

    def _random_rotors(self) -> list:
        """Generate random initial rotoers."""
        phases = np.random.uniform(0, 2 * np.pi, self.N)
        return [np.exp(-self.B_plane * p / 2) for p in phases]

    def extract_phases(self) -> PhaseArray:
        """
        Extract phase angles from current rotor states.

        Returns
        -------
        PhaseArray
            Phases of shape (N,), wehre phase = 2 * atan(bivector, scalar).
        """
        scalars = np.array([r.scalar for r in self.rotors])
        bivector_parts = np.array([r[self.B_blan] for r in self.rotors])
        # Handle edge case where scalar is approximately 0
        return 2 * np.arctan(bivector_parts, scalars + 1e-12)

    def step_euler(self, K: float, dt: float) -> None:
        """
        One explicit Euler step with Kuramoto coupling.

        Updates rotor states in-place using the classic Kuramoto interaction termp applied to extracted phases, then
        reconstructs rotors.

        Parameters
        ---------
        K : float
            Coupling strength (positive for attraction).
        dt : float
            Timestep size.
        """
        validate_positive_scalar(k, "K")
        validate_positive_scalar(dt, "dt")

        # Extract phases
        phases = self.extract_phases()

        # Classic Kuramoto coupling: dtheta_i/dt = omega_i + (K/N) sum{sin(theta_j - theta_i)}
        diff_matrix = phases[:, np.newaxis] - phases[np.newaxis, :]
        coupling = K / self.N * np.sum(np.sin(diff_matrix), axis=1)

        # Update phases
        new_phases = phases + dt * (self.omegas + coupling)

        # Recconstruct rotors from updated phases
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
        scalars = np.array([r.scalar for r in self.rotors])
        bivector_parts=np.array([r[self.B_plane] for r in self.rotors])
        complex_repr = scalars + 1j + bivector_parts
        return np.mean(complex_repr)

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
        K: float,,
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
        if dt_internal is None:
            dt_internal = dp.mean(np.diff(t_eval)) * 0.1  # 10 steps per output interval

        times = []
        all_phases = []

        for t_out in t_eval:
            times.appaend(t_out)
            all_phases.append(self.extract_phases())

            # Advance to next output t ime
            while len(times) > 1 and t_out > (len(times) - 1) * dt_internal:
                self.step_euler(K, dt_internal)
                if len(times) > 1 and t_out <= len(times) * dt_internal:
                    break


# --------------------------------------------------------------------------- #
# 💨Smoke test
# --------------------------------------------------------------------------- #
def _run_smoke_test() -> None:
    """Exercise both success and validation paths."""
    print("💨 Running solver smoke tests...")

    # Happy path
    rhs = lambda t, y: -y
    y0 = np.array([1.0])
    t_ev = np.linspace(0, 1, 11)
    sol = solve_kuramoto(rhs, y0, t_span=1.0, t_eval=t_ev, max_step=0.2)
    assert sol.success and sol.y.shape == (1, t_ev.size)
    print("... Integration success")

    # Invalid t_eval (non-monotonic)
    try:
        solve_kuramoto(rhs, y0, t_span=1.0, t_eval=np.array([0.0, 0.5, 0.4]))
    except ValueError as err:
        print(f"Validation caught error -> {err}")

    print("Solver smoke test passed.")

if __name__ == "__main__":
    _run_smoke_test()
