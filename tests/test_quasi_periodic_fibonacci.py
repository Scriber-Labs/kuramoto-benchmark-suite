from __future__ import annotations

import numpy as np
import pytest

from kuramoto.api import generate_fibonacci_frequencies, generate_kuramoto_dataset
from kuramoto.model import KuramotoModel
from kuramoto.solvers.rotor import (
    RotorSolver,
    fibonacci_word_symbol,
    step_quasi_periodic,
)


def test_generate_fibonacci_frequencies_properties():
    """Verify mathematical properties of Fibonacci frequency generation."""
    N = 8
    base_freq = 2.5
    freqs = generate_fibonacci_frequencies(N, base_frequency=base_freq, offset=1)

    assert freqs.ndim == 1
    assert freqs.shape == (N,)
    assert np.all(freqs > 0)

    # Expected Fibonacci numbers: F_1=1, F_2=1, F_3=2, F_4=3, F_5=5, F_6=8, F_7=13, F_8=21, F_9=34, F_10=55
    # Ratios F_{k+1}/F_k for offset=1:
    # k=1: 1/1 = 1.0 -> 2.5
    # k=2: 2/1 = 2.0 -> 5.0
    # k=3: 3/2 = 1.5 -> 3.75
    # k=4: 5/3 = 1.666... -> 4.1666...
    # k=5: 8/5 = 1.6 -> 4.0
    expected_ratios = np.array(
        [1.0, 2.0, 1.5, 5.0 / 3.0, 8.0 / 5.0, 13.0 / 8.0, 21.0 / 13.0, 34.0 / 21.0]
    )
    assert np.allclose(freqs, base_freq * expected_ratios)

    # Error handling
    with pytest.raises(ValueError, match="Number of oscillators N must be positive"):
        generate_fibonacci_frequencies(0)

    with pytest.raises(ValueError, match="Offset must be >= 1"):
        generate_fibonacci_frequencies(5, offset=0)


def test_fibonacci_word_sequence():
    """Verify Fibonacci word sequence generation via Beatty relation."""
    # Prefix of infinite Fibonacci word W_infinity
    expected_sequence = [0, 1, 0, 0, 1, 0, 1, 0, 0, 1, 0, 0, 1, 0, 1]
    computed_sequence = [
        fibonacci_word_symbol(i) for i in range(len(expected_sequence))
    ]
    assert computed_sequence == expected_sequence

    with pytest.raises(ValueError, match="Step index must be non-negative"):
        fibonacci_word_symbol(-1)


def test_quasi_periodic_rotor_norm_preservation_and_drift_reconstruction():
    """
    Verify quasi-periodic rotor evolution preserves Spin(2) norm
    and achieves machine-precision backward reconstruction drift.
    """
    N = 6
    dt = 0.005
    n_steps = 100

    # 1. Machine precision uncoupled backward reconstruction
    solver_uncoupled = RotorSolver(
        n_oscillators=N,
        dim=2,
        natural_frequencies=generate_fibonacci_frequencies(N, base_frequency=1.0),
        seed=101,
    )
    initial_uncoupled = solver_uncoupled._rotor_array.copy()

    for step_idx in range(n_steps):
        step_quasi_periodic(solver_uncoupled, K=0.0, dt=dt, step_index=step_idx)
        norms = np.sum(solver_uncoupled._rotor_array**2, axis=1)
        assert np.allclose(norms, 1.0, atol=1e-14)

    for step_idx in reversed(range(n_steps)):
        step_quasi_periodic(solver_uncoupled, K=0.0, dt=-dt, step_index=step_idx)
        norms = np.sum(solver_uncoupled._rotor_array**2, axis=1)
        assert np.allclose(norms, 1.0, atol=1e-14)

    reconstructed_uncoupled = solver_uncoupled._rotor_array.copy()
    drift_uncoupled = np.linalg.norm(initial_uncoupled - reconstructed_uncoupled)
    assert drift_uncoupled < 1e-12

    # 2. Coupled forward-backward trajectory norm conservation
    solver_coupled = RotorSolver(
        n_oscillators=N,
        dim=2,
        natural_frequencies=generate_fibonacci_frequencies(N, base_frequency=1.0),
        seed=101,
    )
    initial_coupled = solver_coupled._rotor_array.copy()

    for step_idx in range(n_steps):
        step_quasi_periodic(solver_coupled, K=1.2, dt=dt, step_index=step_idx)
        norms = np.sum(solver_coupled._rotor_array**2, axis=1)
        assert np.allclose(norms, 1.0, atol=1e-14)

    for step_idx in reversed(range(n_steps)):
        step_quasi_periodic(solver_coupled, K=1.2, dt=-dt, step_index=step_idx)
        norms = np.sum(solver_coupled._rotor_array**2, axis=1)
        assert np.allclose(norms, 1.0, atol=1e-14)

    reconstructed_coupled = solver_coupled._rotor_array.copy()
    drift_coupled = np.linalg.norm(initial_coupled - reconstructed_coupled)
    assert drift_coupled < 1e-3


def test_quasi_periodic_simulation_interface():
    """Verify simulation interface with quasi_periodic_step flag and solver method."""
    N = 5
    t_eval = np.linspace(0.0, 0.4, 9)

    # 1. Via RotorSolver.simulate(..., quasi_periodic_step=True)
    solver = RotorSolver(
        n_oscillators=N,
        dim=2,
        natural_frequencies=generate_fibonacci_frequencies(N),
        seed=42,
    )
    t_out, phases_flag = solver.simulate(
        K=1.5, t_eval=t_eval, dt_internal=0.01, quasi_periodic_step=True
    )
    assert phases_flag.shape == (9, N)
    assert np.allclose(t_out, t_eval)

    # 2. Via KuramotoModel with solver_type='quasi_periodic'
    model = KuramotoModel(
        n_oscillators=N,
        natural_frequencies=generate_fibonacci_frequencies(N),
        coupling_strength=1.5,
        solver_type="quasi_periodic",
        random_seed=42,
    )
    dataset = model.simulate(t_span=0.4, n_points=9)
    assert dataset.theta.shape == (9, N)
    assert np.all(np.isfinite(dataset.theta))

    # 3. Via generate_kuramoto_dataset API
    data_dict = generate_kuramoto_dataset(
        n_oscillators=N,
        natural_frequencies=generate_fibonacci_frequencies(N),
        coupling=1.5,
        timesteps=9,
        dt=0.05,
        solver="rotor",
        quasi_periodic_step=True,
        seed=42,
    )
    assert "theta" in data_dict
    assert data_dict["theta"].shape == (9, N)
