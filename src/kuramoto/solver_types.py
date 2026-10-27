# kuramoto/solver_types.py
"""
Canonical solver type definitions and aliases.

Provides a single source of truth for all solver method names used across
the Kuramoto codebase, eliminating duplication in model.py, api.py,
cli/commands.py, and solvers/rotor.py.

Author: Eigenscribe
Date: October 2026
"""

from __future__ import annotations

from typing import Final

# --------------------------------------------------------------------------- #
# 0️⃣ Constants & Types
# --------------------------------------------------------------------------- #

# Classic Scipy ODE integrators
ODE_SOLVERS: Final[tuple[str, ...]] = ("rk45",)

# Clifford Geometric Algebra Rotor solvers
ROTOR_SOLVER_ALIASES: Final[tuple[str, ...]] = (
    "rotor",
    "rkmk4",
    "rkmk",
    "rk4",
    "geometric_rk4",
    "dopri54",
    "dopri",
    "adaptive_dopri54",
    "midpoint",
    "midpoint_geometric",
    "euler_midpoint",
    "euler",
    "euler_fast",
    "fast_euler",
    "fast",
    "euler_geometric",
    "geometric",
    "euler_standard",
    "standard",
    "rotor_geometric",
    "vectorized_geometric",
    "predictor_corrector",
    "pc",
    "adaptive",
    "adaptive_embedded",
    "embedded",
)

# Quantum SCF Rotor solvers
QUANTUM_SOLVER_ALIASES: Final[tuple[str, ...]] = (
    "quantum",
    "quantum_rotor",
    "quantum_scf",
    "quantum_statevector",
    "quantum_expectation",
    "quantum_shot_sampling",
    "statevector",
    "expectation",
    "shot_sampling",
)

# All valid solver names, in the order they appear in CLI help.
SOLVER_ALIASES: Final[tuple[str, ...]] = (
    *ODE_SOLVERS,
    *ROTOR_SOLVER_ALIASES,
    *QUANTUM_SOLVER_ALIASES,
)

# Solvers that use rotor/Clifford-based integration.
ROTOR_SOLVERS: Final[set[str]] = set(ROTOR_SOLVER_ALIASES)

# Solvers that use quantum SCF parallel R_Z gates.
QUANTUM_SOLVERS: Final[set[str]] = set(QUANTUM_SOLVER_ALIASES)

# Solvers that support Lie symmetry tracking (U(1) phase invariance).
# This includes both classical GA rotor / Euler methods and quantum SCF methods.
ROTOR_OR_EULER_SOLVERS: Final[set[str]] = ROTOR_SOLVERS | QUANTUM_SOLVERS


# --------------------------------------------------------------------------- #
# 1️⃣ Public API
# --------------------------------------------------------------------------- #


def is_rotor_solver(solver: str) -> bool:
    """
    Check whether a solver name corresponds to a Geometric Algebra rotor method.

    Parameters
    ----------
    solver : str
        Solver name (case-insensitive).

    Returns
    -------
    bool
        True if the solver uses Clifford GA rotor representations.
    """
    return solver.lower() in ROTOR_SOLVERS


def is_quantum_solver(solver: str) -> bool:
    """
    Check whether a solver name corresponds to a Quantum SCF method.

    Parameters
    ----------
    solver : str
        Solver name (case-insensitive).

    Returns
    -------
    bool
        True if the solver uses Quantum SCF execution.
    """
    return solver.lower() in QUANTUM_SOLVERS


def is_rotor_or_euler(solver: str) -> bool:
    """
    Check whether a solver name corresponds to a rotor, Euler, or quantum method.

    Parameters
    ----------
    solver : str
        Solver name (case-insensitive).

    Returns
    -------
    bool
        True if the solver supports Lie symmetry tracking.
    """
    return solver.lower() in ROTOR_OR_EULER_SOLVERS


def is_valid_solver(solver: str) -> bool:
    """
    Check whether a solver name is valid.

    Parameters
    ----------
    solver : str
        Solver name (case-insensitive).

    Returns
    -------
    bool
        True if the solver name is recognized.
    """
    return solver.lower() in {s.lower() for s in SOLVER_ALIASES}


# --------------------------------------------------------------------------- #
# 💨 Smoke Test
# --------------------------------------------------------------------------- #


def _run_smoke_test() -> None:
    """Verify solver type constants are consistent."""
    print("💨 Running solver_types smoke test...")

    # All rotor/euler solvers should be in the main alias list
    for s in ROTOR_OR_EULER_SOLVERS:
        assert s in SOLVER_ALIASES, f"{s} missing from SOLVER_ALIASES"

    # rk45 should NOT be rotor/euler
    assert not is_rotor_or_euler("rk45")
    assert is_rotor_or_euler("euler")
    assert is_rotor_or_euler("quantum")
    assert is_quantum_solver("quantum_rotor")
    assert is_quantum_solver("shot_sampling")
    assert is_rotor_solver("rkmk4")
    assert is_rotor_solver("dopri54")
    assert is_valid_solver("rk45")
    assert is_valid_solver("quantum_scf")
    assert is_valid_solver("dopri54")
    assert not is_valid_solver("bogus_solver")

    print("✅ solver_types smoke test passed.")


# --------------------------------------------------------------------------- #
# 🔥 Entry point
# --------------------------------------------------------------------------- #


def main() -> None:
    """Entry point for standalone execution."""
    _run_smoke_test()


if __name__ == "__main__":
    main()
