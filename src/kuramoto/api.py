# src/kuramoto/api.py
"""
Public API for Kuramoto dataset generation.

Provides a stable interface for generating benchmark datasets while abstracting internal model implementation details.

Author: Eigenscribe
Development note: Initial LLM scaffolding; implementation has been reviewed and adapted for this project.
Review status: Reviewed and maintained by Eigenscribe.
Date: May 2026
"""

from __future__ import annotations

# --------------------------------------------------------------------------- #
# Imports & type aliases
# --------------------------------------------------------------------------- #

from typing import Optional, Final, Dict, Any
import numpy as np
from numpy.typing import NDArray

from .model import KuramotoModel
from .topologies import load_topology

__all__: list[str] = [
    "generate_kuramoto_dataset",
]

# ------------------------------------------------------------------------------ #
# 0️⃣ Type Aliases
# ------------------------------------------------------------------------------ #
FrequencyArray = NDArray[np.floating]
AdjacencyMatrix = NDArray[np.floating]

# ------------------------------------------------------------------------------ #
# 1️⃣ Public API
# ------------------------------------------------------------------------------ #
def generate_kuramoto_dataset(
    n_oscillators: int,
    natural_frequencies: FrequencyArray,
    coupling: float,
    timesteps: int,
    dt: float,
    adjacency: Optional[AdjacencyMatrix] = None,
    topology: Optional[str] = None,
    topology_kwargs: Optional[Dict[str, Any]] = None,
    noise_std: float = 0.0,
    seed: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Generate Kuramoto dataset.

    Parameters
    ----------
    n_oscillators : int
        Number of oscillators.
    natural_frequencies : FrequencyArray
        Intrinsic frequencies.
    coupling : float
        Coupling strength.
    timesteps : int
        Number of timesteps.
    dt : float
        Time step size.
    adjacency : AdjacencyMatrix, optional
        Network structure (adjacency matrix). If both `adjacency` and `topology` 
        are None, a complete graph is used.
    topology : str, optional
        Name of a predefined topology (e.g., 'ring', 'small_world'). 
        Overrides `adjacency` if provided.
    topology_kwargs : Dict[str, Any], optional
        Arguments passed to the topology generator (e.g., {'k': 4, 'p': 0.1}).
    noise_std : float
        Noise level.
    seed : int, optional
        Random seed.

    Returns
    -------
    Dict[str, Any]
        Dataset dictionary.
    """
    t_span = timesteps * dt
    
    # Resolve topology if requested
    adj_matrix = adjacency
    if topology is not None:
        kwargs = topology_kwargs or {}
        if "n" not in kwargs:
            kwargs["n"] = n_oscillators
        adj_matrix = load_topology(topology, **kwargs)

    model = KuramotoModel(
        n_oscillators=n_oscillators,
        natural_frequencies=natural_frequencies,
        adjacency_matrix=adj_matrix,
        coupling_strength=coupling,
        noise_std=noise_std,
        random_seed=seed,
    )

    dataset = model.simulate(t_span=t_span, n_points=timesteps)

    return dataset.to_dict()

# ------------------------------------------------------------------------------ #
# 2️⃣ Smoke Test
# ------------------------------------------------------------------------------ #

def _run_smoke_test() -> None:
    """
    Run sanity checks for API.

    Verifies:
    - Dataset generation succeeds
    - Output structure is correct
    """
    print("💨 Running API smoke test...")

    num_oscillators = 5

    omega = np.ones(num_oscillators)

    data = generate_kuramoto_dataset(
        n_oscillators=num_oscillators,
        natural_frequencies=omega,
        coupling=1.0,
        timesteps=100,
        dt=0.01,
        seed=1,
    )

    assert "theta" in data
    assert data["theta"].shape[1] == num_oscillators

    print("✔️ API test passed")
    print("\n✅ API smoke test passed.")

def main() -> None:
    """
    Entry point for standalone execution.

    Runs smoke tests.
    """
    _run_smoke_test()

if __name__ == "__main__":
    main()