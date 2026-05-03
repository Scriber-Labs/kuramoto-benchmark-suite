from typing import Optional, Dict, Any
import numpy as np

from .model import KuramotoModel

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
) -> Dict[str, Any]:

    t_span = timesteps * dt

    model = KuramotoModel(
        n_oscillators=n_oscillators,
        natural_frequencies=natural_frequencies,
        adjacency_matrix=adjacency,
        coupling_strength=coupling,
        noise_std=noise_std,
        random_seed=seed,
    )

    dataset = model.simulate(t_span=t_span)

    return dataset.to_dict()