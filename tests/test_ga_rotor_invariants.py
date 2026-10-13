import numpy as np

from kuramoto.order_parameter import compute_order_parameter
from kuramoto.solvers.rotor import RotorSolver


def test_rotor_u1_invariance():
    """Verify global phase shift invariance in RotorSolver."""
    N = 10
    K = 1.0
    t_eval = np.linspace(0, 1.0, 11)
    dt = 0.01
    seed = 42

    # 1. Base simulation
    solver1 = RotorSolver(n_oscillators=N, seed=seed)
    _, phases1 = solver1.simulate(K=K, t_eval=t_eval, dt_internal=dt)
    r1 = compute_order_parameter(phases1)

    # 2. Shifted simulation
    solver2 = RotorSolver(n_oscillators=N, seed=seed)
    shift = 0.5 * np.pi
    B = solver2.B_plane
    # Shift initial state
    solver2.rotors = [r * np.exp(-B * shift / 2.0) for r in solver2.rotors]

    _, phases2 = solver2.simulate(K=K, t_eval=t_eval, dt_internal=dt)
    r2 = compute_order_parameter(phases2)

    # Order parameter magnitude should be invariant
    assert np.allclose(r1, r2, atol=1e-12)


def test_rotor_method_consistency():
    """Verify that 'fast', 'standard', and 'geometric' methods yield identical results."""
    N = 10
    K = 1.5
    t_eval = np.linspace(0, 0.5, 6)
    dt = 0.005
    seed = 123

    # Use 'fast' as reference
    solver_ref = RotorSolver(n_oscillators=N, seed=seed)
    _, phases_ref = solver_ref.simulate(
        K=K, t_eval=t_eval, dt_internal=dt, method="fast"
    )

    for method in ["standard", "geometric"]:
        solver = RotorSolver(n_oscillators=N, seed=seed)
        _, phases = solver.simulate(K=K, t_eval=t_eval, dt_internal=dt, method=method)
        assert np.allclose(phases_ref, phases, atol=1e-10)


def test_rotor_norm_preservation():
    """Verify that rotors remain normalized (magnitude 1) during evolution."""
    N = 5
    solver = RotorSolver(n_oscillators=N, seed=7)

    # Initial norms
    for r in solver.rotors:
        assert np.isclose(abs(r), 1.0, atol=1e-15)

    # Evolve
    solver.simulate(K=2.0, t_eval=np.linspace(0, 1.0, 5), dt_internal=0.01)

    # Final norms
    for r in solver.rotors:
        assert np.isclose(abs(r), 1.0, atol=1e-12)
