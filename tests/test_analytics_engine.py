import numpy as np

from kuramoto.metrics.analytics_engine import (
    ComprehensiveMetrics,
    compute_comprehensive_diagnostics,
)


def test_compute_comprehensive_diagnostics_complex():
    times = np.linspace(0, 10, 200)
    theta = np.outer(times, np.array([1.0, 1.2, 0.8, 1.1]))
    rotors = np.cos(theta / 2.0) - 1j * np.sin(theta / 2.0)

    metrics = compute_comprehensive_diagnostics(
        rotor_history=rotors,
        times=times,
        K=1.5,
    )

    assert isinstance(metrics, ComprehensiveMetrics)
    assert metrics.energy_trajectory.shape == (200,)
    assert metrics.lambda_trajectory.shape == (200,)
    assert len(metrics.spectral_frequencies) > 0
    assert metrics.spectral_psd_mean.shape == metrics.spectral_frequencies.shape
    assert "fundamental" in metrics.energy_decomposition
    assert "harmonics" in metrics.energy_decomposition
    assert "rest" in metrics.energy_decomposition
    assert isinstance(metrics.total_energy_drift, float)


def test_compute_comprehensive_diagnostics_real_array():
    times = np.linspace(0, 10, 200)
    theta = np.outer(times, np.array([1.0, 1.2, 0.8]))
    scalars = np.cos(theta / 2.0)
    bivectors = np.sin(theta / 2.0)
    rotors_real = np.stack([scalars, bivectors], axis=-1)

    adj = np.array([[0.0, 1.0, 1.0], [1.0, 0.0, 0.0], [1.0, 0.0, 0.0]])

    metrics = compute_comprehensive_diagnostics(
        rotor_history=rotors_real,
        times=times,
        K=2.0,
        adjacency_in=adj,
        blade_idx=1,
    )

    assert metrics.energy_trajectory.shape == (200,)
    assert metrics.lambda_trajectory.shape == (200,)
    assert np.all(np.isfinite(metrics.energy_trajectory))
    assert np.all(np.isfinite(metrics.lambda_trajectory))
