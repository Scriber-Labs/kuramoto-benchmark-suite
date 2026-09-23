# src/kuramoto/solvers/rk45.py
"""
Classic RK45 solver wrapper around SciPy's solve_ivp.
 
This module provides the traditional numerical integration path for Kuramoto simulations using adaptive Runge-Kutta
methods with built-in error control.
 
Author: Eigenscribe
Review status: Reviewed and maintained by Eigenscribe
Date created: 05-2026
Last updated: 09-2026
"""

from __future__ import annotations

from typing import Callable, Final, Any

import numpy as np
from numpy.typing import NDArray
from scipy.integrate import solve_ivp

# Import validation utilities
from kuramoto.validation import(
    validate_positive_scalar,
    validate_non_negative_scalar,
    validate_time_axis,
)

__all__: list[str] = ["solve_kuramoto"]

# ---------------------------------------------------------------------------- #
# 🎭 Type Aliases
# ---------------------------------------------------------------------------- #

PhaseArray = NDArray[np.floating]
TimeArray = NDArray[np.floating]

# ---------------------------------------------------------------------------- #
# 🎁 Classic Functional Solver Wrapper
# ---------------------------------------------------------------------------- #

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
        Relative and absolute error tolerances.
    max_step : float, optional
        Upper bound on the internal solver step size. If None, SciPy chooses.

    Returns
    -------
    scipy.integrate.OdeResult
        Standard SciPy result object with fields t, y, success, ...
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
# 💨 Smoke test
# --------------------------------------------------------------------------- #
def _run_smoke_test() -> None:
    """Exercise success, validation, physics, and representation paths."""
    print("💨 Running RK45 solver smoke test...")

    # ==================================================================
    # 🍦 Classic functional solver
    # ==================================================================
    print(" 🍦 Testing solve_kuramoto (SciPy RK45)...")

    # --------------------------------------------------------------
    # Test 1: Basic integration success
    # --------------------------------------------------------------
    rhs = lambda t, y: -y
    y0 = np.array([1.0])
    t_ev = np.linspace(0.0, 1.0, 11)

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

    # --------------------------------------------------------------
    # Test 1: Basic integration success
    # --------------------------------------------------------------
    # For:
    #
    #    dy/dt = -y
    #    y(0) = 1
    #
    # the exact solution is:
    #
    #    y(t) = exp(-t)
    #
    expected = np.exp(-t_ev)

    assert np.allclose(
        sol.y[0],
        expected,
        rtol=1e-5,
        atol=1e-7,
    )

    print(" ... ✔️ Analytical solution test passed")

    # --------------------------------------------------------------
    # Test 3: Time-axis representation
    # --------------------------------------------------------------
    assert np.allclose(
        sol.t,
        t_ev,
    )

    assert sol.t.shape == t_ev.shape

    print(" ... ✔️ Time-axis representation test passed")

    # --------------------------------------------------------------
    # Test 4: Multi-oscillator state representation
    # --------------------------------------------------------------
    omega = np.array([1.0, 2.0, 3.0])

    def oscillator_rhs(t, theta):
        return omega

    y0_multi = np.zeros(3)

    sol_multi = solve_kuramoto(
        oscillator_rhs,
        y0_multi,
        t_span=1.0,
        t_eval=t_ev,
    )

    assert sol_multi.success
    assert sol_multi.y.shape == (
        3,
        t_ev.size,
    )

    # For dtheta_i/dt = omega_i
    #
    #    theta_(i) = omega_i * t
    #
    expected_multi = omega[:, None] * t_ev

    assert np.allclose(
        sol_multi.y,
        expected_multi,
        rtol=1e-5,
        atol=1e-7,
    )

    print(" ... ✔️ Multi-oscillator integration test passed")

    # --------------------------------------------------------------
    # Test 5: Invalid t_eval validation
    # --------------------------------------------------------------
    try:
        solve_kuramoto(
            rhs,
            y0,
            t_span=1.0,
            t_eval=np.array([0.0, 0.5, 0.4])
        )

    except ValueError:
        print(" ... ✔️ Non-monotonic t_eval validation passed")
    else:
        raise AssertionError(
            " ... ❌ solve_kuramoto accepted a non-monotonic t_eval"
        )

    # --------------------------------------------------------------
    # Test 6: Invalid t_span validation
    # --------------------------------------------------------------
    try:
        solve_kuramoto(
            rhs,
            y0,
            t_span=0.0,
            t_eval=t_ev,
        )
    except ValueError:
        print(" ... ✔️ Invalid t_span validation passed")
    else:
        raise AssertionError(
            " ... ❌ solve_kuramoto accepted a non-positive t_span"
        )

    # --------------------------------------------------------------
    # Test 7: Invalid rtol validation
    # --------------------------------------------------------------
    try:
        solve_kuramoto(
            rhs,
            y0,
            t_span=1.0,
            t_eval=t_ev,
            rtol=0.0,
        )
    except ValueError:
        print(" ... ✔️ Invalid rtol validation passed")
    else:
        raise AssertionError(
            " ... ❌ solve_kuramoto accepted a non-positive rtol"
        )

    # --------------------------------------------------------------
    # Test 8: Invalid atol validation
    # --------------------------------------------------------------
    try:
        solve_kuramoto(
            rhs,
            y0,
            t_span=1.0,
            t_eval=t_ev,
            atol=-1.0,
        )
    except ValueError:
        print(" ... ✔️ Invalid atol validation passed")
    else:
        raise AssertionError(
            " ... ❌ solve_kuramoto accepted a negative atol"
        )

    # --------------------------------------------------------------
    # Test 9: Invalid max_step validation
    # --------------------------------------------------------------
    try:
        solve_kuramoto(
            rhs,
            y0,
            t_span=1.0,
            t_eval=t_ev,
            max_step=0.0,
        )
    except ValueError:
        print(" ... ✔️ Invalid max_step validation passed")
    else:
        raise AssertionError(
            " ... ❌ solve_kuramoto accepted a non-positive max_step"
        )

    # --------------------------------------------------------------
    # Test 10: Finite numerical output
    # --------------------------------------------------------------
    assert np.isfinite(sol.t).all()
    assert np.isfinite(sol.y).all()

    print(" ... ✔️ Finite solution output test passed")

    print("✅ All RK45 smoke tests passed")

# ------------------------------------------------------------------------------
# 🔥 Entry point
# ------------------------------------------------------------------------------

def main() -> None:
    _run_smoke_test()

if __name__ == "__main__":
    main()