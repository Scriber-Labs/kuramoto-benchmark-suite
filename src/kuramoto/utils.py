# kuramoto/utils.py
from __future__ import annotations
import numpy as np

def wrap_phase(theta: np.ndarray) -> np.ndarray:
    """
    Wrap phase angles to the interval [0, 2*pi).
    
    Parameters
    ----------
    theta : np.ndarray
        Array of phase angles in radians.

    Returns
    -------
    np.ndarray
        Array of phase angles wrapped to [0, 2*pi).
    """
    return np.mod(theta, 2 * np.pi)

def make_rng(seed: int | None) -> np.random.Generator:
    """
    Create a numpy random number generator with a given seed.
    
    Parameters
    ----------
    seed : int | None
        Seed for the random number generator. If None, a random seed is used.
    
    Returns
    -------
    np.random.Generator
        A numpy ranom number generator instance.
    """
    return np.random.default_rng(seed)
