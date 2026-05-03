# src/kuramoto/dataset.py
"""
Data container for Kuramoto simulation results.

This module defines the `KuramotoDataset` dataclass, which serves as the immutable (conceptually) return type for simulation runs. It ensures type safety and consistency across the benchmark suite.

Author: Eigenscribe
Development note: LLM assistance was used during construction; implementation has been reviewed and adapted for this project.
Reveiw status: REviewed and maintained by Eigenscribe.
Date: 05-2026
"""

from __future__ import annotations

from typing import Final, Dict, Any
from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray

__all__: list[str] = [
    "KuramotoDataset",
]

# ------------------------------------------------------------------------------
# 0️⃣ Type Aliases
# ------------------------------------------------------------------------------
FrequencyArray = NDArray[np.floating]
PhaseArray = NDArray[np.floating]
DerivativeArray = NDArray[np.floating]
TimeArray = NDArray[np.floating]
AdjacencyMatrix = NDArray[np.floating]

@dataclass
class KuramotoDataset:
    """
    Container for Kuramoto simulation results.

    Matches the output format of the legacy benchmark generator for compatibility. This dataclass aggregates all physical quantities and metadata required to reproduce or analyze a specific simulation run.

    Attributes
    ----------
    omega : FrequencyArray
        Natural frequencies of the oscillators (shape: (N,)).
    theta : PhaseArray
        Phase trajectories over time (shape: (T, N)).
    dtheta : DerivativeArray
        Time derivatives of phases (shape: (T, N)).
    time : TimeArray
        Time points corresponding to the phase trajectories (shape: (T,)).
    initial_conditions : PhaseArray
        Initial phase configuration (shape: (N,)).
    coupling : float
        Global coupling strength K.
    adjacency : AdjacencyMatrix
        Network topology adjacency matrix (shape: (N, N)).
    network_stats : Dict[str, Any]
        Computed graph metrics (e.g., degree, density).
    noise_std : float
        Standard deviation of additive Gaussian noise.
    freq_pdf : str
        Identifier for the natural frequency distributions (e.g., "lorentzian").
    phase_pdf : str
        Identifier for the initial phase distribution (e.g., "uniform").
    """

    omega: FrequencyArray
    theta: PhaseArray
    dtheta: DerivativeArray
    time: TimeArray
    initial_conditions: PhaseArray
    coupling: float
    adjacency: AdjacencyMatrix
    network_stats: Dict[str, Any]
    noise_std: float
    freq_pdf: str
    phase_pdf: str

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the dataset to a dictionary for JSON serialization or legacy compatibility.

        Returns
        -------
        dict[str, Any]
            Dictionary containing all attributes as keys.
        """

        return {
            "omega": self.omega,
            "theta": self.theta,
            "dtheta": self.dtheta,
            "time": self.time,
            "initial_conditions": self.initial_conditions,
            "coupling": self.coupling,
            "adjacency": self.adjacency,
            "network_stats": self.network_stats,
            "noise_std": self.noise_std,
            "freq_pdf": self.freq_pdf,
            "phase_pdf": self.phase_pdf,
        }