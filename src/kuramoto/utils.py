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

def compute_order_parameter(phases: np.ndarray) -> np.ndarray | float:
    """
    Compute the Kuramoto order parameter r(t).
    
    Parameters
    ----------
    phases : np.ndarray
        Array of phases. Can be 1D (single time point) or 2D (time series).

    Returns
    -------
    float or np.ndarray
        The order parameter magnitude.
    """
    phases_arr = np.asarray(phases, dtype=np.complex128)
    if phases_arr.ndim == 1:
        return float(np.abs(np.mean(np.exp(1j * phases_arr))))
    elif phases_arr.ndim == 2:
        return np.abs(np.mean(np.exp(1j * phases_arr), axis=1))
    else:
        raise ValueError(f"Phases must be 1D or 2D, got {phases_arr.shape}")
