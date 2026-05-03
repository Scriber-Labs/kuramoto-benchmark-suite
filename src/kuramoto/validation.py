# kuramoto/validation.py
from __future__ import annotations
import numpy as np
from numpy.typing import NDArray

PhaseArray = NDArray[np.floating]
TimeArray = NDArray[np.floating]

__all__: list[str] = [
    "validate_positive_scalar",
    "validate_non_negative_scalar",
    "validate_intrinsic_frequency_array",
    "validate_adjacency",
    "validate_time_axis",
]

def validate_positive_scalar(x: float, name: str) -> None:
    """Validate that the input is a positive scalar (strictly > 0)."""
    if not isinstance(x, (int, float)):
        raise TypeError(f"Error: {name} must be a scalar (int or float).")
    if x <= 0:
        raise ValueError(f"Error: {name} must be positive.")


def validate_non_negative_scalar(x: float, name: str) -> None:
    """Validate that the input is a non-negative scalar (>= 0)."""
    if not isinstance(x, (int, float)):
        raise TypeError(f"Error: {name} must be a scalar (int or float).")
    if x < 0:
        raise ValueError(f"Error: {name} must be non-negative.")


def validate_intrinsic_frequency_array(omega: np.ndarray, expected_size: int) -> None:
    """Validate that the intrinsic frequency array is one-dimensional and of expected size."""
    if not isinstance(omega, np.ndarray):
        raise TypeError("Error: Intrinsic frequencies must be a numpy array.")
    if omega.shape != (expected_size,):
        raise ValueError(f"Error: Intrinsic frequencies array must have shape ({expected_size},).")

def validate_adjacency(A: np.ndarray, expected_size: int) -> None:
    """Validate that the adjacency matrix is a square matrix of expected size and symmetric."""
    if not isinstance(A, np.ndarray):
        raise TypeError("Error: Adjacency matrix must be a numpy array.")
    if A.shape != (expected_size, expected_size):
        raise ValueError(f"Error: Adjacency matrix must have shape ({expected_size}, {expected_size}).")
    if not np.allclose(A, A.T):
        raise ValueError("Error: Adjacency matrix must be symmetric for undirected graphs.")

def validate_time_axis(t: TimeArray) -> None:
    if t.ndim != 1 or t.size == 0 or not np.all(np.diff(t) >0):
        raise ValueError("Error: t_eval must be a 1-D strictly increasing array")