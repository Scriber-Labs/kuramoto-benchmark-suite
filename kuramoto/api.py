# kuramoto/api.py
from __future__ import annotations

import numpy as np
from typing import Dict, Optional

from .validation import (
    validate_positive_scalar,
    validate_intrinsic_frequency_array,
    validate_adjacency,
)
from .graphs import build_adjacency, graph_stats 
from .integrators import euler_step 
from .utils import wrap_phase, make_rng 

__all__ = ["generate_kuramoto_dataset"]

def generate_kuramoto_dataset(
    n_oscillators: int,
    natural_frequencies: np.ndarray,
    coupling: float,
    timesteps: int,
    dt: float,
    adjacency: Optional[np.ndarray] = None,
    noise_std: float = 0.0,
    seed: Optional[int] = None,
) -> Dict[str, np.ndarray]:
    """
    Generate a synthetic phase time series dataset using the Kuramoto model.
    
    Parameters
    ----------
    n_oscillators : int
        Number of oscillators (N).
    natural_frequencies : np.ndarray, shape (N,)
        Intrinsic frequencies of the oscillators (omega_i).
    coupling : float
        Global coupling strength (K).
    timesteps : int
        Number of time steps (T).
    dt : float
        Integration time step.
    adjacency : np.ndarray, shape (N, N), optional
        Adjacency matrix defining the network topology for the system of oscillators. If None, a fully connected graph is used.
    noise_std : float, default = 0.0
        Standard deviation of additive phase noise.
    seed : int, optional
        Random seed for deterministic results. If None, a random seed is used.
    
    Returns
    -------
    dict[str, np.ndarray]
        A dictionary containing:
            - 'phases': Array of shape (T, N) with the phase time series.
            - 'derivatives': Array of shape (T, N) with the phase derivatives.
            - 'frequencies': Array of shape (N,) with the intrinsic frequencies.
            - Metadata about the simulation parameters.
            - Metadata about the graph structure. 

    Raises
    ------
    ValueError
        If inputs are invalid or inconsistent.
    """
    # Validate inputs
    validate_positive_scalar(coupling, "coupling")
    validate_positive_scalar(dt, "dt")
    validate_positive_scalar(timesteps, "timesteps")
    validate_positive_scalar(noise_std, "noise_std")
    validate_intrinsic_frequency_array(natural_frequencies, n_oscillators)

    rng = make_rng(seed)

    A = build_adjacency(n_oscillators, adjacency)
    validate_adjacency(A, n_oscillators)

    # Initialize phase and derivative arrays

    theta = np.zeros((timesteps, n_oscillators), dtype=float)
    dtheta = np.zeros_like(theta)

    # Set initial phases randomly
    theta[0] = rng.uniform(0.0, 2 * np.pi, size=n_oscillators)

    # Compute phase derivatives and update phases
    for t in range(timesteps - 1):
        # Compute phase derivatives
        dtheta[t] = natural_frequencies + (
            coupling / n_oscillators
        ) * np.sum(np.sin(theta[t] - theta[t][:,None]), axis=1)
        
        # Add noise to the derivatives
        if noise_std > 0.0:
            dtheta[t] += rng.normal(0.0, noise_std, size=n_oscillators)

        # Update phases using Euler's method
        theta[t+1] = wrap_phase(euler_step(theta[t], dtheta[t], dt))
    
    time = dt * np.arange(timesteps)

    # Prepare the output dictionary
    return {
        "omega": natural_frequencies.copy(),
        "theta": theta,
        "dtheta": dtheta,
        "time": time,
        "initial_conditions": theta[0].copy(),
        "coupling": coupling,
        "adjacency": A.copy(),
        "graph_stats": graph_stats(A),
        "freq_pdf": "user-specified",
        "phase_pdf": "uniform [0, 2*pi)",
        "noise_std": noise_std
    }


