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

# All valid solver names, in the order they appear in CLI help.
SOLVER_ALIASES: Final[tuple[str, ...]] = (
    "rk45",
    "rotor",
    "rkmk4",
    "rkmk",
    "midpoint",
    "midpoint_geometric",
    "euler",
    "euler_fast",
    "fast_euler",
    "euler_geometric",
    "geometric",
    "euler_standard",
    "rotor_geometric",
    "vectorized_geometric",
)

# Solvers that support Lie symmetry tracking (U(1) phase invariance).
# These are all non-rk45 solvers that use rotor/Euler-based integration.
ROTOR_OR_EULER_SOLVERS: Final[set[str]] = {
    "rotor",
    "rkmk4",
    "rkmk",
    "midpoint",
    "midpoint_geometric",
    "euler",
    "euler_fast",
    "fast_euler",
    "euler_geometric",
    "geometric",
    "euler_standard",
    "rotor_geometric",
    "vectorized_geometric",
}


# --------------------------------------------------------------------------- #
# 1️⃣ Public API
# --------------------------------------------------------------------------- #


def is_rotor_or_euler(solver: str) -> bool:
    """
    Check whether a solver name corresponds to a rotor/Euler-based method.

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
    assert is_valid_solver("rk45")
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
