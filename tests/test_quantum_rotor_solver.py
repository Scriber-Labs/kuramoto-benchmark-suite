import numpy as np

from kuramoto.order_parameter import compute_order_parameter
from kuramoto.solvers.quantum_rotor import QuantumRotorSolver, step_quantum_scf


def test_quantum_rotor_solver_initialization():
    """Verify solver initialization, defaults, and custom states."""
    solver = QuantumRotorSolver(n_oscillators=8, seed=42)
    assert solver.N == 8
    assert len(solver.phases) == 8
    assert len(solver.omegas) == 8
    assert np.all((solver.phases >= -np.pi) & (solver.phases <= np.pi))


def test_quantum_rotor_schemes_equivalence():
    """Verify that statevector and expectation schemes produce identical trajectories."""
    t_eval = np.linspace(0.0, 2.0, 20)
    seed = 123
    n_oscillators = 10
    K = 1.2

    solver1 = QuantumRotorSolver(n_oscillators=n_oscillators, seed=seed)
    _, traj1 = solver1.simulate(K=K, t_eval=t_eval, scheme="statevector")

    solver2 = QuantumRotorSolver(n_oscillators=n_oscillators, seed=seed)
    _, traj2 = solver2.simulate(K=K, t_eval=t_eval, scheme="expectation")

    assert np.allclose(traj1, traj2, atol=1e-5)


def test_quantum_rotor_order_parameter_bounds():
    """Verify order parameter r(t) bounds [0, 1] during quantum SCF simulation."""
    solver = QuantumRotorSolver(n_oscillators=15, seed=99)
    t_eval = np.linspace(0.0, 5.0, 30)
    _, traj = solver.simulate(K=2.0, t_eval=t_eval, scheme="statevector")

    r = compute_order_parameter(traj)
    assert r.shape == (30,)
    assert np.all((r >= 0.0) & (r <= 1.0 + 1e-6))


def test_quantum_rotor_shot_sampling_statistical_convergence():
    """Verify that shot_sampling approaches statevector as shot count increases."""
    phases = np.array([0.1, -0.4, 0.8, -1.2])
    omegas = np.array([0.5, 0.5, -0.5, -0.5])
    K = 1.0
    dt = 0.05

    exact_next = step_quantum_scf(phases, omegas, K=K, dt=dt, scheme="statevector")

    # High shot count should be close to exact
    sampled_next_high = step_quantum_scf(
        phases,
        omegas,
        K=K,
        dt=dt,
        scheme="shot_sampling",
        shots=100000,
        rng=np.random.default_rng(42),
    )
    assert np.allclose(exact_next, sampled_next_high, atol=0.03)


def test_quantum_rotor_qasm_generation():
    """Verify OpenQASM export from quantum solver instance."""
    solver = QuantumRotorSolver(n_oscillators=4, seed=42)
    qasm = solver.to_qasm(K=1.0, dt=0.01)

    assert "OPENQASM 2.0;" in qasm
    assert "qreg q[4];" in qasm
    assert "rz(" in qasm
