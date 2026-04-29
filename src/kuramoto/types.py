# kuramoto/types.py
from __future__ import annotations
import numpy as np
from numpy.typing import NDArray
from typing import Dict, Any
from dataclasses import dataclass

AdjacencyMatrix = NDArray[np.floating]
FrequencyArray = NDArray[np.floating]
PhaseArray = NDArray[np.floating]
TimeArray = NDArray[np.floating]
DerivativeArray = NDArray[np.floating]

@dataclass
class KuramotoDataset:
    """
    Container for Kuramoto simulation results.
    
    Matches the output format of the legacy benchmark generator for compatibility.
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
        """Convert to dictionary for JSON serialization or legacy compatibility."""
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
