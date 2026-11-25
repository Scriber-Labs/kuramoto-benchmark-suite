#!/usr/bin/env python3
"""
Benchmark: quasi_periodic_step vs rkmk4 in RotorSolver.

Compares the Fibonacci-word Strang splitting integrator against the 4th-order
Lie group Runge-Kutta (RKMK4) method on:
1. Numerical drift (manifold preservation over long integrations)
2. Computational speed (wall time per step)
3. Accuracy (order parameter trajectory divergence)
4. Coprime spectral drift detection sensitivity

Usage:
    python scripts/compare_quasi_vs_rkmk4.py
"""

from __future__ import annotations

import time
import numpy as np

from kuramoto.solvers.rotor import RotorSolver
from kuramoto.solvers.coprime import CoprimeSamplerWrapper, detect_spectral_drift


# ---------------------------------------------------------------------------- #
# Benchmark configuration
# ---------------------------------------------------------------------------- #

N_OSCILLATORS = 32
COUPLING = 2.0
DT = 0.01
T_MAX = 100.0  # Long integration to reveal drift
SEED = 42
COPRIME_M = 7
COPRIME_N = 11


def benchmark_speed(method: str, n_runs: int = 5) -> dict:
    """Measure wall time for each method."""
    t_eval = np.linspace(0.0, T_MAX, 100)
    
    times = []
    for _ in range(n_runs):
        solver = RotorSolver(
            n_oscillators=N_OSCILLATORS,
            seed=SEED,
        )
        start = time.perf_counter()
        solver.simulate(K=COUPLING, t_eval=t_eval, dt_internal=DT, method=method)
        elapsed = time.perf_counter() - start
        times.append(elapsed)
    
    return {
        "mean_time": float(np.mean(times)),
        "std_time": float(np.std(times)),
        "min_time": float(np.min(times)),
    }


def benchmark_drift(method: str) -> dict:
    """
    Measure manifold drift: how much the rotor norm deviates from 1.0 over time.
    
    For a proper rotor in Cl(2,0), the norm should be exactly 1.0 (cos^2 + sin^2 = 1).
    Numerical drift causes this to deviate.
    """
    t_eval = np.linspace(0.0, T_MAX, 500)
    
    solver = RotorSolver(
        n_oscillators=N_OSCILLATORS,
        seed=SEED,
    )
    _, phases = solver.simulate(K=COUPLING, t_eval=t_eval, dt_internal=DT, method=method)
    
    # Check rotor norms at each output point
    solver._sync_array_from_rotors()
    rotor_array = solver._rotor_array  # Shape: (N, 2) for dim=2 [cos(theta/2), sin(theta/2)]
    
    # For dim=2, rotor norm is cos^2 + sin^2
    norms = np.sqrt(np.sum(rotor_array**2, axis=1))
    
    return {
        "mean_norm_deviation": float(np.mean(np.abs(norms - 1.0))),
        "max_norm_deviation": float(np.max(np.abs(norms - 1.0))),
        "final_phases_std": float(np.std(phases[-1] - phases[0])),
    }


def benchmark_order_parameter(method: str) -> np.ndarray:
    """Run simulation and return order parameter trajectory."""
    t_eval = np.linspace(0.0, T_MAX, 500)
    
    solver = RotorSolver(
        n_oscillators=N_OSCILLATORS,
        seed=SEED,
    )
    _, phases = solver.simulate(K=COUPLING, t_eval=t_eval, dt_internal=DT, method=method)
    
    # Compute order parameter at each time step
    order_params = np.array([np.abs(np.mean(np.exp(1j * phases[t]))) for t in range(len(phases))])
    return order_params


def benchmark_coprime_drift(method: str) -> dict:
    """Use coprime sampler to detect spectral drift."""
    solver = RotorSolver(
        n_oscillators=N_OSCILLATORS,
        seed=SEED,
    )
    wrapper = CoprimeSamplerWrapper(
        solver=solver,
        M=COPRIME_M,
        N=COPRIME_N,
        record_phases=False,
    )
    
    # CoprimeSamplerWrapper doesn't support "quasi_periodic" directly.
    # Map to the underlying stepper method it recognizes.
    coprime_method = "fast" if method == "quasi_periodic" else method
    
    # For quasi_periodic, we use a custom stepper that calls step_quasi_periodic
    custom_stepper = None
    if method == "quasi_periodic":
        step_counter = [0]  # Mutable counter for closure
        def custom_stepper_fn(K: float, dt: float) -> None:
            solver.step_quasi_periodic(K, dt, step_index=step_counter[0])
            step_counter[0] += 1
        custom_stepper = custom_stepper_fn
        coprime_method = "fast"  # Ignored when custom_stepper is provided
    
    result = wrapper.simulate(
        K=COUPLING,
        dt=DT,
        cycles=3,  # 3 full coprime cycles
        method=coprime_method,
        custom_stepper=custom_stepper,
    )
    
    # Compare order parameters from both channels at overlapping points
    # (only at t=0 and t=M*N*dt for coprime M, N)
    op_m = result.order_parameter_m
    op_n = result.order_parameter_n

    # Compute mean order parameter from each channel
    mean_r_m = float(np.mean(np.abs(op_m)))
    mean_r_n = float(np.mean(np.abs(op_n)))

    return {
        "mean_r_channel_m": mean_r_m,
        "mean_r_channel_n": mean_r_n,
        "channel_discrepancy": abs(mean_r_m - mean_r_n),
        "compression_ratio": result.compression_ratio,
        "total_snapshots": result.total_snapshots,
        "dense_snapshots": result.dense_snapshots,
    }


def print_separator(char: str = "─", width: int = 70) -> None:
    print(char * width)


