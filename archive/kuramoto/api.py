# kuramoto/api.py
from __future__ import annotations

import numpy as np
from typing import Dict, Optional

from .validation import (
    validate_positive_scalar,
    validate_non_negative_scalar,
    validate_intrinsic_frequency_array,
    validate_adjacency,
)
from .graphs import build_adjacency
from .model import KuramotoModel
from .utils import make_rng

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
            - 'theta': Array of shape (T, N) with the phase time series.
            - 'dtheta': Array of shape (T, N) with the phase derivatives.
            - 'omega': Array of shape (N,) with the intrinsic frequencies.
            - 'time': Array of shape (T,) with the time points.
            - 'initial_conditions': Array of shape (N,) with the starting phases.
            - 'coupling': The global coupling strength (K).
            - 'adjacency': The (N, N) adjacency matrix.
            - 'graph_stats': Dictionary with network statistics.
            - 'noise_std': Standard deviation of the noise.
            - 'freq_pdf': Description of the frequency distribution.
            - 'phase_pdf': Description of the initial phase distribution.
            - 'phases', 't', 'natural_frequencies', 'derivatives': Aliases for 'theta', 'time', 'omega', 'dtheta' for legacy compatibility.

    Raises
    ------
    ValueError
        If inputs are invalid or inconsistent.
    """
    # Validate inputs
    validate_positive_scalar(coupling, "coupling")
    validate_positive_scalar(dt, "dt")
    validate_positive_scalar(timesteps, "timesteps")
    validate_non_negative_scalar(noise_std, "noise_std")
    validate_intrinsic_frequency_array(natural_frequencies, n_oscillators)

    A = build_adjacency(n_oscillators, adjacency)
    validate_adjacency(A, n_oscillators)

    model = KuramotoModel(
        n_oscillators=n_oscillators,
        natural_frequencies=natural_frequencies,
        adjacency_matrix=A,
        coupling_strength=coupling,
        noise_std=noise_std,
        random_seed=seed,
    )

    # Use RK45 integration with the provided dt to estimate t_span
    # We want exactly 'timesteps' points to maintain compatibility
    t_span = (timesteps - 1) * dt
    dataset = model.simulate(
        t_span=t_span,
        min_time_points=timesteps,
        max_time_points=timesteps
    )

    # Prepare the output dictionary (preserving legacy format)
    res = dataset.to_dict()
    # Rename network_stats to graph_stats and ensure legacy keys are present if needed
    # but the legacy graph_stats had num_edges, density, is_connected.
    # Actually, let's just recompute it using the existing graph_stats function to be safe.
    from .graphs import graph_stats
    res["graph_stats"] = graph_stats(A)
    
    # Ensure keys match exactly what was there before
    # Legacy: omega, theta, dtheta, time, initial_conditions, coupling, adjacency, graph_stats, freq_pdf, phase_pdf, noise_std
    # Dataset to_dict: omega, theta, dtheta, time, initial_conditions, coupling, adjacency, network_stats, noise_std, freq_pdf, phase_pdf
    
    # dataset.to_dict() already has most of them.
    if "network_stats" in res:
        del res["network_stats"]
    
    # Add legacy keys for backward compatibility with notebooks/scripts
    res["phases"] = res["theta"]
    res["t"] = res["time"]
    res["natural_frequencies"] = res["omega"]
    res["derivatives"] = res["dtheta"]

    return res


