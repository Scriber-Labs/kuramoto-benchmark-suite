import numpy as np
from kuramoto.api import generate_kuramoto_dataset

N = 50
T = 1000
dt = 0.01

omega = np.random.normal(0.0, 1.0, size=N)

data = generate_kuramoto_dataset(
    n_oscillator=N,
    natural_frequencies=omega,
    coupling=5.0,
    timesteps=T,
    dt=dt,
    seed=27,
)

np.savez("data/examples/small_demo.npz", **data)
