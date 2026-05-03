# src/kuramoto/solvers.py
"""
ODE solver interface for Kuramoto simulations.

Provides a thin abstraction over SciPy integrators to allow future solver swapping.

Author: Eigenscribe
Development note: LLM assistance was used during construction; implementation has been reviewed and adapted for this project.
Review status: Reviewed and maintained by Eigenscribe.
Date: 05-2026
"""

from __future__ import annotations

from typing import Callable, Final, Any

import numpy as np
from numpy.typing import NDArray
from scipy.integrate import solve_ivp

from validation import validate_positive_scalar, validate_non_negative_scalar, validate_intrinsic_frequency_array, validate_adjacency, validate_time_axis

__all__: list[str] = [
    "solve_kuramoto",
]

# ------------------------------------------------------------------------------
# 0️⃣ Type Aliases
# ------------------------------------------------------------------------------
PhaseArray = NDArray[np.floating]
TimeArray = NDArray[np.floating]

# ------------------------------------------------------------------------------
# 2️⃣ Solver Wrapper
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

# --------------------------------------------------------------------------- #
# 3️⃣ Smoke test
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
