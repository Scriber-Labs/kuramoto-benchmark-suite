import numpy as np
import os
from kuramoto.api import generate_kuramoto_dataset

N = 50
T = 1000
dt = 0.01

omega = np.random.normal(0.0, 1.0, size=N)

data = generate_kuramoto_dataset(
    n_oscillators=N,
    natural_frequencies=omega,
    coupling=5.0,
    timesteps=T,
    dt=dt,
    seed=27,
)

# Ensure the directory exists before saving
output_path = "data/examples/small_demo.npz"
os.makedirs(os.path.dirname(output_path), exist_ok=True)

np.savez(output_path, **data)
