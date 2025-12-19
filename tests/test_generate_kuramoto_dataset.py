import numpy as np
from kuramoto.api import generate_kuramoto_dataset

def test_determinsim():
    omega = np.ones(10)
    d1 = generate_kuramoto_dataset(10, omega, 1.0, 100, 0.01, seed=0)
    d2 = generate_kuramoto_dataset(10, omega, 1.0, 100, 0.01, seed=0)
    assert np.allclose(d1["theta"], d2["theta"])

def test_immutability():
    omega = np.ones(10)
    omega_copy = omega.copy()
    generate_kuramoto_dataset(10, omega, 1.0, 10, 0.01)
    assert np.allclose(omega, omega_copy)

def test_shapes():
    omega = np.ones(10)
    data = generate_kuramoto_dataset(5, omega, 1.0, 20, 0.1)
    assert data["theta"].shape == (20, 5)