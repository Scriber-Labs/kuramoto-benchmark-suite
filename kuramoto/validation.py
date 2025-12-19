# kuramoto/validation.py
from __future__ import annotations
import numpy as np

def validate_positive_scalar(x: float, name: str) -> None:
    """Validate that the input is a positive scalar (strictly > 0)."""
    if not isinstance(x, (int, float)):
        raise TypeError(f"{name} must be a scalar (int or float).")
    if x <= 0:
        raise ValueError(f"{name} must be positive.")

def validate_non_negative_scalar(x: float, name: str) -> None:
    """Validate that the input is a non-negative scalar (>= 0)."""
    if not isinstance(x, (int, float)):
        raise TypeError(f"{name} must be a scalar (int or float).")
    if x < 0:
        raise ValueError(f"{name} must be non-negative.")
    
def validate_intrinsic_frequency_array(omega: np.ndarray, expected_size: int) -> None:
    """Validate that the intrinsic frequency array is one-dimensional and of expected size."""
    if not isinstance(omega, np.ndarray):
        raise TypeError("Intrinsic frequencies must be a numpy array.")
    if omega.shape != (expected_size,):
        raise ValueError(f"Intrinsic frequencies array must have shape ({expected_size},).")

def validate_adjacency(A: np.ndarray, expected_size: int) -> None:
    """Validate that the adjacency matrix is a square matrix of expected size."""
    if not isinstance(A, np.ndarray):
        raise TypeError("Adjacency matrix must be a numpy array.")
    if A.shape != (expected_size, expected_size):
        raise ValueError(f"Adjacency matrix must have shape ({expected_size}, {expected_size}).")
    