
import numpy as np
import matplotlib.pyplot as plt
from kuramoto.solvers import RotorSolver
from kuramoto.analysis.viz import set_style, PROJECT_COLORS

def viz_3d_sync():
    set_style()
    print("🎨 Generating 3D Spherical Synchronization Visualization...")
    
    N = 100
    K = 3.0
    T_MAX = 5.0
    dt = 0.05
    steps = int(T_MAX / dt)
    
    solver = RotorSolver(n_oscillators=N, dim=3, seed=42)
    
    # Setup Figure
    fig = plt.figure(figsize=(12, 5))
    ax1 = fig.add_subplot(121, projection='3d')
    ax2 = fig.add_subplot(122, projection='3d')
    
    def get_points(solver):
        e1 = solver.layout.basis_vectors["e1"]
        pts = np.array([(r * e1 * r.conjugate()).value[1:4] for r in solver.rotors])
        return pts

    # Initial State
    pts_start = get_points(solver)
    ax1.scatter(pts_start[:, 0], pts_start[:, 1], pts_start[:, 2], color=PROJECT_COLORS['cyan_light'], alpha=0.6)
    ax1.set_title("Initial State (Random on S^2)")
    
    # Run Simulation
    for _ in range(steps):
        solver.step_euler_vectorized_geometric(K=K, dt=dt)
        
    # Final State
    pts_end = get_points(solver)
    ax2.scatter(pts_end[:, 0], pts_end[:, 1], pts_end[:, 2], color=PROJECT_COLORS['purple_light'], alpha=0.8)
    ax2.set_title(f"Final State (Synchronized, K={K})")
    
    # Draw Sphere for reference
    u, v = np.mgrid[0:2*np.pi:20j, 0:np.pi:10j]
    x = np.cos(u)*np.sin(v)
    y = np.sin(u)*np.sin(v)
    z = np.cos(v)
    for ax in [ax1, ax2]:
        ax.plot_wireframe(x, y, z, color="white", alpha=0.05)
        ax.set_axis_off()
        ax.set_xlim([-1.1, 1.1])
        ax.set_ylim([-1.1, 1.1])
        ax.set_zlim([-1.1, 1.1])

    plt.tight_layout()
    plt.savefig("plots/3d_sync_demo.png", dpi=150)
    print("✅ Visualization saved to plots/3d_sync_demo.png")

if __name__ == "__main__":
    viz_3d_sync()