def main() -> None:
    """Run all benchmarks and print comparison."""
    
    methods = ["quasi_periodic", "rkmk4"]
    method_labels = {
        "quasi_periodic": "Quasi-Periodic (Fibonacci Strang)",
        "rkmk4": "RKMK4 (Lie Group RK4)",
    }
    
    print("\n" + "=" * 70)
    print("  ROTOR SOLVER BENCHMARK: quasi_periodic vs rkmk4")
    print("=" * 70)
    print(f"  Oscillators: {N_OSCILLATORS}")
    print(f"  Coupling K:  {COUPLING}")
    print(f"  Time step:   {DT}")
    print(f"  T_max:       {T_MAX}")
    print(f"  Seed:        {SEED}")
    print("=" * 70 + "\n")
    
    # 1. Speed benchmark
    print("\n📊 SPEED BENCHMARK")
    print_separator()
    speed_results = {}
    for method in methods:
        result = benchmark_speed(method)
        speed_results[method] = result
        print(f"\n  {method_labels[method]}:")
        print(f"    Mean time:  {result['mean_time']:.4f}s ± {result['std_time']:.4f}s")
        print(f"    Min time:   {result['min_time']:.4f}s")
    
    # Speed ratio
    quasi_time = speed_results["quasi_periodic"]["mean_time"]
    rkmk4_time = speed_results["rkmk4"]["mean_time"]
    ratio = rkmk4_time / quasi_time if quasi_time > 0 else float('inf')
    print(f"\n  Speed ratio (RKMK4 / Quasi): {ratio:.2f}x")
    if ratio > 1:
        print(f"  → Quasi-periodic is {ratio:.1f}x faster")
    else:
        print(f"  → RKMK4 is {1/ratio:.1f}x faster")
    
    # 2. Drift benchmark
    print("\n\n📐 MANIFOLD DRIFT BENCHMARK")
    print_separator()
    for method in methods:
        result = benchmark_drift(method)
        print(f"\n  {method_labels[method]}:")
        print(f"    Mean norm deviation:  {result['mean_norm_deviation']:.2e}")
        print(f"    Max norm deviation:   {result['max_norm_deviation']:.2e}")
    
    # 3. Order parameter comparison
    print("\n\n📈 ORDER PARAMETER TRAJECTORY")
    print_separator()
    op_quasi = benchmark_order_parameter("quasi_periodic")
    op_rkmk4 = benchmark_order_parameter("rkmk4")
    
    print(f"\n  Final order parameter:")
    print(f"    Quasi-periodic: {op_quasi[-1]:.6f}")
    print(f"    RKMK4:          {op_rkmk4[-1]:.6f}")
    print(f"    Difference:     {abs(op_quasi[-1] - op_rkmk4[-1]):.2e}")
    
    print(f"\n  Mean order parameter:")
    print(f"    Quasi-periodic: {np.mean(op_quasi):.6f}")
    print(f"    RKMK4:          {np.mean(op_rkmk4):.6f}")
    
    # Trajectory divergence
    divergence = np.sqrt(np.mean((op_quasi - op_rkmk4)**2))
    print(f"\n  RMS trajectory divergence: {divergence:.2e}")
    
    # 4. Coprime spectral drift
    print("\n\n🔍 COPRIME SPECTRAL DRIFT DETECTION")
    print_separator()
    for method in methods:
        result = benchmark_coprime_drift(method)
        print(f"\n  {method_labels[method]}:")
        print(f"    Mean R (Channel M): {result['mean_r_channel_m']:.6f}")
        print(f"    Mean R (Channel N): {result['mean_r_channel_n']:.6f}")
        print(f"    Channel discrepancy: {result['channel_discrepancy']:.2e}")
        print(f"    Compression ratio:   {result['compression_ratio']:.2%}")
        print(f"    Snapshots saved:     {result['total_snapshots']} / {result['dense_snapshots']}")
    
    # Summary
    print("\n\n" + "=" * 70)
    print("  SUMMARY")
    print("=" * 70)
    
    quasi_drift = benchmark_drift("quasi_periodic")
    rkmk4_drift = benchmark_drift("rkmk4")
    
    print(f"\n  Manifold preservation:")
    print(f"    Quasi-periodic: {quasi_drift['max_norm_deviation']:.2e} max deviation")
    print(f"    RKMK4:          {rkmk4_drift['max_norm_deviation']:.2e} max deviation")
    
    if rkmk4_drift['max_norm_deviation'] < quasi_drift['max_norm_deviation']:
        improvement = quasi_drift['max_norm_deviation'] / rkmk4_drift['max_norm_deviation'] if rkmk4_drift['max_norm_deviation'] > 0 else float('inf')
        print(f"    → RKMK4 preserves manifold {improvement:.1f}x better")
    else:
        improvement = rkmk4_drift['max_norm_deviation'] / quasi_drift['max_norm_deviation'] if quasi_drift['max_norm_deviation'] > 0 else float('inf')
        print(f"    → Quasi-periodic preserves manifold {improvement:.1f}x better")
    
    print(f"\n  Computational cost:")
    print(f"    Quasi-periodic: {quasi_time:.4f}s")
    print(f"    RKMK4:          {rkmk4_time:.4f}s")
    
    print(f"\n  Verdict:")
    if rkmk4_time / quasi_time > 2:
        print("    Quasi-periodic is significantly faster but may have more drift.")
        print("    Use RKMK4 when accuracy matters; use quasi-periodic for speed.")
    elif quasi_drift['max_norm_deviation'] > rkmk4_drift['max_norm_deviation'] * 10:
        print("    RKMK4 has significantly better manifold preservation.")
        print("    Use RKMK4 for long integrations; quasi-periodic for short runs.")
    else:
        print("    Both methods perform similarly. Choice depends on specific needs.")
    
    print("\n")


if __name__ == "__main__":
    main()
