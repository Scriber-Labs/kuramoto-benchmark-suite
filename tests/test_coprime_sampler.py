# tests/test_coprime_sampler.py
"""
Unit and integration tests for Coprime Time-Domain Sampler Wrapper and CRT reconstruction.

Verifies:
1. Extended Euclidean Algorithm (Extended GCD) and Bézout identity resolution.
2. Chinese Remainder Theorem (CRT) frequency index reconstruction across coprime moduli.
3. Vectorized and scalar multi-index frequency unwrapping.
4. CoprimeSamplerWrapper memory footprint reduction from O(MN) down to O(M + N).
5. Validation against gold-standard dense RotorSolver simulations.
6. Failure mode / structural rotor drift detection and sensitivity amplification.
"""

from __future__ import annotations

import numpy as np
import pytest

from kuramoto.solvers.coprime import (
    CoprimeSampleResult,
    CoprimeSamplerWrapper,
    coprime_reconstruct_frequency,
    detect_spectral_drift,
    extended_gcd,
)
from kuramoto.solvers.rotor import RotorSolver


def test_extended_gcd_bezout_identity():
    """Verify Extended GCD returns correct gcd and satisfies Bézout identity."""
    # Standard coprime pairs
    test_pairs = [(7, 11), (3, 5), (13, 17), (8, 15), (21, 20)]
    for m, n in test_pairs:
        g, a, b = extended_gcd(m, n)
        assert g == 1
        assert a * m + b * n == 1

    # Non-coprime pair
    g, a, b = extended_gcd(12, 18)
    assert g == 6
    assert a * 12 + b * 18 == 6

    # Error handling for (0, 0)
    with pytest.raises(ValueError, match="Extended GCD is undefined"):
        extended_gcd(0, 0)


def test_coprime_reconstruct_frequency_all_bins():
    """Verify exact CRT reconstruction for all integer bins within [0, M*N - 1]."""
    for M, N in [(7, 11), (3, 5), (5, 9), (13, 17)]:
        for true_k in range(M * N):
            k_m = true_k % M  # Sampler B alias
            k_n = true_k % N  # Sampler A alias
            reconstructed_k = coprime_reconstruct_frequency(k_m=k_m, k_n=k_n, M=M, N=N)
            assert (
                reconstructed_k == true_k
            ), f"Failed for M={M}, N={N}, true_k={true_k}: got {reconstructed_k}"


def test_coprime_reconstruct_frequency_vectorized():
    """Verify vectorized array inputs to coprime_reconstruct_frequency."""
    M, N = 7, 11
    true_ks = np.array([0, 1, 14, 27, 45, 60, 76])
    k_m = true_ks % M
    k_n = true_ks % N

    reconstructed_ks = coprime_reconstruct_frequency(k_m=k_m, k_n=k_n, M=M, N=N)
    np.testing.assert_array_equal(reconstructed_ks, true_ks)


def test_coprime_reconstruct_frequency_invalid_inputs():
    """Verify input validation for non-coprime or non-positive strides."""
    # Non-positive strides
    with pytest.raises(ValueError, match="must be positive"):
        coprime_reconstruct_frequency(1, 2, M=0, N=11)

    with pytest.raises(ValueError, match="must be positive"):
        coprime_reconstruct_frequency(1, 2, M=7, N=-5)

    # Non-coprime strides (gcd(6, 9) = 3)
    with pytest.raises(ValueError, match="not coprime"):
        coprime_reconstruct_frequency(1, 2, M=6, N=9)


