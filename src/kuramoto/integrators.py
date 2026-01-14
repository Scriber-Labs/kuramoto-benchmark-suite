# kuramoto/integrators.py
from __future__ import annotations
import numpy as np

def euler_step(theta: np.ndarray, dtheta: np.ndarray, dt: float) -> np.ndarray:
    """
    Perform a single Euler integration step for phase variables.
    
    Parameters
    ----------
    theta : np.ndarray
        Current state of the system (phases).
    dtheta : np.ndarray
        Derivative of the state (phase velocities).
    dt : float
        Time step for the integration.
    
    Returns 
    -------
    np.ndarray
        Updated state of the system after one Euler step.
    """
    return theta + dtheta * dt
