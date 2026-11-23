"""
kuramoto.validation

Input validation utilities for Kuramoto simulation parameters.
Provides scalar, array, and adjacency matrix validators.

Author: Eigenscribe
Date: November 2026
"""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray

# -----------------------------------------------------------------------------------------------------------
# 🎭 Typing helpers / protocols / constants
# -----------------------------------------------------------------------------------------------------------

PhaseArray = NDArray[np.floating]
"""Type alias for phase arrays."""

TimeArray = NDArray[np.floating]
"""Type alias for time axis arrays."""

__all__: list[str] = [
    "validate_positive_scalar",
    "validate_non_negative_scalar",
    "validate_intrinsic_frequency_array",
    "validate_adjacency",
    "validate_time_axis",
]


# -----------------------------------------------------------------------------------------------------------
# 1️⃣ Core definitions
# -----------------------------------------------------------------------------------------------------------


def validate_positive_scalar(x: float, name: str) -> None:
    """
    Validate that the input is a positive scalar (strictly > 0).

    Parameters
    ----------
    x : float
        Value to validate.
    name : str
        Human-readable name of the parameter (used in error messages).

    Raises
    ------
    TypeError
        If ``x`` is not an int or float.
    ValueError
        If ``x`` is not strictly positive.
    """
    if not isinstance(x, (int, float)):
        raise TypeError(f"Error: {name} must be a scalar (int or float).")
    if x <= 0:
        raise ValueError(f"Error: {name} must be positive.")


def validate_non_negative_scalar(x: float, name: str) -> None:
    """
    Validate that the input is a non-negative scalar (>= 0).

    Parameters
    ----------
    x : float
        Value to validate.
    name : str
        Human-readable name of the parameter (used in error messages).

    Raises
    ------
    TypeError
        If ``x`` is not an int or float.
    ValueError
        If ``x`` is negative.
    """
    if not isinstance(x, (int, float)):
        raise TypeError(f"Error: {name} must be a scalar (int or float).")
    if x < 0:
        raise ValueError(f"Error: {name} must be non-negative.")


def validate_intrinsic_frequency_array(
    omega: NDArray[np.floating], expected_size: int
) -> None:
    """
    Validate that the intrinsic frequency array is one-dimensional and of expected size.

    Parameters
    ----------
    omega : NDArray[np.floating]
        Intrinsic frequency array.
    expected_size : int
        Expected number of oscillators.

    Raises
    ------
    TypeError
        If ``omega`` is not a NumPy array.
    ValueError
        If ``omega`` shape does not match ``(expected_size,)``.
    """
    if not isinstance(omega, np.ndarray):
        raise TypeError("Error: Intrinsic frequencies must be a numpy array.")
    if omega.shape != (expected_size,):
        raise ValueError(
            f"Error: Intrinsic frequencies array must have shape ({expected_size},)."
        )


def validate_adjacency(A: NDArray[np.floating], expected_size: int) -> None:
    """
    Validate that the adjacency matrix is a square matrix of expected size and symmetric.

    Parameters
    ----------
    A : NDArray[np.floating]
        Adjacency matrix.
    expected_size : int
        Expected number of nodes.

    Raises
    ------
    TypeError
        If ``A`` is not a NumPy array.
    ValueError
        If ``A`` shape does not match ``(expected_size, expected_size)`` or is not symmetric.
    """
    if not isinstance(A, np.ndarray):
        raise TypeError("Error: Adjacency matrix must be a numpy array.")
    if A.shape != (expected_size, expected_size):
        raise ValueError(
            f"Error: Adjacency matrix must have shape ({expected_size}, {expected_size})."
        )
    if not np.allclose(A, A.T):
        raise ValueError(
            "Error: Adjacency matrix must be symmetric for undirected graphs."
        )


def validate_time_axis(t: TimeArray) -> None:
    """
    Validate that the time axis is a 1-D strictly increasing array.

    Parameters
    ----------
    t : TimeArray
        Time axis array.

    Raises
    ------
    ValueError
        If ``t`` is not 1-D, empty, or not strictly increasing.
    """
    if t.ndim != 1 or t.size == 0 or not np.all(np.diff(t) > 0):
        raise ValueError("Error: t_eval must be a 1-D strictly increasing array")


# -----------------------------------------------------------------------------------------------------------
# 💨 Smoke tests
# -----------------------------------------------------------------------------------------------------------


def _run_smoke_test() -> None:
    """Quick sanity check for validation functions."""
    # Positive scalar
    validate_positive_scalar(1.0, "test")
    try:
        validate_positive_scalar(0.0, "test")
        raise AssertionError("Should have raised ValueError")
    except ValueError:
        pass

    # Non-negative scalar
    validate_non_negative_scalar(0.0, "test")
    validate_non_negative_scalar(1.0, "test")
    try:
        validate_non_negative_scalar(-1.0, "test")
        raise AssertionError("Should have raised ValueError")
    except ValueError:
        pass

    # Frequency array
    omega = np.array([1.0, 2.0, 3.0])
    validate_intrinsic_frequency_array(omega, 3)
    try:
        validate_intrinsic_frequency_array(omega, 4)
        raise AssertionError("Should have raised ValueError")
    except ValueError:
        pass

    # Adjacency matrix
    A = np.array([[0, 1], [1, 0]], dtype=float)
    validate_adjacency(A, 2)
    try:
        validate_adjacency(A, 3)
        raise AssertionError("Should have raised ValueError")
    except ValueError:
        pass

    # Time axis
    t = np.linspace(0, 1, 10)
    validate_time_axis(t)
    try:
        validate_time_axis(np.array([]))
        raise AssertionError("Should have raised ValueError")
    except ValueError:
        pass

    print("✅ Validation smoke test passed.")


# -----------------------------------------------------------------------------------------------------------
# 🔥 Entry point
# -----------------------------------------------------------------------------------------------------------


def main() -> None:
    """Entry point for module-level smoke testing."""
    _run_smoke_test()


if __name__ == "__main__":
    main()
