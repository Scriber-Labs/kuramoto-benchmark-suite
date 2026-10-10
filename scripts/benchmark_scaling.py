
import numpy as np
import time
from kuramoto.solvers import RotorSolver
from tabulate import tabulate

def benchmark_scaling():
    print("🚀 Benchmarking Solver Scaling: Standard (O(N^2)) vs Vectorized GA (O(N))")
    
    # Parameters
    N_list = [50, 100, 200, 500]
    K = 1.5
    T_MAX = 2.0
    dt_internal = 0.005
    t_eval = np.linspace(0, T_MAX, 10) # Minimal evaluation points to focus on integration speed
    seed = 42
    
    results = []
    
    for N in N_list:
        print(f"  - Testing N={N}...")
        
        # 1. Standard (Pairwise)
        solver_std = RotorSolver(n_oscillators=N, dim=2, seed=seed)
        t0 = time.time()
        solver_std.simulate(K=K, t_eval=t_eval, dt_internal=dt_internal, method="standard")
        dur_std = time.time() - t0
        
        # 2. Vectorized GA (Mean-field)
        solver_vec = RotorSolver(n_oscillators=N, dim=2, seed=seed)
        t0 = time.time()
        solver_vec.simulate(K=K, t_eval=t_eval, dt_internal=dt_internal, method="vectorized_geometric")
        dur_vec = time.time() - t0
        
        speedup = dur_std / max(dur_vec, 1e-6)
        results.append([N, f"{dur_std:.4f}s", f"{dur_vec:.4f}s", f"{speedup:.1f}x"])
        
    print("\n📊 Scaling Results:")
    print(tabulate(results, headers=["N", "Standard (O(N^2))", "Vectorized GA (O(N))", "Speedup"], tablefmt="github"))

if __name__ == "__main__":
    benchmark_scaling()