def test_coprime_sampler_wrapper_decimation_and_shapes():
    """Verify CoprimeSamplerWrapper decimates trajectories and yields O(M+N) storage."""
    n_oscillators = 12
    omegas = np.linspace(0.8, 1.2, n_oscillators)
    M, N = 7, 11
    cycles = 2
    total_steps = cycles * (M * N)  # 2 * 77 = 154

    solver = RotorSolver(
        n_oscillators=n_oscillators,
        natural_frequencies=omegas,
        seed=101,
    )

    wrapper = CoprimeSamplerWrapper(solver=solver, M=M, N=N, record_phases=True)
    result = wrapper.simulate(K=1.2, dt=0.01, cycles=cycles, method="fast")

    assert isinstance(result, CoprimeSampleResult)
    assert result.M == M
    assert result.N == N
    assert result.total_steps == total_steps

    # Check sample counts: step 0 + step (k * stride)
    expected_len_a = (total_steps // N) + 1  # 154 // 11 + 1 = 15
    expected_len_b = (total_steps // M) + 1  # 154 // 7 + 1 = 23

    assert len(result.t_a) == expected_len_a
    assert len(result.order_parameter_a) == expected_len_a
    assert result.phases_a is not None
    assert result.phases_a.shape == (expected_len_a, n_oscillators)

    assert len(result.t_b) == expected_len_b
    assert len(result.order_parameter_b) == expected_len_b
    assert result.phases_b is not None
    assert result.phases_b.shape == (expected_len_b, n_oscillators)

    # Check storage reduction: dense would be 155 snapshots, stored is 15 + 23 = 38
    assert result.dense_snapshots == total_steps + 1
    assert result.total_snapshots == expected_len_a + expected_len_b
    assert result.compression_ratio < 0.26  # > 74% compression


def test_coprime_sampler_wrapper_no_phases():
    """Verify CoprimeSamplerWrapper memory savings when record_phases=False."""
    n_oscillators = 8
    omegas = np.ones(n_oscillators)
    solver = RotorSolver(
        n_oscillators=n_oscillators,
        natural_frequencies=omegas,
        seed=42,
    )

    wrapper = CoprimeSamplerWrapper(solver=solver, M=7, N=11, record_phases=False)
    result = wrapper.simulate(K=1.0, dt=0.01, cycles=1, method="fast")

    assert result.phases_a is None
    assert result.phases_b is None
    assert len(result.order_parameter_a) == (77 // 11) + 1
    assert len(result.order_parameter_b) == (77 // 7) + 1


def test_coprime_gold_standard_baseline_comparison():
    """Compare coprime sub-sampled trajectory against dense gold-standard simulation."""
    n_oscillators = 6
    omegas = np.array([0.9, 0.95, 1.0, 1.05, 1.1, 1.15])
    M, N = 7, 11
    dt = 0.01
    cycles = 2
    total_steps = cycles * (M * N)

    # 1. Run gold standard dense simulation
    solver_gold = RotorSolver(
        n_oscillators=n_oscillators,
        natural_frequencies=omegas.copy(),
        seed=777,
    )
    t_eval_dense = np.arange(total_steps + 1) * dt
    _, phases_dense = solver_gold.simulate(
        K=1.5,
        t_eval=t_eval_dense,
        dt_internal=dt,
        enforce_nyquist=False,
        method="fast",
    )
    op_dense = np.mean(np.exp(1j * phases_dense), axis=1)

    # 2. Run CoprimeSamplerWrapper simulation with identical initial conditions
    solver_coprime = RotorSolver(
        n_oscillators=n_oscillators,
        natural_frequencies=omegas.copy(),
        seed=777,
    )
    wrapper = CoprimeSamplerWrapper(solver=solver_coprime, M=M, N=N, record_phases=True)
    result = wrapper.simulate(K=1.5, dt=dt, total_steps=total_steps, method="fast")

    # Verify Sampler A snapshots match exact dense snapshots at indices k * N
    indices_a = np.arange(0, total_steps + 1, N)
    np.testing.assert_allclose(result.t_a, t_eval_dense[indices_a], rtol=1e-10)
    np.testing.assert_allclose(
        result.order_parameter_a, op_dense[indices_a], rtol=1e-8, atol=1e-8
    )

    # Verify Sampler B snapshots match exact dense snapshots at indices k * M
    indices_b = np.arange(0, total_steps + 1, M)
    np.testing.assert_allclose(result.t_b, t_eval_dense[indices_b], rtol=1e-10)
    np.testing.assert_allclose(
        result.order_parameter_b, op_dense[indices_b], rtol=1e-8, atol=1e-8
    )


def test_coprime_drift_amplification_diagnostic():
    """Verify detect_spectral_drift correctly identifies uncompensated rotor drift."""
    n_oscillators = 10
    omegas = np.linspace(0.8, 1.2, n_oscillators)

    # Case 1: Clean geometric integration without uncompensated drift
    solver_clean = RotorSolver(
        n_oscillators=n_oscillators,
        natural_frequencies=omegas.copy(),
        seed=42,
    )
    diag_clean = detect_spectral_drift(
        solver=solver_clean,
        K=1.0,
        dt=0.01,
        M=7,
        N=11,
        cycles=2,
        drift_perturbation=0.0,
    )
    assert diag_clean["crt_residual"] == 0.0
    assert not diag_clean["drift_detected"]

    # Case 2: Injected uncompensated phase drift
    solver_drifting = RotorSolver(
        n_oscillators=n_oscillators,
        natural_frequencies=omegas.copy(),
        seed=42,
    )
    diag_drifting = detect_spectral_drift(
        solver=solver_drifting,
        K=1.0,
        dt=0.01,
        M=7,
        N=11,
        cycles=2,
        drift_perturbation=5.0,  # strong perturbation
    )
    assert diag_drifting["drift_detected"]
