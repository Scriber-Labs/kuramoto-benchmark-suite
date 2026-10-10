"""
validate_ga_rotor_metrics.py

Comprehensive validation script for the Geometric Algebra (GA) rotor solver.
Computes Hamiltonian invariants, U(1) symmetry invariance, and spectral benchmarks.

Author: Eigenscribe
Date: 10-2026
"""

from __future__ import annotations

import time
import os
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Final, Dict, Any

# Local kuramoto imports
from kuramoto.solvers.rotor import RotorSolver
from kuramoto.metrics.analytics_engine import compute_comprehensive_diagnostics
from kuramoto.order_parameter import compute_order_parameter

# -----------------------------------------------------------------------------------------------------------
# 🎭 Constants & Config
# -----------------------------------------------------------------------------------------------------------

OUTPUT_DIR: Final[str] = "plots/validation"
N_OSCILLATORS: Final[int] = 50
COUPLING: Final[float] = 1.5
T_MAX: Final[float] = 5.0
DT_INTERNAL: Final[float] = 0.001
SEED: Final[int] = 42

# Ensure output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

# -----------------------------------------------------------------------------------------------------------
# 1️⃣ Core Validation Logic
# -----------------------------------------------------------------------------------------------------------

def run_benchmarks() -> Dict[str, Any]:
    """Run side-by-side comparison of rotor integration methods."""
    print("🚀 Running benchmarks...")
    
    t_eval = np.linspace(0, T_MAX, int(T_MAX / 0.05) + 1)
    
    # Standard vs Fast vs Geometric vs Vectorized
    methods = ["standard", "fast", "geometric", "vectorized_geometric"]
    results = {}
    
    for method in methods:
        solver = RotorSolver(n_oscillators=N_OSCILLATORS, dim=2, seed=SEED)
        start_time = time.time()
        times, phases = solver.simulate(
            K=COUPLING, 
            t_eval=t_eval, 
            dt_internal=DT_INTERNAL,
            method=method
        )
        elapsed = time.time() - start_time
        
        results[method] = {
            "times": times,
            "phases": phases,
            "elapsed": elapsed,
            "order_param": compute_order_parameter(phases)
        }
        print(f"  - {method}: {elapsed:.3f}s")
        
    return results

def verify_u1_invariance() -> bool:
    """Verify that a global phase shift does not change synchronization dynamics."""
    print("🧪 Verifying U(1) invariance...")
    
    t_eval = np.linspace(0, 2.0, 41)
    shift = 0.73 * np.pi
    
    # 1. Original
    solver1 = RotorSolver(n_oscillators=N_OSCILLATORS, dim=2, seed=SEED)
    _, phases1 = solver1.simulate(K=COUPLING, t_eval=t_eval, dt_internal=DT_INTERNAL)
    r1 = compute_order_parameter(phases1)
    
    # 2. Shifted
    solver2 = RotorSolver(n_oscillators=N_OSCILLATORS, dim=2, seed=SEED)
    # Apply shift to initial rotors
    B = solver2.B_plane
    solver2.rotors = [r * np.exp(-B * shift / 2.0) for r in solver2.rotors]
    
    _, phases2 = solver2.simulate(K=COUPLING, t_eval=t_eval, dt_internal=DT_INTERNAL)
    r2 = compute_order_parameter(phases2)
    
    max_diff = np.max(np.abs(r1 - r2))
    is_invariant = max_diff < 1e-12
    print(f"  - Max |r| difference: {max_diff:.2e}")
    print(f"  - Result: {'PASSED' if is_invariant else 'FAILED'}")
    
    return is_invariant

def analyze_energy_drift(benchmark_results: Dict[str, Any]) -> None:
    """Compute and plot energy diagnostics from simulation history."""
    print("📊 Analyzing energy drift...")
    
    res = benchmark_results["geometric"]
    times = res["times"]
    phases = res["phases"]
    
    # Convert phases to complex rotors for analytics engine
    rotors = np.exp(1j * phases) 
    
    metrics = compute_comprehensive_diagnostics(
        rotor_history=rotors,
        times=times,
        K=COUPLING
    )
    
    # Plot Energy Trajectory
    plt.figure(figsize=(10, 6))
    plt.plot(times, metrics.energy_trajectory - metrics.energy_trajectory[0], label="Total Energy Drift")
    plt.xlabel("Time")
    plt.ylabel(r"$\Delta H$ (Relative to t=0)")
    plt.title(f"Hamiltonian Energy Drift (Geometric Solver, dt={DT_INTERNAL})")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.savefig(f"{OUTPUT_DIR}/energy_drift.png")
    plt.close()
    
    # Plot Phase-Space Contraction
    plt.figure(figsize=(10, 6))
    plt.plot(times, metrics.lambda_trajectory, color="red")
    plt.xlabel("Time")
    plt.ylabel(r"Contraction Rate $\lambda(t)$")
    plt.title("Phase-Space Volume Contraction Trajectory")
    plt.grid(True, alpha=0.3)
    plt.savefig(f"{OUTPUT_DIR}/contraction_rate.png")
    plt.close()
    
    # Plot Spectral PSD
    plt.figure(figsize=(10, 6))
    plt.semilogy(metrics.spectral_frequencies, metrics.spectral_psd_mean, label="Mean PSD", color="blue")
    plt.xlabel("Frequency (Hz)")
    plt.ylabel("Power Spectral Density")
    plt.title("Spectral Distribution of Oscillator Velocities")
    plt.grid(True, which="both", alpha=0.3)
    plt.savefig(f"{OUTPUT_DIR}/spectral_psd.png")
    plt.close()
    
    print(f"  - Total energy drift: {metrics.total_energy_drift:.2e}")
    print(f"  - Results saved to {OUTPUT_DIR}")

# -----------------------------------------------------------------------------------------------------------
# 2️⃣ Visualization
# -----------------------------------------------------------------------------------------------------------

def plot_comparison(results: Dict[str, Any]) -> None:
    """Plot synchronization comparison."""
    plt.figure(figsize=(12, 6))
    
    for method, data in results.items():
        ls = "-" if method == "geometric" else "--"
        plt.plot(data["times"], data["order_param"], label=f"{method} (r={np.mean(data['order_param']):.3f})", linestyle=ls)
        
    plt.xlabel("Time")
    plt.ylabel("Order Parameter |r|")
    plt.title("Solver Comparison: Synchronization Strength")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.savefig(f"{OUTPUT_DIR}/solver_comparison.png")
    plt.close()

# -----------------------------------------------------------------------------------------------------------
# 💨 Smoke tests
# -----------------------------------------------------------------------------------------------------------

def _run_smoke_test() -> None:
    """Quick sanity check."""
    print("💨 Running script smoke test...")
    results = run_benchmarks()
    assert "geometric" in results
    assert verify_u1_invariance()
    analyze_energy_drift(results)
    plot_comparison(results)
    print("✅ Smoke test passed.")

# -----------------------------------------------------------------------------------------------------------
# 🔥 Entry point
# -----------------------------------------------------------------------------------------------------------

def main() -> None:
    _run_smoke_test()

if __name__ == "__main__":
    main()
