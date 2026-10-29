
import time
import json
import os
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Final, List, Dict, Any
from kuramoto.api import generate_kuramoto_dataset
from kuramoto.order_parameter import compute_order_parameter
from kuramoto.analysis.viz import set_style, SOLVER_COLORS, PROJECT_COLORS

# Constants
OUTPUT_DIR: Final[str] = "data/benchmark"
PLOTS_DIR: Final[str] = "plots/benchmarks"
N_LIST: Final[List[int]] = [50, 100, 200, 500]
DT_LIST: Final[List[float]] = [0.05, 0.01]
T_MAX: Final[float] = 2.0
SEED: Final[int] = 9

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(PLOTS_DIR, exist_ok=True)

def run_rigorous_benchmarks():
    set_style()
    print("🚀 Starting Rigorous Benchmarking Sweep...")
    
    results = {
        "metadata": {
            "T_MAX": T_MAX,
            "SEED": SEED,
            "N_LIST": N_LIST,
            "DT_LIST": DT_LIST
        },
        "runs": []
    }
    
    for n in N_LIST:
        # Generate common natural frequencies for this N
        rng = np.random.default_rng(SEED)
        omega = rng.normal(0.0, 1.0, n)
        
        for dt in DT_LIST:
            print(f"📊 Testing N={n}, dt={dt}...")
            timesteps = int(T_MAX / dt)
            
            # 1. RK45 Ground Truth
            start_rk45 = time.time()
            rk45_data = generate_kuramoto_dataset(
                n_oscillators=n,
                natural_frequencies=omega,
                coupling=1.5,
                timesteps=timesteps,
                dt=dt,
                solver="rk45",
                seed=SEED
            )
            time_rk45 = time.time() - start_rk45
            r_rk45 = compute_order_parameter(rk45_data["theta"])
            
            # 2. Vectorized GA Rotor
            start_ga = time.time()
            ga_data = generate_kuramoto_dataset(
                n_oscillators=n,
                natural_frequencies=omega,
                coupling=1.5,
                timesteps=timesteps,
                dt=dt,
                solver="rotor", # Note: KuramotoModel uses 'fast' (vectorized) by default for 'rotor'
                seed=SEED
            )
            time_ga = time.time() - start_ga
            r_ga = compute_order_parameter(ga_data["theta"])
            
            # Calculate RMSE Accuracy
            rmse = np.sqrt(np.mean((r_rk45 - r_ga)**2))
            
            run_info = {
                "N": n,
                "dt": dt,
                "time_rk45": time_rk45,
                "time_ga": time_ga,
                "rmse": float(rmse),
                "speedup": time_rk45 / time_ga if time_ga > 0 else 0
            }
            results["runs"].append(run_info)
            print(f"   - Speedup: {run_info['speedup']:.2f}x | RMSE: {run_info['rmse']:.2e}")

    # Save Results
    with open(f"{OUTPUT_DIR}/rigorous_results.json", "w") as f:
        json.dump(results, f, indent=2)
    print(f"✅ Results saved to {OUTPUT_DIR}/rigorous_results.json")
    
    # Generate Plots
    plot_results(results)

def plot_results(results):
    runs = results["runs"]
    n_list = results["metadata"]["N_LIST"]
    dt_list = results["metadata"]["DT_LIST"]
    
    # --- Scaling Plot ---
    plt.figure(figsize=(10, 6))
    for dt in dt_list:
        n_vals = [r["N"] for r in runs if r["dt"] == dt]
        t_ga = [r["time_ga"] for r in runs if r["dt"] == dt]
        t_rk45 = [r["time_rk45"] for r in runs if r["dt"] == dt]
        
        plt.loglog(n_vals, t_ga, 'o-', label=f"Vectorized GA (dt={dt})")
        plt.loglog(n_vals, t_rk45, 's--', alpha=0.5, label=f"RK45 (dt={dt})")
        
    plt.xlabel("Number of Oscillators (N)")
    plt.ylabel("Execution Time (s)")
    plt.title("Scaling Performance: Vectorized GA vs RK45")
    plt.legend()
    plt.grid(True, which="both", alpha=0.3)
    plt.savefig(f"{PLOTS_DIR}/scaling_performance.png")
    plt.close()
    
    # --- Accuracy Plot ---
    plt.figure(figsize=(10, 6))
    for dt in dt_list:
        n_vals = [r["N"] for r in runs if r["dt"] == dt]
        rmse_vals = [r["rmse"] for r in runs if r["dt"] == dt]
        plt.plot(n_vals, rmse_vals, 'o-', label=f"dt={dt}")
        
    plt.xlabel("Number of Oscillators (N)")
    plt.ylabel("Order Parameter RMSE (vs RK45)")
    plt.title("Numerical Stability & Accuracy vs Ground Truth")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.savefig(f"{PLOTS_DIR}/accuracy_rmse.png")
    plt.close()
    
    print(f"✅ Plots saved to {PLOTS_DIR}/")

if __name__ == "__main__":
    run_rigorous_benchmarks()
