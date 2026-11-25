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
    g, a, b = extended_gcd(7, 11)
    assert (g, a, b) == (1, -3, 2)
    assert (3 * b * 11 + 5 * a * 7) % 77 == 38

    for M, N in [(7, 11), (3, 5), (5, 9), (13, 17)]:
        for true_k in range(M * N):
            k_m = true_k % M  # Channel N FFT alias
            k_n = true_k % N  # Channel M FFT alias
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
    expected_len_m = (total_steps // M) + 1  # 154 // 7 + 1 = 23
    expected_len_n = (total_steps // N) + 1  # 154 // 11 + 1 = 15

    assert len(result.t_m) == expected_len_m
    assert len(result.order_parameter_m) == expected_len_m
    assert result.phases_m is not None
    assert result.phases_m.shape == (expected_len_m, n_oscillators)

    assert len(result.t_n) == expected_len_n
    assert len(result.order_parameter_n) == expected_len_n
    assert result.phases_n is not None
    assert result.phases_n.shape == (expected_len_n, n_oscillators)

    # Check storage reduction: dense would be 155 snapshots, stored is 15 + 23 = 38
    assert result.dense_snapshots == total_steps + 1
    assert result.total_snapshots == expected_len_m + expected_len_n
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

    assert result.phases_m is None
    assert result.phases_n is None
    assert len(result.order_parameter_m) == (77 // 7) + 1
    assert len(result.order_parameter_n) == (77 // 11) + 1


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

    # Verify Channel M snapshots match exact dense snapshots at indices k * M
    indices_m = np.arange(0, total_steps + 1, M)
    np.testing.assert_allclose(result.t_m, t_eval_dense[indices_m], rtol=1e-10)
    np.testing.assert_allclose(
        result.order_parameter_m, op_dense[indices_m], rtol=1e-8, atol=1e-8
    )

    # Verify Channel N snapshots match exact dense snapshots at indices k * N
    indices_n = np.arange(0, total_steps + 1, N)
    np.testing.assert_allclose(result.t_n, t_eval_dense[indices_n], rtol=1e-10)
    np.testing.assert_allclose(
        result.order_parameter_n, op_dense[indices_n], rtol=1e-8, atol=1e-8
    )


def test_coprime_drift_amplification_diagnostic():
    """Verify the diagnostic reports whether an explicit drift was injected."""
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


@pytest.mark.parametrize(
    ("M", "N", "cycles"),
    [(7, 11, 1), (7, 11, 2), (11, 7, 3)],
)
def test_spectral_drift_diagnostic_uses_crossed_channel_aliases(
    monkeypatch, M, N, cycles
):
    """Recover crossed residues from coherent tones over whole coprime periods."""
    k_true = 38
    total_steps = cycles * M * N
    sample_steps_m = np.arange(0, total_steps + 1, M)
    sample_steps_n = np.arange(0, total_steps + 1, N)
    order_parameter_m = np.exp(2j * np.pi * k_true * sample_steps_m / (M * N))
    order_parameter_n = np.exp(2j * np.pi * k_true * sample_steps_n / (M * N))
    sample_result = CoprimeSampleResult(
        t_m=sample_steps_m.astype(np.float64) * 0.01,
        order_parameter_m=order_parameter_m,
        t_n=sample_steps_n.astype(np.float64) * 0.01,
        order_parameter_n=order_parameter_n,
        M=M,
        N=N,
        dt=0.01,
        total_steps=total_steps,
    )

    def fake_simulate(self, **kwargs):
        return sample_result

    monkeypatch.setattr(CoprimeSamplerWrapper, "simulate", fake_simulate)

    diagnostics = detect_spectral_drift(
        solver=object(), K=1.0, dt=0.01, M=M, N=N, cycles=cycles
    )

    assert diagnostics["peak_alias_m"] == k_true % M
    assert diagnostics["peak_alias_n"] == k_true % N
    assert diagnostics["reconstructed_peak_index"] == k_true
    assert diagnostics["crt_residual"] == 0.0
